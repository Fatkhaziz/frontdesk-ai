import React, {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {createClient} from '@supabase/supabase-js';
import './style.css';

type Facts = {make: string; model: string; year: number; price: number; mileage: number; availability: string};
type Car = {id: string; revision: number; facts: Facts; description: string; published_revision: number | null};
type PublicListing = {facts: Facts; description: string; revision: number};
type Config = {supabaseUrl: string; supabaseKey: string; questionMode: 'demo' | 'ai'; aiEnabled: boolean};
const blank: Facts = {make: 'Toyota', model: 'Camry', year: 2022, price: 2350000, mileage: 42000, availability: 'available'};
const money = (cents: number) => (cents / 100).toLocaleString('en-US', {style: 'currency', currency: 'USD'});

function App() {
 const [config, setConfig] = useState<Config | null>(null);
 const [token, setToken] = useState(''), [email, setEmail] = useState(''), [password, setPassword] = useState('');
 const [cars, setCars] = useState<Car[]>([]), [car, setCar] = useState<Car | null>(null);
 const [facts, setFacts] = useState(blank), [description, setDescription] = useState('');
 const [message, setMessage] = useState(''), [busy, setBusy] = useState(false), [approved, setApproved] = useState(false);
 const [publicListing, setPublicListing] = useState<PublicListing | null>(null);
 const [question, setQuestion] = useState(''), [answer, setAnswer] = useState(''), [handoff, setHandoff] = useState(false);
 const [contact, setContact] = useState(''), [submittedQuestion, setSubmittedQuestion] = useState('');
 const [inbox, setInbox] = useState<Record<string, unknown>[]>([]), [diagnostics, setDiagnostics] = useState<unknown>(null);
 const lid = location.pathname.startsWith('/listing/') ? location.pathname.split('/')[2] : null;
 const dirty = !!car && (JSON.stringify(facts) !== JSON.stringify(car.facts) || description !== car.description);

 async function api(path: string, method = 'GET', body?: unknown) {
  const r = await fetch('/api' + path, {
   method, headers: {'Content-Type': 'application/json', ...(token ? {Authorization: 'Bearer ' + token} : {})},
   body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = await r.json();
  if (!r.ok) {
   const detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
   throw Error(detail + (r.status >= 500 && data.request_id ? ' (request ' + data.request_id + ')' : ''));
  }
  return data;
 }
 async function run(fn: () => Promise<void>) {
  setBusy(true); setMessage('');
  try { await fn(); } catch (e) { setMessage(e instanceof Error ? e.message : String(e)); }
  finally { setBusy(false); }
 }
 function select(c: Car) { setCar(c); setFacts(c.facts); setDescription(c.description); setApproved(false); }
 async function load() {
  const [savedCars, savedInbox] = await Promise.all([api('/listings'), api('/inquiries')]);
  setCars(savedCars); setInbox(savedInbox);
 }
 useEffect(() => { run(async () => {
  setConfig(await api('/config'));
  if (lid) setPublicListing(await api('/public/' + lid));
 }); }, []);
 useEffect(() => { if (token) run(load); }, [token]);
 async function save() {
  const saved = await api(car ? '/listings/' + car.id : '/listings', car ? 'PATCH' : 'POST', {
   facts, description, ...(car ? {expected_revision: car.revision} : {}),
  });
  select(saved); await load(); setMessage('Draft saved. Review the saved revision before publishing.'); return saved;
 }
 function signOut() {
  setToken(''); setCar(null); setCars([]); setInbox([]); setDiagnostics(null);
  setFacts(blank); setDescription(''); setApproved(false); setMessage('Signed out.');
 }
 const demo = config?.questionMode === 'demo';

 return <main>
  <header><a href="/">FrontDesk <strong>AI</strong></a><span>Dealership feasibility demo</span></header>
  {config && <p className="mode-banner">{demo
   ? 'Demo question mode · scripted matching of approved price and mileage · no AI or paid API calls'
   : 'Live AI mode · questions are processed by xAI'}</p>}
  <p role="status" aria-live="polite">{busy ? 'Working…' : message}</p>
  {lid ? publicListing ? <>
   <h1>{publicListing.facts.year} {publicListing.facts.make} {publicListing.facts.model}</h1>
   <p>{publicListing.description}</p>
   <h2>{money(publicListing.facts.price)} USD · {publicListing.facts.mileage.toLocaleString('en-US')} miles</h2>
   <p>{publicListing.facts.availability} · Approved revision {publicListing.revision}</p>
   <section>
    <h2>{demo ? 'Ask about this vehicle — demo' : 'Ask the AI assistant'}</h2>
    <p>{demo
     ? 'This demonstration uses fixed question matching, not AI. Try “Price?”, “Mileage?”, or “Price and mileage?”. Unknown questions go to staff.'
     : 'Questions are processed by xAI. Answers use approved price and mileage facts.'} Please do not include personal information in your question.</p>
    <label>Question<input value={question} maxLength={1000} onChange={e => {setQuestion(e.target.value); setHandoff(false); setAnswer('');}} /></label>
    <button disabled={busy || !question.trim()} onClick={() => run(async () => {
     const result = await api('/public/' + lid + '/questions', 'POST', {question});
     setAnswer(result.answer); setHandoff(result.handoff); setSubmittedQuestion(question);
    })}>Ask</button>
    <p aria-live="polite">{answer}</p>
    {handoff && <>
     <p>Voluntarily share contact details so Demo Motors staff can follow up. These details are saved in the staff inbox.</p>
     <label>Your email or phone<input value={contact} maxLength={300} onChange={e => setContact(e.target.value)} /></label>
     <button disabled={busy || contact.trim().length < 3} onClick={() => run(async () => {
      await api('/public/' + lid + '/inquiries', 'POST', {contact, message: submittedQuestion, request_key: crypto.randomUUID()});
      setMessage('Inquiry saved in the staff inbox.'); setHandoff(false); setContact('');
     })}>Submit inquiry to staff</button>
    </>}
   </section>
  </> : <section><h1>{busy ? 'Loading listing…' : 'Listing unavailable'}</h1><p>Only approved, published listings are public.</p></section>
  : !token ? <section>
   <h1>Your next listing starts here.</h1><p>Sign in with your verified demo owner account. After refreshing, sign in again to retrieve saved records.</p>
   <form onSubmit={e => {e.preventDefault(); run(async () => {
    if (!config?.supabaseUrl || !config.supabaseKey) throw Error('Supabase configuration is missing');
    const client = createClient(config.supabaseUrl, config.supabaseKey, {auth: {persistSession: false, autoRefreshToken: false, detectSessionInUrl: false}});
    const {data, error} = await client.auth.signInWithPassword({email, password});
    if (error) throw error;
    if (!data.session) throw Error('Sign-in did not return a session');
    setToken(data.session.access_token); setPassword('');
   });}}>
    <label>Email<input type="email" autoComplete="username" required value={email} onChange={e => setEmail(e.target.value)} /></label>
    <label>Password<input type="password" autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)} /></label>
    <button disabled={busy || !config}>Sign in</button>
   </form>
  </section> : <>
   <nav>
    <button onClick={signOut}>Sign out</button>
    <button disabled={busy} onClick={() => run(async () => {await load(); setMessage('Saved listings and inbox reloaded from the database.');})}>Reload saved records</button>
    <button disabled={busy} onClick={() => {setCar(null); setFacts(blank); setDescription(''); setApproved(false); setMessage('');}}>New car</button>
    <button disabled={busy} onClick={() => run(async () => setDiagnostics(await api('/diagnostics')))}>Owner diagnostics</button>
    <a href="/docs" target="_blank" rel="noreferrer">API docs</a>
   </nav>
   <div className="layout">
    <aside><h2>Saved listings</h2>{cars.length === 0 && <p>No saved listings loaded.</p>}{cars.map(c => <button disabled={busy} key={c.id} onClick={() => select(c)}>{c.facts.year} {c.facts.make} {c.facts.model}<br />{money(c.facts.price)} · {c.facts.mileage.toLocaleString('en-US')} miles<br />Revision {c.revision} · {c.published_revision === null ? 'private draft' : 'published'}</button>)}</aside>
    <section>
     <h1>{car ? 'Review your listing' : 'Create a car listing'}</h1>
     <p>Save a private draft, review its facts and manual description, then approve and publish.</p>
     {Object.entries(facts).map(([key, value]) => <label key={key}>{key === 'price' ? 'Price (USD cents — 2350000 = $23,500)' : key}
      {key === 'availability' ? <select value={value} onChange={e => {setFacts({...facts, availability: e.target.value}); setApproved(false);}}>
       {['available', 'reserved', 'sold'].map(s => <option key={s}>{s}</option>)}
      </select> : <input value={value} type={typeof value === 'number' ? 'number' : 'text'} onChange={e => {setFacts({...facts, [key]: typeof value === 'number' ? Number(e.target.value) : e.target.value}); setApproved(false);}} />}
     </label>)}
     <label>Manual description<textarea value={description} maxLength={3000} onChange={e => {setDescription(e.target.value); setApproved(false);}} /></label>
     <button disabled={busy} onClick={() => {
      setDescription(`${facts.year} ${facts.make} ${facts.model}. Listed at ${money(facts.price)} USD with ${facts.mileage.toLocaleString('en-US')} miles. Availability: ${facts.availability}.`);
      setApproved(false);
     }}>Fill manual description from current facts</button>
     <p>This button formats the facts above into text. It does not use AI.</p>
     <button disabled={busy} onClick={() => run(async () => {await save();})}>Save draft</button>
     {car && <>
      <button disabled={busy || !config?.aiEnabled} onClick={() => run(async () => {
       const saved = await save(); select(await api('/listings/' + saved.id + '/draft', 'POST', {expected_revision: saved.revision})); await load();
      })}>Generate description with Grok</button>
      {!config?.aiEnabled && <p>Grok drafting is disabled. Manual descriptions support the complete review and publish flow.</p>}
      <p>Saved revision {car.revision}. Published revision: {car.published_revision ?? 'none'}.</p>
      {dirty && <p>Unsaved changes: save this draft before approving. The public page keeps the previously published revision.</p>}
      <details><summary>Review saved database record</summary><pre>{JSON.stringify(car, null, 2)}</pre></details>
      <label><input type="checkbox" disabled={dirty || busy} checked={approved} onChange={e => setApproved(e.target.checked)} /> I reviewed the saved revision and approve these facts and description.</label>
      <button disabled={busy || dirty || !approved || !car.description.trim()} onClick={() => run(async () => {
       await api('/listings/' + car.id + '/publish', 'POST', {expected_revision: car.revision, confirm_approval: true});
       select(await api('/listings/' + car.id)); await load(); setMessage('Approved and published. Open the public listing to view the approved revision.');
      })}>Approve and publish saved revision</button>
      {car.published_revision !== null && <a href={'/listing/' + car.id} target="_blank" rel="noreferrer">Open public listing</a>}
      {car.published_revision !== null && <button disabled={busy} onClick={() => run(async () => {
       await api('/listings/' + car.id + '/unpublish', 'POST'); select(await api('/listings/' + car.id)); await load(); setMessage('Listing is private again.');
      })}>Unpublish</button>}
     </>}
    </section>
   </div>
   <section><h2>Staff inquiry inbox</h2>{inbox.length === 0 && <p>No inquiries loaded.</p>}{inbox.map(i => <article key={String(i.id)}>
    <p>{String(i.message)} · {String(i.contact)}</p><p>Listing: {String(i.listing_id)}</p>
    <select aria-label="Inquiry status" disabled={busy} value={String(i.status)} onChange={e => run(async () => {
     await api('/inquiries/' + i.id, 'PATCH', {status: e.target.value}); await load();
    })}>{['open', 'pending', 'resolved'].map(s => <option key={s}>{s}</option>)}</select>
   </article>)}</section>
   {diagnostics !== null && <section><h2>Owner diagnostics</h2><pre>{JSON.stringify(diagnostics, null, 2)}</pre></section>}
  </>}
 </main>;
}
createRoot(document.getElementById('root')!).render(<App />);
