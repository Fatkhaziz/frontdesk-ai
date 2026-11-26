import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { createClient } from "@supabase/supabase-js";
import {
  Car,
  Config,
  defaultCar,
  sortCars,
  money,
  vehicleName,
  dateTime,
} from "./domain";
import ListingEditor from "./ListingEditor";
import PublicListing from "./PublicListing";
import SystemStatus from "./SystemStatus";
import BusinessSettings from "./BusinessSettings";
import PublicBusiness from "./PublicBusiness";
import PublicShop from "./PublicShop";
import KnowledgeSetup from "./KnowledgeSetup";
import { Workspace } from "./business";
import "./style.css";
function App() {
  const [config, setConfig] = useState<Config | null>(null),
    [token, setToken] = useState("");
  const [email, setEmail] = useState(""),
    [password, setPassword] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false);
  const lock = useRef(false);
  const [cars, setCars] = useState<Car[]>([]),
    [car, setCar] = useState<Car | null>(null),
    [inbox, setInbox] = useState<any[]>([]);
  const [editorStage, setEditorStage] = useState(1);
  const [listingSearch, setListingSearch] = useState("");
  const [listingFilter, setListingFilter] = useState("all");
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [tab, setTab] = useState("Listings"),
    [editorKey, setEditorKey] = useState(0);
  const lid = location.pathname.startsWith("/listing/")
    ? location.pathname.split("/")[2]
    : null;
  const shopId = location.pathname.startsWith("/shop/")
    ? location.pathname.split("/")[2]
    : null;
  const businessId = location.pathname.startsWith("/business/")
    ? location.pathname.split("/")[2]
    : null;
  const authClient = useMemo(() => config?.supabaseUrl && config?.supabaseKey && !lid && !shopId && !businessId
    ? createClient(config.supabaseUrl, config.supabaseKey, { auth: {
      persistSession: false, autoRefreshToken: true, detectSessionInUrl: false,
    }}) : null, [config?.supabaseUrl, config?.supabaseKey]);
  useEffect(() => {
    if (!authClient) return;
    const { data } = authClient.auth.onAuthStateChange((_event, session) => setToken(session?.access_token || ""));
    return () => { data.subscription.unsubscribe(); authClient.auth.stopAutoRefresh(); };
  }, [authClient]);
  async function api(path: string, method = "GET", body?: unknown) {
    const r = await fetch("/api" + path, {
      method,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: "Bearer " + token } : {}),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const data = await r.json();
    if (!r.ok) {
      if (r.status === 422)
        throw Error("Please check the required fields and use valid numbers.");
      throw Error(
        typeof data.detail === "string"
          ? data.detail
          : "We could not complete that action. Please try again.",
      );
    }
    return data;
  }
  async function run(fn: () => Promise<void>) {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setMessage("");
    try {
      await fn();
    } catch (e) {
      setMessage(
        e instanceof Error
          ? e.message
          : "Something went wrong. Please try again.",
      );
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  function select(c: Car | null) {
    setEditorStage(1);
    setCar(c);
    setEditorKey((k) => k + 1);
    if (c) sessionStorage.setItem("frontdesk-selected-listing", c.id);
    else sessionStorage.removeItem("frontdesk-selected-listing");
  }
  async function load() {
    const [cs, is, ws] = await Promise.all([
      api("/listings"),
      api("/inquiries"),
      api("/workspace"),
    ]);
    setCars(sortCars(cs));
    setInbox(is);
    setWorkspace(ws);
    return cs as Car[];
  }
  useEffect(() => {
    api("/config")
      .then(setConfig)
      .catch(() =>
        setMessage("The service is unavailable. Please reload in a moment."),
      );
  }, []);
  useEffect(() => {
    if (token)
      run(async () => {
        const cs = await load();
        select(
          cs.find(
            (c) =>
              c.id === sessionStorage.getItem("frontdesk-selected-listing"),
          ) ||
            defaultCar(cs) ||
            null,
        );
      });
  }, [!!token]);
  const salon = workspace?.profile && workspace.profile.domain !== "dealership";
  const tabs = [
    "Business settings",
    ...(!salon ? ["Listings"] : []),
    "Inquiries",
    ...(workspace?.role === "owner"
      ? ["Owner knowledge", "System status"]
      : []),
  ];
  const visibleTab = tabs.includes(tab) ? tab : "Business settings";
  return (
    <main className={token && !shopId && !businessId && !lid ? "owner-app" : "public-app"}>
      <header>
        <a className="brand" href="/">
          FrontDesk <strong>AI</strong>
        </a>
        <span>
          {token
            ? workspace?.profile?.name || workspace?.name
            : "For small businesses"}{" "}
          <span className="header-tag">Fall Release 1</span>
        </span>
      </header>
      {config?.rehearsal && (
        <p className="notice">
          Rehearsal only · Synthetic local data · Simulated sign-in · Paid AI
          disabled
        </p>
      )}
      {shopId ? (
        config && <PublicShop id={shopId} api={api} config={config} />
      ) : businessId ? (
        <PublicBusiness id={businessId} api={api} />
      ) : lid ? (
        config && <PublicListing id={lid} api={api} config={config} />
      ) : !token ? (
        <div className="login-layout">
          <div>
            <p className="eyebrow">Your business front desk</p>
            <h1>
              Clear answers.
              <br />
              Your business rules.
              <br />
              Human approval.
            </h1>
            <p className="lead">
              Publish approved business information and give customer inquiries
              a place for follow-up.
            </p>
          </div>
          <section>
            <h2>Welcome back</h2>
            <p>Sign in with your verified business account.</p>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                run(async () => {
                  if (!config)
                    throw Error("Please wait for the service to connect.");
                  if (!authClient) throw Error("Sign-in configuration is unavailable.");
                  const { data, error } = await authClient.auth.signInWithPassword({
                    email,
                    password,
                  });
                  if (error || !data.session)
                    throw Error(
                      "Sign-in failed. Check your email and password, then try again.",
                    );
                  setToken(data.session.access_token);
                  setPassword("");
                });
              }}
            >
              <label>
                Email
                <input
                  type="email"
                  required
                  autoComplete="username"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </label>
              <label>
                Password
                <input
                  type="password"
                  required
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </label>
              <button className="primary" disabled={busy || !config}>
                {busy ? "Signing in…" : "Sign in"}
              </button>
            </form>
            <small>
              After refreshing, sign in again. Your saved records and selected
              listing will be restored.
            </small>
          </section>
        </div>
      ) : (
        <>
          <div className="dashboard-heading">
            <div>
              <p className="eyebrow">Business workspace</p>
              <h1>Your front desk</h1>
            </div>
            <button
              disabled={busy}
              onClick={() => {
                authClient?.auth.signOut();
                setToken("");
                setTab("Business settings");
                setWorkspace(null);
                setCars([]);
                setInbox([]);
                setCar(null);
                setMessage("Signed out.");
              }}
            >
              Sign out
            </button>
          </div>
          <nav aria-label="Dashboard sections">
            {tabs.map((t) => (
              <button
                key={t}
                aria-current={visibleTab === t ? "page" : undefined}
                disabled={busy}
                className={visibleTab === t ? "active" : ""}
                onClick={() => {
                  setTab(t);
                  setMessage("");
                }}
              >
                {t}
                {t === "Inquiries" && (
                  <span className="count">
                    {inbox.filter((i) => i.status === "open").length}
                  </span>
                )}
              </button>
            ))}
          </nav>
          {message && (
            <p className="notice" role="status" aria-live="polite">
              {message}
            </p>
          )}
          {visibleTab === "Owner knowledge" && workspace && (
            <KnowledgeSetup
              api={api}
              run={run}
              busy={busy}
              notify={setMessage}
              businessId={workspace.id}
            />
          )}
          {visibleTab === "Business settings" && workspace && (
            <BusinessSettings
              workspace={workspace}
              api={api}
              run={run}
              busy={busy}
              refresh={async () => {
                await load();
              }}
              notify={setMessage}
            />
          )}
          {visibleTab === "Listings" && (
            <>
              <div className="section-heading">
                <div>
                  <h2>Listings</h2>
                  <p className="muted">
                    Prepare privately. Publish only after owner review.
                  </p>
                </div>
                <div className="actions">
                  {workspace && (
                    <a
                      className="button"
                      target="_blank"
                      rel="noreferrer"
                      href={"/shop/" + workspace.id}
                    >
                      Open customer inventory ↗
                    </a>
                  )}
                  <button
                    disabled={busy}
                    onClick={() =>
                      run(async () => {
                        const cs = await load();
                        select(
                          cs.find((c) => c.id === car?.id) ||
                            defaultCar(cs) ||
                            null,
                        );
                        setMessage("Saved records refreshed.");
                      })
                    }
                  >
                    Refresh records
                  </button>
                  <button
                    className="primary"
                    disabled={busy}
                    onClick={() => select(null)}
                  >
                    + New listing
                  </button>
                </div>
              </div>
              <div className="workspace">
                <aside className="listing-list" aria-label="Saved vehicles">
                  <div className="listing-tools">
                    <label>Find a vehicle<input type="search" placeholder="Make, model or year" value={listingSearch} onChange={e => setListingSearch(e.target.value)} /></label>
                    <label>Show<select value={listingFilter} onChange={e => setListingFilter(e.target.value)}><option value="all">All listings ({cars.length})</option><option value="published">Published</option><option value="draft">Private drafts</option></select></label>
                  </div>
                  {cars.length === 0 && (
                    <p className="empty">
                      No vehicles yet. Create your first listing.
                    </p>
                  )}
                  {cars.filter(c => vehicleName(c.facts).toLowerCase().includes(listingSearch.toLowerCase()) && (listingFilter === "all" || (listingFilter === "published" ? c.published_revision !== null : c.published_revision === null))).map((c) => {
                    const matches = cars.filter(
                      (v) => vehicleName(v.facts) === vehicleName(c.facts),
                    );
                    const duplicate = matches.length > 1;
                    return (
                      <button
                        className={
                          "vehicle-card " + (c.id === car?.id ? "selected" : "")
                        }
                        key={c.id}
                        disabled={busy}
                        onClick={() => select(c)}
                      >
                        <span
                          className={
                            "badge " +
                            (c.published_revision !== null ? "green" : "")
                          }
                        >
                          {c.published_revision !== null
                            ? "Published"
                            : "Draft"}
                        </span>
                        <strong>{vehicleName(c.facts)}</strong>
                        <span>
                          {money(c.facts.price)} ·{" "}
                          {c.facts.mileage.toLocaleString()} miles
                        </span>
                        <small>
                          Saved r{c.revision} · Public{" "}
                          {c.published_revision === null
                            ? "none"
                            : "r" + c.published_revision}
                        </small>
                        {c.published_at && (
                          <small>Published {dateTime(c.published_at)}</small>
                        )}
                        {duplicate && (
                          <span className="duplicate">
                            {defaultCar(matches)?.id === c.id
                              ? "Latest published copy"
                              : "Duplicate / rehearsal copy"}
                          </span>
                        )}
                      </button>
                    );
                  })}
                </aside>
                <ListingEditor
                  key={editorKey}
                  stage={editorStage}
                  setStage={setEditorStage}
                  car={car}
                  api={api}
                  run={run}
                  busy={busy}
                  aiEnabled={!!config?.aiEnabled}
                  refresh={async () => {
                    await load();
                  }}
                  onSaved={(c) => {
                    setCar(c);
                    setEditorKey((k) => k + 1);
                    sessionStorage.setItem("frontdesk-selected-listing", c.id);
                  }}
                  onDeleted={() => select(null)}
                  notify={setMessage}
                />
              </div>
            </>
          )}
          {visibleTab === "Inquiries" && (
            <section>
              <div className="section-heading">
                <div>
                  <p className="eyebrow">Customer follow-up</p>
                  <h1>Inquiries</h1>
                </div>
                <button
                  disabled={busy}
                  onClick={() =>
                    run(async () => {
                      await load();
                      setMessage("Inbox refreshed.");
                    })
                  }
                >
                  Refresh inquiries
                </button>
              </div>
              <p className="muted">
                Newest first. Follow up using the customer’s contact details.
              </p>
              {inbox.length === 0 ? (
                <div className="empty">
                  <h3>You’re all caught up</h3>
                  <p>Customer handoffs will appear here.</p>
                </div>
              ) : (
                inbox.map((i) => (
                  <article className="inquiry" key={i.id}>
                    <div>
                      <span
                        className={
                          "badge " + (i.status === "resolved" ? "green" : "")
                        }
                      >
                        {i.status}
                      </span>
                      <h3>{i.vehicle_name}</h3>
                      <p className="inquiry-question">{i.message}</p>
                      <p>
                        <strong>Contact:</strong> {i.contact}
                      </p>
                      {i.kind === "business" && (
                        <dl>
                          {Object.entries(i.answers).map(([key, value]) => (
                            <div key={key}>
                              <dt>
                                {i.answer_labels?.[key] ||
                                  key.replaceAll("-", " ")}
                              </dt>
                              <dd>{String(value)}</dd>
                            </div>
                          ))}
                        </dl>
                      )}
                      {i.kind === "shopping" && (
                        <details>
                          <summary>
                            Customer requirements and selected vehicles
                          </summary>
                          <dl>
                            {Object.entries(i.context.preferences).map(
                              ([key, value]) => (
                                <div key={key}>
                                  <dt>{key.replaceAll("_", " ")}</dt>
                                  <dd>
                                    {key === "budget_cents" && value !== null
                                      ? money(Number(value))
                                      : Array.isArray(value)
                                        ? value.join(", ") || "None"
                                        : value === null
                                          ? "Not specified"
                                          : String(value)}
                                  </dd>
                                </div>
                              ),
                            )}
                          </dl>
                          {i.context.listings.map((l: any) => (
                            <p key={l.id}>
                              {vehicleName(l.facts)} · {money(l.facts.price)} ·
                              approved revision {l.revision}
                            </p>
                          ))}
                        </details>
                      )}
                      <time dateTime={i.created_at}>
                        {dateTime(i.created_at)}
                      </time>
                    </div>
                    <label>
                      Status
                      <select
                        aria-label={"Status for " + i.vehicle_name + " inquiry"}
                        disabled={busy}
                        value={i.status}
                        onChange={(e) =>
                          run(async () => {
                            await api(
                              (i.kind === "shopping"
                                ? "/shopping/inquiries/"
                                : i.kind === "business"
                                  ? "/business/inquiries/"
                                  : "/inquiries/") + i.id,
                              "PATCH",
                              { status: e.target.value },
                            );
                            await load();
                            setMessage("Inquiry status saved.");
                          })
                        }
                      >
                        {["open", "pending", "resolved"].map((s) => (
                          <option key={s} value={s}>
                            {s[0].toUpperCase() + s.slice(1)}
                          </option>
                        ))}
                      </select>
                    </label>
                  </article>
                ))
              )}
            </section>
          )}
          {visibleTab === "System status" && <SystemStatus api={api} />}
        </>
      )}
      {!token && message && (
        <p role="alert" className="notice">
          {message}
        </p>
      )}
      <footer>FrontDesk AI · Fall Release 1 small-business prototype</footer>
    </main>
  );
}
createRoot(document.getElementById("root")!).render(<App />);
