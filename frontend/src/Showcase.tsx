import { useEffect, useState } from "react";
import { Api, dateTime, money } from "./domain";

type Turn = {
  question: string;
  outcome: string;
  answer?: string;
  follow_up?: string;
  budget_cents?: number | null;
  min_seats?: number | null;
  sources?: { id: string; label: string; text: string; reference?: string }[];
  request_id?: string;
  provider_response_id?: string;
  provider_outcome?: string;
  model?: string;
  rejection?: { stage: string; reason: string; field?: string };
};

type SavedRun = { saved_at: string; turns: Turn[] };

export default function Showcase({ api, businessId, openKnowledge }: {
  api: Api;
  businessId: string;
  openKnowledge: () => void;
}) {
  const [run, setRun] = useState<SavedRun | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const shop = "/shop/" + encodeURIComponent(businessId);

  async function refresh() {
    setLoading(true);
    setError(false);
    try {
      const saved = await api("/assistant/saved-rehearsal");
      setRun(saved.run);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => { refresh(); }, []);

  return (
    <section>
      <h1>Dealership showcase</h1>
      <div className="showcase-features">
        <article className="saved-summary">
          <h2>Compare listings</h2>
          <p>Select two or three vehicles to compare listed prices, mileage, seats, fuel economy and features.</p>
          <a className="button" href={shop} target="_blank" rel="noreferrer">Open inventory to compare</a>
        </article>
        <article className="saved-summary">
          <h2>Customer AI chat</h2>
          <p>Describe your budget, daily driving or family needs. Ask follow-ups and inspect the sources used.</p>
          <a className="button primary" href={shop + "?view=fit"} target="_blank" rel="noreferrer">Open Find my fit</a>
        </article>
        <article className="saved-summary">
          <h2>Owner questions and answers</h2>
          <p>Get AI suggestions for likely customer questions. Add an answer and its source, or route it to staff.</p>
          <div className="actions">
            <button onClick={openKnowledge}>Open Owner knowledge</button>
            <a className="button" href={shop + "?view=questions"} target="_blank" rel="noreferrer">See published answers</a>
          </div>
        </article>
      </div>

      <div className="evidence-panel">
        <div className="section-heading">
          <div>
            <h2>Saved Grok responses</h2>
            <p className="muted">Read the shopping check run from Terminal. Refreshing this section uses no AI credit.</p>
          </div>
          <button disabled={loading} onClick={refresh}>Refresh saved responses</button>
        </div>
        {loading ? <p role="status">Looking for saved responses…</p> : error ? (
          <p role="alert">Could not load the saved check. Refresh saved responses to try again.</p>
        ) : !run ? (
          <p>No saved Terminal check was found for this business. Replies to messages sent in Find my fit appear in that customer tab.</p>
        ) : (
          <>
            <p>Saved Terminal check · {dateTime(run.saved_at)}</p>
            {run.turns.map((turn) => (
              <article className="evidence-card" key={turn.question}>
                <h3>{turn.question}</h3>
                {turn.answer ? (
                  <>
                    <p><strong>{turn.outcome === "accepted_with_limits" ? "Confirmed listing summary" : "Accepted Grok reply"}</strong></p>
                    <p className="saved-reply">{turn.answer}</p>
                    {turn.follow_up && <p><strong>Follow-up question</strong> {turn.follow_up}</p>}
                    <dl className="specs">
                      {turn.budget_cents != null && <div><dt>Recorded budget</dt><dd>{money(turn.budget_cents)}</dd></div>}
                      {turn.min_seats != null && <div><dt>Minimum seats</dt><dd>{turn.min_seats}</dd></div>}
                    </dl>
                    {!!turn.sources?.length && <details>
                      <summary>Sources used ({turn.sources.length})</summary>
                      <ul>{turn.sources.map((source) => <li key={source.id}>
                        <strong>{source.label}</strong><p>{source.text}</p>
                        {source.reference && <p>{source.reference}</p>}
                      </li>)}</ul>
                    </details>}
                  </>
                ) : (
                  <p>{turn.outcome === "invalid_output" || turn.outcome === "stale_source" ? "The application withheld this reply." : "There is no delivered answer for this turn."}</p>
                )}
                {turn.rejection && <p className="muted">Validation detail {turn.rejection.stage} / {turn.rejection.reason}{turn.rejection.field && ` / ${turn.rejection.field}`}</p>}
                {turn.request_id && <details>
                  <summary>Request evidence</summary>
                  <dl className="specs">
                    <div><dt>Application outcome</dt><dd>{turn.outcome}</dd></div>
                    <div><dt>Provider outcome</dt><dd>{turn.provider_outcome}</dd></div>
                    <div><dt>Model</dt><dd>{turn.model}</dd></div>
                    <div><dt>Request ID</dt><dd>{turn.request_id}</dd></div>
                    <div><dt>Provider response ID</dt><dd>{turn.provider_response_id ?? "Not reported"}</dd></div>
                  </dl>
                </details>}
              </article>
            ))}
          </>
        )}
      </div>
    </section>
  );
}
