import { useState } from 'react';
import { Api, Run, Car, Facts, blank, money, vehicleName, dollarsToCents, validateFacts } from './domain';
type Props = {
    stage: number;
    setStage: (n: number) => void;
    car: Car | null;
    api: Api;
    run: Run;
    busy: boolean;
    aiEnabled: boolean;
    refresh: () => Promise<void>;
    onSaved: (c: Car) => void;
    onDeleted: () => void;
    notify: (s: string) => void;
};
export default function ListingEditor({ stage, setStage, car, api, run, busy, aiEnabled, refresh, onSaved, onDeleted, notify }: Props) {
    const [facts, setFacts] = useState<Facts>(car?.facts || blank);
    const [price, setPrice] = useState(String((car?.facts.price ?? blank.price) / 100));
    const [description, setDescription] = useState(car?.description || '');
    const [featureText,setFeatureText]=useState((car?.facts.features || []).join(', '));
    const [approved, setApproved] = useState(false), [generating, setGenerating] = useState(false);
    const dirty = !car || JSON.stringify(facts) !== JSON.stringify(car.facts) || price !== String(car.facts.price / 100) || description !== car.description || featureText !== (car.facts.features || []).join(', ');
    function update(key: string, value: string) { setFacts({ ...facts, [key]: ['year', 'mileage'].includes(key) ? (value === '' ? NaN : Number(value)) : value }); setApproved(false); }
    function currentFacts() { const next = { ...facts, make: facts.make.trim(), model: facts.model.trim(), price: dollarsToCents(price), features:featureText.split(',').map(v=>v.trim()).filter(Boolean) }; validateFacts(next); return next; }
    async function saveDraft(updateSelection = true) {
        const next = currentFacts();
        if (car && !dirty)
            return car;
        const saved = await api(car ? '/listings/' + car.id : '/listings', car ? 'PATCH' : 'POST', { facts: next, description, ...(car ? { expected_revision: car.revision } : {}) });
        if (updateSelection)
            onSaved(saved);
        await refresh();
        return saved as Car;
    }
    return <div className="editor">
  <div className="section-heading"><div><p className="eyebrow">Listing workspace</p><h2>{car ? vehicleName(car.facts) : 'New listing'}</h2></div><span className={'badge ' + (car?.published_revision ? 'green' : '')}>{car?.published_revision ? 'Published' : 'Draft'}</span></div>
  <div className="stage-nav" aria-label="Listing stages">{['Vehicle details', 'AI description', 'Review and publish'].map((name, i) => <button key={name} disabled={busy} aria-current={stage === i + 1 ? 'step' : undefined} onClick={() => setStage(i + 1)}><span className="step">{i + 1}</span>{name}</button>)}</div>
  <section hidden={stage !== 1} className="stage"><h3><span className="step">1</span>Vehicle details</h3><p>Enter the facts customers can rely on. Prices are in US dollars.</p>
   <div className="field-grid">
    <label>Make<input value={facts.make} maxLength={80} onChange={e => update('make', e.target.value)}/></label>
    <label>Model<input value={facts.model} maxLength={80} onChange={e => update('model', e.target.value)}/></label>
    <label>Year<input type="number" min={1886} max={new Date().getFullYear() + 1} value={Number.isNaN(facts.year) ? '' : facts.year} onChange={e => update('year', e.target.value)}/></label>
    <label>Price (USD)<input aria-label="Price (USD)" inputMode="decimal" value={price} onChange={e => { setPrice(e.target.value); setApproved(false); }} aria-describedby="price-help"/><small id="price-help">For example, 23500 means $23,500.</small></label>
    <label>Mileage (miles)<input type="number" min={0} max={10000000} step={1} value={Number.isNaN(facts.mileage) ? '' : facts.mileage} onChange={e => update('mileage', e.target.value)}/></label>
    <label>Availability<select value={facts.availability} onChange={e => update('availability', e.target.value)}>{['available', 'reserved', 'sold'].map(v => <option key={v}>{v}</option>)}</select></label>
    {([['body_style', 'Body style', ['sedan','suv','hatchback','truck','coupe','wagon','van']], ['fuel_type','Fuel type',['gasoline','diesel','hybrid','electric','plug_in_hybrid']], ['drivetrain','Drivetrain',['fwd','rwd','awd','4wd']], ['transmission','Transmission',['automatic','manual']]] as const).map(([key,label,options]) => <label key={key}>{label}<select value={facts[key] || ''} onChange={e => { setFacts({...facts,[key]:e.target.value || null}); setApproved(false); }}><option value="">Not provided</option>{options.map(v => <option key={v} value={v}>{v.replaceAll('_',' ').toUpperCase()}</option>)}</select></label>)}
    {([['seats','Seats',1,15],['mpg_combined','Documented combined MPG',1,150],['cargo_cubic_feet','Cargo space (cubic feet)',1,500]] as const).map(([key,label,min,max]) => <label key={key}>{label}<input type="number" min={min} max={max} step={key === 'seats' ? 1 : 'any'} value={facts[key] ?? ''} onChange={e => {setFacts({...facts,[key]:e.target.value === '' ? null : Number(e.target.value)});setApproved(false);}}/><small>Leave blank when unknown. Enter documented values only.</small></label>)}
    <label className="full-width">Documented features<input value={featureText} placeholder="For example: heated seats, rear camera" maxLength={1000} onChange={e => {setFeatureText(e.target.value);setApproved(false);}}/><small>Comma-separated. These facts become available for comparison only after publication.</small></label>
   </div>
   <button disabled={busy} onClick={() => run(async () => { await saveDraft(); setStage(2); notify('Private draft saved. Review its saved revision before publishing.'); })}>Save vehicle details</button>
  </section>
  <section hidden={stage !== 2} className="stage"><h3><span className="step">2</span>AI description</h3><p>Grok drafts from your facts. You review the wording and decide what goes public.</p>
   <div className="actions"><button className="primary" disabled={busy || !aiEnabled} onClick={() => run(async () => {
            currentFacts();
            setGenerating(true);
            try {
                const saved = await saveDraft(false);
                const result = await api('/listings/' + saved.id + '/draft', 'POST', { expected_revision: saved.revision });
                onSaved(result);
                await refresh();
                notify('Grok description saved as a private draft. Review or edit it before publishing.');
            }
            catch {
                throw Error('Grok could not finish the draft. Your saved listing is safe. Try the free formatter or retry later.');
            }
            finally {
                setGenerating(false);
            }
        })}>{generating ? 'Grok is drafting…' : 'Generate with Grok'}</button>
   <button disabled={busy} onClick={() => run(async () => { const f = currentFacts(); setDescription(`${vehicleName(f)}. Listed at ${money(f.price)} USD with ${f.mileage.toLocaleString()} miles. Availability: ${f.availability}.`); setApproved(false); notify('Formatted from entered facts without AI. Save the description when ready.'); })}>Format facts without AI</button></div>
   <small>Each Grok click can make one paid API request. The formatter is free and does not use AI.</small>
   {!aiEnabled && <p>Grok drafting is unavailable. You can still write or format a description.</p>}
   <label>Listing description<textarea value={description} maxLength={3000} onChange={e => { setDescription(e.target.value); setApproved(false); }}/></label>
   <button disabled={busy} onClick={() => run(async () => { await saveDraft(); setStage(3); notify('Description saved. Review the saved revision below.'); })}>Save description</button>
  </section>
  <section hidden={stage !== 3} className="stage review"><h3><span className="step">3</span>Review and publish</h3>
   {car ? <><p><strong>Saved revision {car.revision}</strong><span className="separator">·</span>Public revision {car.published_revision ?? 'none'}</p>
    <div className="saved-summary"><h4>{vehicleName(car.facts)}</h4><p>{money(car.facts.price)} USD · {car.facts.mileage.toLocaleString()} miles · {car.facts.availability}</p><p>{car.description || 'Save a description before publishing.'}</p></div>
    {dirty && <p className="notice">You have unsaved changes. Save them before approving. Customers still see the previously published revision.</p>}
    <label className="checkbox"><input type="checkbox" checked={approved} disabled={busy || dirty} onChange={e => setApproved(e.target.checked)}/>I reviewed the saved revision and approve these facts and description.</label>
    <div className="actions"><button className="primary" disabled={busy || dirty || !approved || !car.description.trim()} onClick={() => run(async () => {
                await api('/listings/' + car.id + '/publish', 'POST', { expected_revision: car.revision, confirm_approval: true });
                onSaved(await api('/listings/' + car.id));
                await refresh();
                notify('Approved revision published. Customers can now see it.');
            })}>Publish approved revision</button>
    {car.published_revision !== null && <a className="button primary" target="_blank" rel="noreferrer" href={'/listing/' + car.id}>View public page ↗</a>}</div>
   </> : <p>Save a private listing first. Its exact saved revision will appear here for approval.</p>}
  </section>
  {car && <details className="danger-zone"><summary>Listing management</summary><p>Unpublish hides this listing. Delete permanently removes its saved facts, public page, inquiries and linked AI history.</p><div className="actions">
   {car.published_revision !== null && <button disabled={busy} onClick={() => run(async () => { await api('/listings/' + car.id + '/unpublish', 'POST'); onSaved(await api('/listings/' + car.id)); await refresh(); notify('Listing unpublished.'); })}>Unpublish</button>}
   <button className="danger" disabled={busy} onClick={() => { if (window.confirm(`Delete ${vehicleName(car.facts)} permanently? Its inquiries and linked AI history will also be deleted.`))
            run(async () => { await api('/listings/' + car.id, 'DELETE'); onDeleted(); await refresh(); notify('Listing deleted.'); }); }}>Delete listing</button>
  </div></details>}
 </div>;
}
