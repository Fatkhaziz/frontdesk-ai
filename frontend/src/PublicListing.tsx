import { useEffect, useState, useRef } from 'react';
import { Api, Config, Facts, money, vehicleName } from './domain';
export default function PublicListing({ id, api, config }: {
    id: string;
    api: Api;
    config: Config;
}) {
    const [listing, setListing] = useState<{
        facts: Facts;
        description: string;
    } | null>(null), [error, setError] = useState('');
    const [question, setQuestion] = useState(''), [messages, setMessages] = useState<{
        question: string;
        answer: string;
    }[]>([]);
    const [busy, setBusy] = useState(false), [handoff, setHandoff] = useState(''), [contact, setContact] = useState(''), [notice, setNotice] = useState('');
    const requestKey = useRef(crypto.randomUUID());
    useEffect(() => { api('/public/' + id).then(setListing).catch(() => setError('This listing is unavailable. It may have been removed from sale.')); }, [id]);
    async function ask(e: React.FormEvent) {
        e.preventDefault();
        if (busy || !question.trim())
            return;
        setBusy(true);
        setError('');
        setNotice('');
        setHandoff('');
        try {
            const q = question.trim();
            const result = await api('/public/' + id + '/questions', 'POST', { question: q });
            setMessages(m => [...m, { question: q, answer: result.answer }]);
            setQuestion('');
            if (result.handoff) {
                setHandoff(q);
                requestKey.current = crypto.randomUUID();
            }
        }
        catch {
            setError('We could not check the approved facts. You can send your question to staff.');
            setHandoff(question.trim());
        }
        finally {
            setBusy(false);
        }
    }
    return <>{error && <p role="alert" className="notice">{error}</p>}{listing ? <>
  <div className="public-hero"><p className="eyebrow">Demo Motors · Available vehicles</p><h1>{vehicleName(listing.facts)}</h1><div className="price">{money(listing.facts.price)} <small>USD</small></div><div className="vehicle-meta"><span>{listing.facts.mileage.toLocaleString()} miles</span><span className="badge green">{listing.facts.availability}</span></div></div>
  <div className="public-layout"><section><p className="eyebrow">Vehicle overview</p><h2>Ready for your next drive</h2><p className="description">{listing.description}</p><dl className="specs"><div><dt>Model year</dt><dd>{listing.facts.year}</dd></div><div><dt>Mileage</dt><dd>{listing.facts.mileage.toLocaleString()} miles</dd></div><div><dt>Availability</dt><dd>{listing.facts.availability}</dd></div></dl><p className="muted">Details shown here have been reviewed and approved by the dealership.</p></section>
  <section className="chat"><p className="eyebrow">Your vehicle assistant</p><h2>Ask about this vehicle</h2><p>{config.questionMode === 'ai' ? 'Live AI helps identify price and mileage questions. Answers come from the approved listing.' : 'Scripted fallback answers supported price and mileage questions from the approved listing.'}</p><p className="privacy">{config.questionMode === 'ai' ? 'Supported questions are processed by xAI. ' : ''}Please leave personal details out of chat. For other questions, we can save an inquiry for staff.</p>
   <div className="conversation" role="log" aria-live="polite">{messages.length === 0 && <p className="empty">Try “What is the price?” or “How many miles does it have?”</p>}{messages.map((m, i) => <div key={i}><p className="bubble customer"><strong>You</strong>{m.question}</p><p className="bubble assistant"><strong>Vehicle assistant</strong>{m.answer}</p></div>)}</div>
   <form onSubmit={ask}><label>Your question<input value={question} maxLength={1000} onChange={e => setQuestion(e.target.value)}/></label><button className="primary" disabled={busy || !question.trim()}>{busy ? 'Checking approved facts…' : 'Ask question'}</button></form>
   {handoff && <form className="handoff" onSubmit={async (e) => { e.preventDefault(); if (busy)
            return; setBusy(true); setError(''); try {
            await api('/public/' + id + '/inquiries', 'POST', { contact: contact.trim(), message: handoff, request_key: requestKey.current });
            setHandoff('');
            setContact('');
            setNotice('Your inquiry has reached the dealership’s staff inbox. Staff can follow up using the contact you provided.');
        }
        catch {
            setError('Your inquiry was not saved. Please try again.');
        }
        finally {
            setBusy(false);
        } }}><h3>Let our staff help</h3><p>Question: {handoff}</p><label>Your email or phone<input required minLength={3} maxLength={300} value={contact} onChange={e => setContact(e.target.value)}/></label><small>Share contact details voluntarily so staff can follow up. No email or phone notification is sent by this demo.</small><button disabled={busy || contact.trim().length < 3} className="primary">Send inquiry to staff</button></form>}
   {notice && <p role="status" className="notice success">{notice}</p>}
  </section></div>
 </> : !error && <p role="status">Loading vehicle…</p>}</>;
}
