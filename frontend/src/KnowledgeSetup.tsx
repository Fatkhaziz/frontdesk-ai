import { useEffect, useState } from 'react';
import { Api, Run } from './domain';

type Card = { id: string; question: string; answer: string; source_note: string; status: 'draft'|'approved'|'staff'|'ignored'; reason: string };
type State = { revision: number; published_revision: number|null; cards: Card[] };
export default function KnowledgeSetup({api, run, busy, notify, businessId}:{api:Api;run:Run;busy:boolean;notify:(s:string)=>void;businessId:string}) {
    const [saved,setSaved]=useState<State|null>(null),[cards,setCards]=useState<Card[]>([]),[approved,setApproved]=useState(false),[error,setError]=useState('');
    const dirty=!!saved && JSON.stringify(cards)!==JSON.stringify(saved.cards);
    useEffect(()=>{api('/dealer/knowledge').then(s=>{setSaved(s);setCards(s.cards);}).catch(()=>setError('Knowledge setup could not load. Check migrations and owner access.'));},[]);
    function change(id:string,patch:Partial<Card>){setCards(cs=>cs.map(c=>c.id===id?{...c,...patch}:c));setApproved(false);}
    return <section className="knowledge"><div className="section-heading"><div><p className="eyebrow">Prepare your receptionist</p><h1>Owner knowledge</h1><p className="muted">AI suggests what customers may ask. You supply the answers and decide what goes public.</p></div><a className="button" href={'/shop/'+businessId} target="_blank" rel="noreferrer">Open customer inventory ↗</a></div>
      {error && <p role="alert" className="notice">{error}</p>}
      <ol className="workflow-strip"><li>Generate useful questions</li><li>Answer or route to staff</li><li>Review and publish</li></ol>
      <div className="actions"><button className="primary" disabled={busy || !saved || dirty || cards.length>=30} onClick={()=>run(async()=>{
        const result=await api('/dealer/knowledge/suggest','POST',{expected_revision:saved!.revision});
        const existing=new Set(cards.map(c=>c.question.toLowerCase().trim()));
        const next=result.questions.filter((q:any)=>!existing.has(q.question.toLowerCase().trim())).map((q:any)=>({id:crypto.randomUUID(),question:q.question,answer:'',source_note:'',status:'draft' as const,reason:q.reason}));
        setCards(cs=>[...cs,...next].slice(0,30));setApproved(false);notify('AI question suggestions are private and unsaved. Review, answer and save them.');
      })}>{busy ? 'Working…' : 'Suggest customer questions with AI'}</button><button disabled={busy || !saved || cards.length>=30} onClick={()=>{setCards(cs=>[...cs,{id:crypto.randomUUID(),question:'',answer:'',source_note:'',status:'draft',reason:''}]);setApproved(false);}}>+ Add a question</button></div>
      <p className="muted">Suggestions use one paid request. Save edits before generating more. No AI-generated answer or policy is published automatically.</p>
      {saved && <p className="revision-note">Private revision {saved.revision} · Published revision {saved.published_revision ?? 'none'} {dirty && '· Unsaved changes'}</p>}
      {!cards.length && <div className="empty"><h3>What will customers want to know?</h3><p>Generate suggestions or add your own question. Missing policies should be marked for staff.</p></div>}
      <div className="knowledge-cards">{cards.map((c,index)=><article className="knowledge-card" key={c.id}><div className="section-heading"><h3>Question {index+1}</h3><button disabled={busy} onClick={()=>{setCards(cs=>cs.filter(v=>v.id!==c.id));setApproved(false);}}>Remove</button></div>
        {c.reason && <p className="suggestion-reason">Why this matters: {c.reason}</p>}
        <label>Customer question<input value={c.question} maxLength={200} onChange={e=>change(c.id,{question:e.target.value})}/></label>
        <label>How should the receptionist handle it?<select value={c.status} onChange={e=>change(c.id,{status:e.target.value as Card['status']})}><option value="draft">Draft — keep private</option><option value="approved">Approved answer — publish after review</option><option value="staff">Staff must answer — publish this boundary</option><option value="ignored">Not relevant — keep private</option></select></label>
        <label>Owner-provided answer<textarea value={c.answer} maxLength={1200} placeholder="Enter your actual policy or approved information." onChange={e=>change(c.id,{answer:e.target.value,status:c.status==='approved'?'draft':c.status})}/></label>
        <label>Source or reference (optional)<input value={c.source_note} maxLength={200} placeholder="For example: owner-approved warranty policy, section 2" onChange={e=>change(c.id,{source_note:e.target.value})}/><small>A reference label records your source. It does not upload or independently verify a document.</small></label>
      </article>)}</div>
      <div className="publish-panel"><button disabled={busy || !saved || !dirty} onClick={()=>run(async()=>{
        if(cards.some(c=>c.question.trim().length<3))throw Error('Enter a question of at least three characters.');
        if(cards.some(c=>c.status==='approved'&&!c.answer.trim()))throw Error('An approved answer cannot be blank.');
        const result=await api('/dealer/knowledge','PUT',{expected_revision:saved!.revision,cards});setSaved(result);setCards(result.cards);setApproved(false);notify('Private knowledge saved. Review it before publication.');
      })}>Save private knowledge</button>
      <label className="checkbox"><input type="checkbox" checked={approved} disabled={busy || dirty || !saved?.revision} onChange={e=>setApproved(e.target.checked)}/>I reviewed the saved answers and staff-only boundaries for publication.</label>
      <button className="primary" disabled={busy || !saved?.revision || dirty || !approved} onClick={()=>run(async()=>{const r=await api('/dealer/knowledge/publish','POST',{expected_revision:saved!.revision,confirm_approval:true});setSaved(r);setCards(r.cards);setApproved(false);notify('Reviewed knowledge published. Draft and ignored questions remain private.');})}>Publish reviewed knowledge</button></div>
    </section>;
}
