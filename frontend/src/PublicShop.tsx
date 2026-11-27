import { useEffect, useRef, useState } from "react";
import {
  Api,
  Config,
  Facts,
  dollarsToCents,
  money,
  vehicleName,
} from "./domain";

type Vehicle = {
  id: string;
  revision: number;
  facts: Facts;
  description: string;
};
type PublishedQuestion = {
  id: string;
  question: string;
  status: "approved" | "staff";
  answer: string;
  source_note: string;
};
type Preferences = {
  budget_cents: number | null;
  budget_kind: string;
  min_seats: number | null;
  max_mileage: number | null;
  body_style: string;
  fuel_type: string;
  drivetrain: string;
  priorities: string[];
  required_features: string[];
};
const defaults: Preferences = {
  budget_cents: null,
  budget_kind: "unknown",
  min_seats: null,
  max_mileage: null,
  body_style: "any",
  fuel_type: "any",
  drivetrain: "any",
  priorities: [],
  required_features: [],
};
const fields: [keyof Facts, string][] = [
  ["price", "Vehicle price"],
  ["mileage", "Mileage"],
  ["year", "Model year"],
  ["body_style", "Body style"],
  ["fuel_type", "Fuel type"],
  ["drivetrain", "Drivetrain"],
  ["transmission", "Transmission"],
  ["seats", "Seats"],
  ["mpg_combined", "Combined MPG (documented)"],
  ["cargo_cubic_feet", "Cargo space (cu ft)"],
  ["features", "Documented features"],
  ["availability", "Availability"],
];
function fact(f: Facts, key: keyof Facts) {
  const v = f[key];
  return v === null || v === undefined || (Array.isArray(v) && !v.length)
    ? "Not provided"
    : key === "price"
      ? money(Number(v))
      : Array.isArray(v)
        ? v.join(", ")
        : key === "year"
          ? String(v)
          : typeof v === "number"
            ? v.toLocaleString()
            : String(v).replaceAll("_", " ").toUpperCase();
}
type Source = { id: string; label: string; text: string; listing_id?: string; reference?: string };
type Message = {
  question: string;
  answer: string;
  follow_up?: string;
  sources: Source[];
  partial: boolean;
};
type ChatError = { question: string; detail: string; requestId?: string };

export default function PublicShop({
  id,
  api,
  config,
}: {
  id: string;
  api: Api;
  config: Config;
}) {
  const [data, setData] = useState<{
      name: string;
      listings: Vehicle[];
      knowledge: PublishedQuestion[];
    } | null>(null),
    [tab, setTab] = useState(() => {
      const view = new URLSearchParams(window.location.search).get("view");
      if (view === "chat" || view === "fit") return "AI chat";
      if (view === "questions") return "FAQs";
      return "Inventory";
    }),
    [error, setError] = useState(""),
    [notice, setNotice] = useState("");
  const [selected, setSelected] = useState<string[]>([]),
    [preferences, setPreferences] = useState<Preferences>(defaults),
    [budget, setBudget] = useState(""),
    [featuresText, setFeaturesText] = useState(""),
    [question, setQuestion] = useState(""),
    [messages, setMessages] = useState<Message[]>([]);
  const [pendingQuestion, setPendingQuestion] = useState("");
  const [chatError, setChatError] = useState<ChatError | null>(null);
  const [busy, setBusy] = useState(false),
    [aiBusy, setAiBusy] = useState(false),
    [comparison, setComparison] = useState<any>(null),
    [recommended, setRecommended] = useState<string[]>([]),
    [matches, setMatches] = useState<string[] | null>(null);
  const [preferencesOpen, setPreferencesOpen] = useState(false);
  const [contact, setContact] = useState(""),
    [summary, setSummary] = useState(""),
    [consent, setConsent] = useState(false),
    [showFollowup, setShowFollowup] = useState(false);
  const lock = useRef(false),
    requestKey = useRef(crypto.randomUUID()),
    chatEnd = useRef<HTMLDivElement>(null);
  const ai = config.questionMode === "ai" && !!config.shoppingAiEnabled;
  useEffect(() => {
    api("/shop/" + id)
      .then(setData)
      .catch((e) => setError(e.message));
  }, [id]);
  useEffect(() => {
    const container = chatEnd.current?.parentElement;
    if (container) container.scrollTop = container.scrollHeight;
  }, [messages, aiBusy, chatError]);
  useEffect(() => {
    const resize = () => setPreferencesOpen(tab === "AI chat" && window.innerWidth > 960);
    resize();
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, [tab]);
  async function work(fn: () => Promise<void>, isAi = false) {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setAiBusy(isAi);
    setError("");
    setNotice("");
    try {
      await fn();
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Unable to complete the request.",
      );
    } finally {
      lock.current = false;
      setBusy(false);
      setAiBusy(false);
    }
  }
  function choose(lid: string) {
    setSelected((ids) =>
      ids.includes(lid)
        ? ids.filter((i) => i !== lid)
        : ids.length < 3
          ? [...ids, lid]
          : ids,
    );
    setComparison(null);
  }
  function updatePrefs(p: Partial<Preferences>) {
    setPreferences((v) => ({ ...v, ...p }));
    setRecommended([]);
    setMatches(null);
    setComparison(null);
  }
  function currentPrefs() {
    const next = {
      ...preferences,
      budget_cents: budget.trim() ? dollarsToCents(budget) : null,
      required_features: featuresText
        .split(",")
        .map((v) => v.trim())
        .filter(Boolean),
    };
    return next;
  }
  function showComparison(result: any) {
    setComparison(result);
    if (result) {
      setData((previous) => previous && ({...previous, listings: previous.listings.map((listing) =>
        result.listings.find((car: Vehicle) => car.id === listing.id) ?? listing,
      )}));
    }
  }
  async function compare() {
    await work(async () => {
      const updated = currentPrefs();
      setPreferences(updated);
      const r = await api("/shop/" + id + "/compare", "POST", {
        listing_ids: selected,
        preferences: updated,
      });
      showComparison(r);
      setTab("Compare");
    });
  }
  async function ask(text = question) {
    const message = text.trim();
    if (!message || !ai || lock.current) return;
    setTab("AI chat");
    await work(async () => {
      setPendingQuestion(message);
      setChatError(null);
      try {
        const history = messages.slice(-4).flatMap((turn) => [
          { role: "user", content: turn.question },
          { role: "assistant", content: (turn.answer + " " + (turn.follow_up || "")).slice(0, 1600) },
        ]);
        const reply = await api("/shop/" + id + "/assist", "POST", {
          message,
          preferences: currentPrefs(),
          history,
          selected_ids: selected,
        });
        setMessages((existing) => [...existing, {
          question: message, answer: reply.answer, follow_up: reply.follow_up,
          sources: reply.sources, partial: reply.answer_mode === "partial_ai_explanation",
        }]);
        setPreferences(reply.preferences);
        setFeaturesText(reply.preferences.required_features.join(", "));
        setBudget(reply.preferences.budget_cents === null ? "" : String(reply.preferences.budget_cents / 100));
        setRecommended(reply.recommended_ids);
        setMatches(reply.matches);
        showComparison(reply.comparison ?? null);
        setQuestion("");
      } catch (e) {
        const err = e instanceof Error ? e as Error & { requestId?: string } : null;
        setChatError({ question: message, detail: err?.message || "The message could not be sent.", requestId: err?.requestId });
        setQuestion(message);
      } finally {
        setPendingQuestion("");
      }
    }, true);
  }
  function newChat() {
    setMessages([]);
    setChatError(null);
    setQuestion("");
    setPreferences(defaults);
    setBudget("");
    setFeaturesText("");
    setRecommended([]);
    setMatches(null);
    setComparison(null);
  }
  function prepareFollowup() {
    setShowFollowup(true);
    setConsent(false);
    requestKey.current = crypto.randomUUID();
    setSummary(
      messages.length
        ? messages[messages.length - 1].question
        : "Please help me choose between the selected vehicles.",
    );
  }
  if (!data)
    return <p role="status">{error || "Loading published inventory…"}</p>;
  const chosen = data.listings.filter((l) => selected.includes(l.id));
  return (
    <div className="shop" data-view={tab}>
      <div className="shop-heading">
        <h1>{data.name}</h1>
        {tab !== "AI chat" && <button className="primary" onClick={() => setTab("AI chat")}>Ask AI</button>}
      </div>
      <nav className="shop-nav" aria-label="Shopping sections">
        {["Inventory", "Compare", "AI chat", "FAQs"].map((t) => (
          <button
            key={t}
            aria-current={tab === t ? "page" : undefined}
            className={tab === t ? "active" : ""}
            onClick={() => {
              setTab(t);
              if (t === "Compare" && selected.length >= 2 && !comparison) void compare();
            }}
          >
            {t}
            {t === "Compare" && selected.length > 0 && (
              <span className="count">{selected.length}</span>
            )}
          </button>
        ))}
      </nav>
      {selected.length > 0 && tab !== "FAQs" && (
        <div className="selection-tray" aria-label="Selected vehicles">
          <span><strong>Selected:</strong> {chosen.map((car) => car.facts.model).join(", ")}</span>
          <div className="actions">
            {tab === "Inventory" && <button className="primary" disabled={busy || selected.length < 2} onClick={compare}>Compare selected ({selected.length})</button>}
            {tab === "Inventory" && <button onClick={() => setTab("AI chat")}>Ask about selection</button>}
            <button disabled={busy} onClick={() => { setSelected([]); setComparison(null); }}>Clear selection</button>
          </div>
        </div>
      )}
      {error && (
        <p role="alert" className="notice error-notice">
          {error}
        </p>
      )}
      {notice && (
        <p role="status" className="notice success">
          {notice}
        </p>
      )}
      <div className={"shop-layout" + (tab === "AI chat" ? " fit-layout" : "")}>
        <aside className="preference-panel" hidden={tab !== "AI chat" && tab !== "Compare"}>
          <details
            open={preferencesOpen}
            onToggle={(e) => setPreferencesOpen(e.currentTarget.open)}
          >
            <summary className="preference-summary">
              <strong>Your preferences</strong>
            </summary>
            <fieldset className="preference-fields" disabled={busy}>
              <p className="muted">
                Chat can fill these in. You can also change them yourself.
              </p>
              <label>
                Maximum budget (USD)
                <input
                  inputMode="decimal"
                  value={budget}
                  placeholder="For example: 25000"
                  onChange={(e) => setBudget(e.target.value)}
                  onBlur={() => {
                    try {
                      updatePrefs({
                        budget_cents: budget.trim()
                          ? dollarsToCents(budget)
                          : null,
                      });
                    } catch (e) {
                      setError((e as Error).message);
                    }
                  }}
                />
              </label>
              <label>
                Budget includes
                <select
                  value={preferences.budget_kind}
                  onChange={(e) => updatePrefs({ budget_kind: e.target.value })}
                >
                  <option value="unknown">Not sure yet</option>
                  <option value="vehicle">Vehicle price only</option>
                  <option value="total">
                    Everything, including taxes and fees
                  </option>
                </select>
              </label>
              <label>
                Minimum seats
                <input
                  type="number"
                  min={1}
                  max={15}
                  value={preferences.min_seats ?? ""}
                  onChange={(e) =>
                    updatePrefs({
                      min_seats: e.target.value ? Number(e.target.value) : null,
                    })
                  }
                />
              </label>
              <label>
                Maximum mileage
                <input
                  type="number"
                  min={0}
                  max={10000000}
                  value={preferences.max_mileage ?? ""}
                  onChange={(e) =>
                    updatePrefs({
                      max_mileage: e.target.value
                        ? Number(e.target.value)
                        : null,
                    })
                  }
                />
              </label>
              {(
                [
                  [
                    "body_style",
                    "Body style",
                    [
                      "sedan",
                      "suv",
                      "hatchback",
                      "truck",
                      "coupe",
                      "wagon",
                      "van",
                    ],
                  ],
                  [
                    "fuel_type",
                    "Fuel type",
                    [
                      "gasoline",
                      "diesel",
                      "hybrid",
                      "electric",
                      "plug_in_hybrid",
                    ],
                  ],
                  ["drivetrain", "Drivetrain", ["fwd", "rwd", "awd", "4wd"]],
                ] as const
              ).map(([key, label, values]) => (
                <label key={key}>
                  {label}
                  <select
                    value={preferences[key]}
                    onChange={(e) => updatePrefs({ [key]: e.target.value })}
                  >
                    <option value="any">Any / undecided</option>
                    {values.map((v) => (
                      <option value={v} key={v}>
                        {v.replaceAll("_", " ").toUpperCase()}
                      </option>
                    ))}
                  </select>
                </label>
              ))}
              <label>
                Must-have features
                <input
                  value={featuresText}
                  maxLength={400}
                  placeholder="For example: heated seats"
                  onChange={(e) => setFeaturesText(e.target.value)}
                  onBlur={() =>
                    updatePrefs({
                      required_features: featuresText
                        .split(",")
                        .map((v) => v.trim())
                        .filter(Boolean),
                    })
                  }
                />
                <small>
                  Use the listed feature names, separated by commas.
                </small>
              </label>
              <fieldset className="priorities">
                <legend>Priorities (preferences, not guarantees)</legend>
                {["price", "mileage", "space", "fuel_economy"].map((p) => (
                  <label className="checkbox" key={p}>
                    <input
                      type="checkbox"
                      checked={preferences.priorities.includes(p)}
                      onChange={(e) =>
                        updatePrefs({
                          priorities: e.target.checked
                            ? [...preferences.priorities, p]
                            : preferences.priorities.filter((v) => v !== p),
                        })
                      }
                    />
                    {p.replaceAll("_", " ")}
                  </label>
                ))}
              </fieldset>
            </fieldset>
          </details>
        </aside>
        <div className="shop-main">
          {tab === "Inventory" && (
            <>
              <div className="section-heading">
                <div>
                  <h2>Published inventory</h2>
                  <p className="muted">
                    Select two or three vehicles to compare.
                  </p>
                </div>
              </div>
              {!data.listings.length && (
                <section className="empty">
                  <h3>No published vehicles yet</h3>
                  <p>
                    The owner needs to review and publish inventory before
                    customers can compare it.
                  </p>
                </section>
              )}
              <div className="inventory-grid">
                {data.listings.map((l) => (
                  <article
                    key={l.id}
                    className={
                      "inventory-card " +
                      (selected.includes(l.id) ? "selected" : "")
                    }
                  >
                    <div className="inventory-content">
                      <span
                        className={
                          "badge " +
                          (l.facts.availability === "available" ? "green" : "")
                        }
                      >
                        {l.facts.availability}
                      </span>
                      <h3>{vehicleName(l.facts)}</h3>
                      {l.facts.synthetic && (
                        <small className="badge">Fictional example</small>
                      )}
                      <p className="card-price">{money(l.facts.price)}</p>
                      <p>
                        {l.facts.mileage.toLocaleString()} miles ·{" "}
                        {l.facts.seats
                          ? l.facts.seats + " seats"
                          : "Seats not provided"}
                      </p>
                      <p className="muted">
                        {l.facts.fuel_type?.replaceAll("_", " ") ||
                          "Fuel type not provided"}{" "}
                        ·{" "}
                        {l.facts.drivetrain?.toUpperCase() ||
                          "Drivetrain not provided"}
                      </p>
                      {matches !== null && (
                        <span
                          className={
                            "badge " + (matches.includes(l.id) ? "green" : "")
                          }
                        >
                          {matches.includes(l.id)
                            ? "Meets recorded hard requirements"
                            : "Mismatch or missing required facts"}
                        </span>
                      )}
                      <label className="checkbox">
                        <input
                          type="checkbox"
                          checked={selected.includes(l.id)}
                          disabled={
                            busy || (!selected.includes(l.id) && selected.length >= 3)
                          }
                          onChange={() => choose(l.id)}
                        />
                        Compare this vehicle
                      </label>
                      <a href={"/listing/" + l.id}>View listing</a>
                    </div>
                  </article>
                ))}
              </div>
            </>
          )}
          {tab === "FAQs" && (
            <section>
              <h2>Common questions</h2>
              {!data.knowledge.length && <p className="muted">No questions have been published yet.</p>}
              {data.knowledge.map((item) => (
                <details className="evidence-card" key={item.id}>
                  <summary>{item.question}</summary>
                  {item.status === "approved" ? (
                    <>
                      <p className="saved-reply">{item.answer}</p>
                      {item.source_note && <p><strong>Source</strong> {item.source_note}</p>}
                    </>
                  ) : (
                    <p>Staff can confirm this. Use Ask staff to follow up below.</p>
                  )}
                </details>
              ))}
            </section>
          )}
          {tab === "Compare" && (
            <>
              <div className="section-heading">
                <div>
                  <h2>Your comparison</h2>
                  <p className="muted">
                    Published facts first. AI can explain how the differences
                    relate to your needs.
                  </p>
                </div>
                <button
                  disabled={busy || selected.length < 2}
                  onClick={compare}
                >
                  Refresh comparison
                </button>
              </div>
              {chosen.length < 2 ? (
                <section className="empty">
                  <h3>Choose at least two vehicles</h3>
                  <button onClick={() => setTab("Inventory")}>
                    Choose from inventory
                  </button>
                </section>
              ) : (
                <>
                  <div className="table-scroll">
                    <table className="comparison-table">
                      <caption>Owner-approved vehicle specifications</caption>
                      <thead>
                        <tr>
                          <th scope="col">Specification</th>
                          {chosen.map((l) => (
                            <th scope="col" key={l.id}>
                              {vehicleName(l.facts)}
                              <button
                                className="text-button"
                                onClick={() => choose(l.id)}
                              >
                                Remove
                              </button>
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {fields.map(([key, label]) => (
                          <tr key={key}>
                            <th scope="row">{label}</th>
                            {chosen.map((l) => (
                              <td key={l.id}>{fact(l.facts, key)}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {comparison && (
                    <div className="comparison-results">
                      <p>
                        <strong>
                          Listed price difference:{" "}
                          {money(comparison.price_difference_cents)}.
                        </strong>
                      </p>
                      {comparison.listings.map((l: any) => (
                        <article key={l.id}>
                          <h3>{vehicleName(l.facts)}</h3>
                          {l.budget_difference_cents !== null && (
                            <p>
                              {money(Math.abs(l.budget_difference_cents))}{" "}
                              {l.budget_difference_cents >= 0
                                ? "below"
                                : "above"}{" "}
                              your budget, before taxes and fees.
                            </p>
                          )}
                          <ul>
                            {l.checks.map((c: any) => (
                              <li key={c.label}>
                                <span className={"check-status " + c.status}>
                                  {c.status}
                                </span>{" "}
                                {c.label}: {c.note}
                              </li>
                            ))}
                          </ul>
                        </article>
                      ))}
                    </div>
                  )}
                  <button
                    className="primary"
                    disabled={busy || !ai}
                    onClick={() =>
                      ask(
                        "How do these vehicles compare for my needs? Explain the trade-offs and what I should check with staff.",
                      )
                    }
                  >
                    Explain this comparison with AI
                  </button>
                </>
              )}
            </>
          )}
          {tab === "AI chat" && (
            <section className="shopping-chat">
              <div className="section-heading">
                <h2>Shopping assistant</h2>
                {(messages.length > 0 || chatError) && <button className="text-button" disabled={busy} onClick={newChat}>New chat</button>}
              </div>
              <div
                className="shopping-conversation"
                role="log"
                aria-live="polite"
              >
                {!messages.length && !pendingQuestion && !chatError && (
                  <p className="chat-intro">{ai ? "Tell me how you’ll use the car and what matters most to you." : "Chat is unavailable. You can compare listings or contact staff."}</p>
                )}
                {messages.map((m, i) => (
                  <article key={i}>
                    <p className="bubble customer">
                      <strong>You</strong>
                      {m.question}
                    </p>
                    <div className="bubble assistant">
                      <strong>Assistant</strong>
                      <p className="chat-reply">{m.answer}</p>
                      {m.follow_up && (
                        <p className="followup-question">{m.follow_up}</p>
                      )}
                      {m.sources.length > 0 && (
                        <details>
                          <summary>Sources used ({m.sources.length})</summary>
                          <ul>
                            {m.sources.map((s) => (
                              <li key={s.id}>
                                {s.listing_id ? (
                                  <a
                                    href={"/listing/" + s.listing_id}
                                    target="_blank"
                                    rel="noreferrer"
                                  >
                                    {s.label}
                                  </a>
                                ) : (
                                  <strong>{s.label}</strong>
                                )}
                                <p>{s.text}</p>
                                {s.reference && <small>{s.reference}</small>}
                              </li>
                            ))}
                          </ul>
                        </details>
                      )}
                      {m.partial && <small>Some details could not be verified and were left out.</small>}
                    </div>
                  </article>
                ))}
                {pendingQuestion && <article>
                  <p className="bubble customer"><strong>You</strong>{pendingQuestion}</p>
                  <p className="bubble assistant" role="status">Thinking…</p>
                </article>}
                {chatError && <article>
                  <p className="bubble customer"><strong>You</strong>{chatError.question}</p>
                  <div className="bubble chat-error" role="alert">
                    {chatError.detail}
                    {chatError.requestId && <details><summary>Request reference</summary><code>{chatError.requestId}</code></details>}
                  </div>
                </article>}
                <div ref={chatEnd} />
              </div>
              {recommended.length > 0 && (
                <div className="recommendation-links">
                  <strong>Suggested matches</strong>
                  {recommended.map((lid) => {
                    const l = data.listings.find((v) => v.id === lid);
                    return (
                      l && (
                        <button
                          key={lid}
                          onClick={() => {
                            if (!selected.includes(lid) && selected.length < 3)
                              choose(lid);
                            setTab("Inventory");
                          }}
                        >
                          {vehicleName(l.facts)} · {money(l.facts.price)} · Add
                          to comparison
                        </button>
                      )
                    );
                  })}
                </div>
              )}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  ask();
                }}
              >
                <label>
                  Your message
                  <textarea
                    maxLength={1000}
                    disabled={aiBusy || !ai}
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask about a car or tell us what you need…"
                  />
                </label>
                <button
                  className="primary"
                  disabled={busy || !ai || !question.trim()}
                >
                  Send to AI
                </button>
                <small>Messages go to xAI. Use the staff form for contact details.</small>
              </form>
            </section>
          )}
          <section className="staff-help">
            <h2>Contact the dealership</h2>
            <button onClick={prepareFollowup}>Ask staff to follow up</button>
            {showFollowup && (
              <form
                className="full-width"
                onSubmit={(e) => {
                  e.preventDefault();
                  work(async () => {
                    await api("/shop/" + id + "/inquiries", "POST", {
                      request_key: requestKey.current,
                      contact,
                      message: summary,
                      consent,
                      preferences: currentPrefs(),
                      listing_ids: selected,
                    });
                    setShowFollowup(false);
                    setContact("");
                    setConsent(false);
                    setNotice("Inquiry saved in the staff inbox.");
                  });
                }}
              >
                <label>
                  Your question or summary
                  <textarea
                    required
                    maxLength={1000}
                    value={summary}
                    onChange={(e) => {
                      setSummary(e.target.value);
                      requestKey.current = crypto.randomUUID();
                    }}
                  />
                </label>
                <label>
                  Email or phone for follow-up
                  <input
                    required
                    minLength={3}
                    maxLength={300}
                    value={contact}
                    onChange={(e) => {
                      setContact(e.target.value);
                      requestKey.current = crypto.randomUUID();
                    }}
                  />
                </label>
                <details>
                  <summary>Review what will be sent</summary>
                  <p>
                    Selected:{" "}
                    {chosen.map((l) => vehicleName(l.facts)).join(", ") ||
                      "No vehicles selected"}
                  </p>
                  <dl>
                    {Object.entries(preferences)
                      .filter(([, v]) => v !== null && v !== "any")
                      .map(([k, v]) => (
                        <div key={k}>
                          <dt>{k.replaceAll("_", " ")}</dt>
                          <dd>
                            {k === "budget_cents"
                              ? money(Number(v))
                              : Array.isArray(v)
                                ? v.join(", ")
                                : String(v)}
                          </dd>
                        </div>
                      ))}
                  </dl>
                </details>
                <label className="checkbox">
                  <input
                    type="checkbox"
                    required
                    checked={consent}
                    onChange={(e) => setConsent(e.target.checked)}
                  />
                  I agree to send these details to staff for follow-up.
                </label>
                <button
                  className="primary"
                  disabled={
                    busy ||
                    !consent ||
                    contact.trim().length < 3 ||
                    !summary.trim()
                  }
                >
                  Send inquiry to staff
                </button>
                <button type="button" onClick={() => setShowFollowup(false)}>
                  Cancel
                </button>
              </form>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
