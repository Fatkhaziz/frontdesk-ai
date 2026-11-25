import { useEffect, useState } from "react";
import { Api, dateTime } from "./domain";
export default function SystemStatus({ api }: { api: Api }) {
  const [status, setStatus] = useState<any>(null),
    [failed, setFailed] = useState(false),
    [busy, setBusy] = useState(false);
  const [runs, setRuns] = useState<any[]>([]);
  async function refresh() {
    setBusy(true);
    setFailed(false);
    try {
      const [s, r] = await Promise.all([
        api("/diagnostics"),
        api("/assistant/evidence"),
      ]);
      setStatus(s);
      setRuns(r);
    } catch {
      setFailed(true);
    } finally {
      setBusy(false);
    }
  }
  useEffect(() => {
    refresh();
  }, []);
  const last = status?.last_successful_ai_request;
  const evidence = status?.last_business_qa_evidence;
  let usage: any = {};
  try {
    usage = JSON.parse(last?.usage || "{}");
  } catch {
    /* No provider usage available. */
  }
  return (
    <section>
      <div className="section-heading">
        <div>
          <p className="eyebrow">Presentation readiness</p>
          <h1>System status</h1>
        </div>
        <button disabled={busy} onClick={refresh}>
          {busy ? "Checking…" : "Refresh status"}
        </button>
      </div>
      {failed ? (
        <p className="notice" role="alert">
          System checks failed or owner access is unavailable. Sign in again and
          retry. Database and Auth readiness could not be confirmed.
        </p>
      ) : (
        status && (
          <>
            <div className="status-grid">
              {[
                ["Supabase Auth", status.auth],
                ["PostgreSQL database", status.database],
                ["Grok listing drafting", status.drafting],
                [
                  "Customer question mode",
                  status.question_mode === "ai"
                    ? "Live AI"
                    : "Scripted fallback",
                ],
                ["Backend health", status.backend],
                [
                  "AI call limit",
                  `${status.ai_calls_used} used / ${status.ai_call_limit} total`,
                ],
              ].map(([label, value]) => (
                <article key={label}>
                  <p>{label}</p>
                  <strong
                    className={
                      ["failed", "unavailable", "last request failed"].includes(
                        value,
                      )
                        ? "error-text"
                        : ""
                    }
                  >
                    {value}
                  </strong>
                </article>
              ))}
            </div>
            <div className="saved-summary">
              <h2>Last successful vehicle provider request</h2>
              {last ? (
                <dl className="specs">
                  <div>
                    <dt>Model</dt>
                    <dd>{last.model}</dd>
                  </div>
                  <div>
                    <dt>Tokens</dt>
                    <dd>{usage.total_tokens ?? "Not reported"}</dd>
                  </div>
                  <div>
                    <dt>Time</dt>
                    <dd>{dateTime(last.created_at)}</dd>
                  </div>
                </dl>
              ) : (
                <p>No successful AI request recorded yet.</p>
              )}
            </div>
            <p className="muted">
              Status checks do not make paid AI requests. The call cap includes
              failed attempts and does not show your xAI dollar balance.
            </p>
            <div className="saved-summary">
              <h2>Business Q&amp;A evidence</h2>
              {evidence ? (
                <dl className="specs">
                  {[
                    ["HTTP request ID", evidence.request_id],
                    ["AI task ID", evidence.task_id],
                    ["Published revision", evidence.published_revision],
                    ["Provider outcome", evidence.provider_outcome],
                    ["Application outcome", evidence.application_outcome],
                    [
                      "Provider response ID",
                      evidence.provider_response_id ?? "Not reported",
                    ],
                    ["Latency (ms)", evidence.latency_ms],
                  ].map(([label, value]) => (
                    <div key={label}>
                      <dt>{label}</dt>
                      <dd>{value}</dd>
                    </div>
                  ))}
                </dl>
              ) : (
                <p>
                  No business Q&amp;A evidence recorded yet. Earlier vehicle
                  requests have their original metadata only.
                </p>
              )}
            </div>
            <details>
              <summary>Technical API diagnostics</summary>
              <pre>{JSON.stringify(status, null, 2)}</pre>
              <a href="/docs" target="_blank" rel="noreferrer">
                Open API reference
              </a>
            </details>
            <div className="evidence-panel">
              <h2>Latest showcase AI requests</h2>
              <p className="muted">
                Actual saved request records. Provider success means xAI
                returned a completion; application acceptance means our checks
                passed. These are separate outcomes.
              </p>
              {!runs.length ? (
                <p>
                  No showcase requests recorded yet. An empty table does not
                  prove a live AI call.
                </p>
              ) : (
                runs.map((r) => (
                  <article className="evidence-card" key={r.task_id}>
                    <div className="section-heading">
                      <h3>{r.operation.replaceAll("_", " ")}</h3>
                      <span className="badge">{r.application_outcome}</span>
                    </div>
                    <dl className="specs">
                      {[
                        ["Time", dateTime(r.created_at)],
                        ["Requested model", r.requested_model || r.model],
                        ["Provider model", r.provider_model || "Not reported"],
                        [
                          "Provider response ID",
                          r.provider_response_id || "Not returned",
                        ],
                        ["Provider outcome", r.provider_outcome],
                        ["Application outcome", r.application_outcome],
                        [
                          "Total tokens",
                          r.token_usage?.total_tokens ?? "Not reported",
                        ],
                        [
                          "Latency",
                          r.latency_ms === null
                            ? "Pending"
                            : r.latency_ms + " ms",
                        ],
                        ["Request ID", r.request_id],
                        ["Task ID", r.task_id],
                      ].map(([label, value]) => (
                        <div key={label}>
                          <dt>{label}</dt>
                          <dd className="identifier">{value}</dd>
                        </div>
                      ))}
                    </dl>
                    <details>
                      <summary>Published source evidence</summary>
                      <p>{r.source_ids?.length ?? 0} cited source references</p>
                      <pre>
                        {JSON.stringify(
                          {
                            source_ids: r.source_ids,
                            source_snapshot: r.source_snapshot,
                          },
                          null,
                          2,
                        )}
                      </pre>
                    </details>
                  </article>
                ))
              )}
            </div>
          </>
        )
      )}
      {busy && !status && <p role="status">Checking connected services…</p>}
    </section>
  );
}
