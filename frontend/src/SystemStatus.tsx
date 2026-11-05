import { useEffect, useState } from 'react';
import { Api, dateTime } from './domain';
export default function SystemStatus({ api }: {
    api: Api;
}) {
    const [status, setStatus] = useState<any>(null), [failed, setFailed] = useState(false), [busy, setBusy] = useState(false);
    async function refresh() { setBusy(true); setFailed(false); try {
        setStatus(await api('/diagnostics'));
    }
    catch {
        setFailed(true);
    }
    finally {
        setBusy(false);
    } }
    useEffect(() => { refresh(); }, []);
    const last = status?.last_successful_ai_request;
    let usage: any = {};
    try {
        usage = JSON.parse(last?.usage || '{}');
    }
    catch { /* No provider usage available. */ }
    return <section><div className="section-heading"><div><p className="eyebrow">Presentation readiness</p><h1>System status</h1></div><button disabled={busy} onClick={refresh}>{busy ? 'Checking…' : 'Refresh status'}</button></div>
 {failed ? <p className="notice" role="alert">System checks failed or owner access is unavailable. Sign in again and retry. Database and Auth readiness could not be confirmed.</p> : status && <>
  <div className="status-grid">{[['Supabase Auth', status.auth], ['PostgreSQL database', status.database], ['Grok listing drafting', status.drafting], ['Customer question mode', status.question_mode === 'ai' ? 'Live AI' : 'Scripted fallback'], ['Backend health', status.backend], ['AI call limit', `${status.ai_calls_used} used / ${status.ai_call_limit} total`]].map(([label, value]) => <article key={label}><p>{label}</p><strong className={['failed', 'unavailable', 'last request failed'].includes(value) ? 'error-text' : ''}>{value}</strong></article>)}</div>
  <div className="saved-summary"><h2>Last successful AI request</h2>{last ? <dl className="specs"><div><dt>Model</dt><dd>{last.model}</dd></div><div><dt>Tokens</dt><dd>{usage.total_tokens ?? 'Not reported'}</dd></div><div><dt>Time</dt><dd>{dateTime(last.created_at)}</dd></div></dl> : <p>No successful AI request recorded yet.</p>}</div><p className="muted">Status checks do not make paid AI requests. The call cap includes failed attempts and does not show your xAI dollar balance.</p>
  <details><summary>Technical API diagnostics</summary><pre>{JSON.stringify(status, null, 2)}</pre><a href="/docs" target="_blank" rel="noreferrer">Open API reference</a></details>
 </>}{busy && !status && <p role="status">Checking connected services…</p>}</section>;
}
