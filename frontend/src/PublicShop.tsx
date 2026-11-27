import { useEffect, useRef, useState } from "react";
import Icon from "./Icon";
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
type Message = {
  question: string;
  answer: string;
  follow_up?: string;
  sources: any[];
  task_id?: string;
  request_id?: string;
};

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
      knowledge: any[];
    } | null>(null),
    [tab, setTab] = useState("Inventory"),
    [error, setError] = useState(""),
    [notice, setNotice] = useState("");
  const [selected, setSelected] = useState<string[]>([]),
    [preferences, setPreferences] = useState<Preferences>(defaults),
    [budget, setBudget] = useState(""),
    [featuresText, setFeaturesText] = useState(""),
    [question, setQuestion] = useState(""),
    [messages, setMessages] = useState<Message[]>([]);
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
  function exportConversation() {
    const content = { exported_at: new Date().toISOString(), business_id: id, preferences, selected_ids: selected,
      note: "Actual accepted responses from this browser tab. Not a new AI request.", messages };
    const url = URL.createObjectURL(new Blob([JSON.stringify(content, null, 2)], {type: "application/json"}));
    const link = document.createElement("a"); link.href = url; link.download = "frontdesk-conversation.json"; link.click();
    URL.revokeObjectURL(url);
  }
  useEffect(() => {
    api("/shop/" + id)
      .then(setData)
      .catch((e) => setError(e.message));
  }, [id]);
  useEffect(() => {
    const container = chatEnd.current?.parentElement;
    if (container) container.scrollTop = container.scrollHeight;
  }, [messages, aiBusy]);
  useEffect(() => {
    const resize = () => setPreferencesOpen(tab === "Find my fit" && window.innerWidth > 960);
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
  async function compare() {
    await work(async () => {
      const updated = currentPrefs();
      setPreferences(updated);
      const r = await api("/shop/" + id + "/compare", "POST", {
        listing_ids: selected,
        preferences: updated,
      });
      setComparison(r);
      setData((d) =>
        d
          ? {
              ...d,
              listings: d.listings.map(
                (l) => r.listings.find((v: Vehicle) => v.id === l.id) || l,
              ),
            }
          : d,
      );
      setTab("Compare");
    });
  }
  async function ask(text = question) {
    await work(async () => {
      if (!text.trim()) return;
      const history = messages.slice(-4).flatMap((m) => [
        { role: "user", content: m.question },
        {
          role: "assistant",
          content: (m.answer + " " + (m.follow_up || "")).slice(0, 1600),
        },
      ]);
      const r = await api("/shop/" + id + "/assist", "POST", {
        message: text,
        preferences: currentPrefs(),
        history,
        selected_ids: selected,
      });
      setPreferences(r.preferences);
      setFeaturesText(r.preferences.required_features.join(", "));
      setBudget(
        r.preferences.budget_cents === null
          ? ""
          : String(r.preferences.budget_cents / 100),
      );
      setRecommended(r.recommended_ids);
      setMatches(r.matches);
      if (tab === "Compare" && selected.length >= 2) {
        const refreshed = await api("/shop/" + id + "/compare", "POST", {
          listing_ids: selected,
          preferences: r.preferences,
        });
        setComparison(refreshed);
        setData((d) =>
          d
            ? {
                ...d,
                listings: d.listings.map(
                  (l) =>
                    refreshed.listings.find((v: Vehicle) => v.id === l.id) || l,
                ),
              }
            : d,
        );
      } else setComparison(null);
      setMessages((ms) => [
        ...ms,
        {
          question: text,
          answer: r.answer,
          follow_up: r.follow_up,
          sources: r.sources,
          task_id: r.task_id,
          request_id: r.request_id,
        },
      ]);
      setQuestion("");
      setNotice(
        "Answer received from live AI and checked against published source IDs. Review the facts and limitations below.",
      );
    }, true);
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
      <div className="shop-hero">
        <div>
          <p className="eyebrow">{data.name} · FrontDesk AI</p>
          <h1>{tab === "Find my fit" ? "Tell us what matters." : <>Find your next car.<br /><span>Know why it fits.</span></>}</h1>
          <p className="lead">
            Explore reviewed inventory, compare the details, and get an explanation built around your needs.
          </p>
          <button className="hero-cta" onClick={() => setTab("Find my fit")}>Help me choose <Icon name="arrow" /></button>
        </div>
        <div className="hero-stamp">
          <strong>
            {
              data.listings.filter((l) => l.facts.availability === "available")
                .length
            }
          </strong>
          <span>available vehicles</span>
          <small>Reviewed information.<br />A clearer starting point.</small>
        </div>
      </div>
      <nav className="shop-nav" aria-label="Shopping sections">
        {["Inventory", "Find my fit", "Compare"].map((t) => (
          <button
            key={t}
            aria-current={tab === t ? "page" : undefined}
            className={tab === t ? "active" : ""}
            onClick={() => setTab(t)}
          >
            {t}
            {t === "Compare" && (
              <span className="count">{selected.length}</span>
            )}
          </button>
        ))}
      </nav>
      {selected.length > 0 && <div className="selection-tray" aria-label="Selected vehicles"><span><strong>{selected.length} of 3 selected</strong> · {data.listings.filter(l => selected.includes(l.id)).map(l => l.facts.model).join(" + ")}</span><div className="actions"><button disabled={busy || selected.length < 2} onClick={compare}>Compare selected</button><button className="primary" onClick={() => setTab("Find my fit")}>Ask about my selection</button><button onClick={() => { setSelected([]); setComparison(null); }}>Clear selection</button></div></div>}
      {data.listings.some((l) => l.facts.synthetic) && (
        <p className="notice">
          Vehicles marked “Fictional example” use illustrative specifications
          for the class showcase. They are not real sale offers.
        </p>
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
      <div className={"shop-layout" + (tab === "Find my fit" ? " fit-layout" : "")}>
        <aside className="preference-panel">
          <details
            open={preferencesOpen}
            onToggle={(e) => setPreferencesOpen(e.currentTarget.open)}
          >
            <summary className="preference-summary">
              <span className="eyebrow">Your requirements</span>
              <strong>What matters to you?</strong>
            </summary>
            <div className="preference-fields">
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
              <button
                disabled={busy}
                onClick={() => {
                  setPreferences(defaults);
                  setBudget("");
                  setFeaturesText("");
                  setMessages([]);
                  setRecommended([]);
                  setMatches(null);
                  setComparison(null);
                  setNotice("Started a new consultation.");
                }}
              >
                Start over
              </button>
              <p className="privacy">
                Preferences stay in this page until you submit them to staff. AI
                messages go to xAI. Keep contact details out of chat.
              </p>
            </div>
          </details>
        </aside>
        <div className="shop-main">
          {tab === "Inventory" && (
            <>
              <div className="section-heading">
                <div>
                  <h2>Published inventory</h2>
                  <p className="muted">
                    Select two or three vehicles to compare. Unknown
                    specifications stay marked “Not provided”.
                  </p>
                </div>
                <button
                  className="primary"
                  disabled={selected.length < 2 || busy}
                  onClick={compare}
                >
                  Compare selected ({selected.length})
                </button>
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
                    <div className="vehicle-silhouette" aria-hidden="true">
                      <span>
                        {l.facts.body_style?.toUpperCase() || "VEHICLE"}
                      </span>
                      <svg viewBox="0 0 240 80" fill="none">
                        <path d="M20 52h12l25-29h85l44 25 30 8v15H20V52Z" />
                        <path d="M64 30h35v20H47m60-20h30l35 20h-65V30Z" />
                        <circle cx="61" cy="67" r="12" />
                        <circle cx="180" cy="67" r="12" />
                      </svg>
                      <small>Illustration · vehicle photos not supplied</small>
                    </div>
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
                            !selected.includes(l.id) && selected.length >= 3
                          }
                          onChange={() => choose(l.id)}
                        />
                        Compare this vehicle
                      </label>
                      <a href={"/listing/" + l.id}>View approved listing ↗</a>
                    </div>
                  </article>
                ))}
              </div>
            </>
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
                        </strong>{" "}
                        Calculated by the backend, without an AI request.
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
                  <p className="notice">
                    A vehicle price below your total budget does not prove it
                    fits after taxes and fees. Missing costs require staff
                    confirmation.
                  </p>
                  <button
                    className="primary"
                    disabled={busy || !ai}
                    onClick={() =>
                      ask(
                        "Compare the selected vehicles against my preferences. Explain the trade-offs and any missing information. Do not assume missing preferences.",
                      )
                    }
                  >
                    Explain this comparison with AI
                  </button>
                </>
              )}
            </>
          )}
          {(tab === "Find my fit" || tab === "Compare") && (
            <section className="shopping-chat">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">A conversation around your needs</p>
                  <h2>
                    {tab === "Compare"
                      ? "Discuss the trade-offs"
                      : "Find my fit"}
                  </h2>
                </div>
                <span className="badge">
                  {ai ? "Live AI enabled" : "AI disabled"}
                </span>
              </div>
              {messages.length > 0 && <div className="actions chat-tools"><button onClick={exportConversation}>Save conversation</button><button disabled={busy} onClick={() => { setMessages([]); setRecommended([]); setMatches(null); setQuestion(""); }}>New conversation</button><small>Saved files contain the messages you entered. Refreshing this page clears the chat.</small></div>}
              <p>
                Describe your budget, driving routine or priorities. The
                assistant can ask a follow-up, suggest options and explain its
                sources.
              </p>
              {!ai && (
                <p className="notice">
                  Live AI is disabled. You can still browse inventory, set
                  preferences and compare facts. A rehearsal is not evidence of
                  a real Grok call.
                </p>
              )}
              {!messages.length && (
                <div className="starter-prompts">
                  {[
                    "I have $25,000 and commute every day. What should I consider?",
                    "I need space for my family but I am not sure which car fits.",
                    "Is this a fair price? What can you actually verify?",
                  ].map((t) => (
                    <button key={t} onClick={() => setQuestion(t)}>
                      {t}
                    </button>
                  ))}
                </div>
              )}
              <div
                className="shopping-conversation"
                role="log"
                aria-live="polite"
              >
                {messages.map((m, i) => (
                  <article key={i}>
                    <p className="bubble customer">
                      <strong>You</strong>
                      {m.question}
                    </p>
                    <div className="bubble assistant">
                      <strong>FrontDesk AI</strong>
                      <p>{m.answer}</p>
                      {m.follow_up && (
                        <p className="followup-question">{m.follow_up}</p>
                      )}
                      {m.sources.length > 0 && (
                        <details>
                          <summary>Sources used ({m.sources.length})</summary>
                          <ul>
                            {m.sources.map((s: any) => (
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
                              </li>
                            ))}
                          </ul>
                        </details>
                      )}
                      <small>
                        Live AI · response checked against published source
                        references. Recommendations still require judgment.
                      </small>
                    </div>
                  </article>
                ))}
                {aiBusy && <p role="status">Checking published information…</p>}
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
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Tell us what you need, or ask a follow-up…"
                  />
                </label>
                <button
                  className="primary"
                  disabled={busy || !ai || !question.trim()}
                >
                  {aiBusy ? "Thinking…" : "Send to AI"}
                </button>
                <small>
                  Each send or explanation uses a paid request, subject to the
                  owner’s shared limit.
                </small>
              </form>
            </section>
          )}
          <section className="staff-help">
            <div>
              <h2>A person can take it from here.</h2>
              <p>
                Send your selected vehicles, recorded requirements and question
                to the dealership. Nothing is sent until you approve it.
              </p>
            </div>
            <button onClick={prepareFollowup}>Ask staff to follow up</button>
            {showFollowup && (
              <form
                className="full-width"
                onSubmit={(e) => {
                  e.preventDefault();
                  work(async () => {
                    if (
                      budget.trim() &&
                      dollarsToCents(budget) !== preferences.budget_cents
                    )
                      throw Error(
                        "Finish editing the budget before submitting.",
                      );
                    await api("/shop/" + id + "/inquiries", "POST", {
                      request_key: requestKey.current,
                      contact,
                      message: summary,
                      consent,
                      preferences,
                      listing_ids: selected,
                    });
                    setShowFollowup(false);
                    setContact("");
                    setConsent(false);
                    setNotice(
                      "Inquiry saved in the staff inbox. No appointment, email or text message was sent.",
                    );
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
