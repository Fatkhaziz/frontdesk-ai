import {test} from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
const dom=new JSDOM('<div id="root"></div>',{url:'http://localhost/'});
for(const k of ['window','document','HTMLElement','HTMLInputElement','HTMLTextAreaElement','HTMLSelectElement','Event','MouseEvent'])globalThis[k]=dom.window[k];
HTMLElement.prototype.scrollIntoView=function(){};
globalThis.IS_REACT_ACT_ENVIRONMENT=true;
const {createElement:h,act}=await import('react');
const {createRoot}=await import('react-dom/client');
const {default:PublicShop}=await import('../src/PublicShop.tsx');
const {default:KnowledgeSetup}=await import('../src/KnowledgeSetup.tsx');
const {default:SystemStatus}=await import('../src/SystemStatus.tsx');
const root=createRoot(document.getElementById('root'));
const prefs={budget_cents:null,budget_kind:'unknown',min_seats:null,max_mileage:null,body_style:'any',fuel_type:'any',drivetrain:'any',priorities:[],required_features:[]};
const inventory={name:'Test Motors',knowledge:[],listings:[{id:'a',revision:1,facts:{make:'Example',model:'A',year:2022,price:2350000,mileage:42000,availability:'available'},description:'Synthetic'},{id:'b',revision:1,facts:{make:'Example',model:'B',year:2022,price:2650000,mileage:38000,availability:'available'},description:'Synthetic'}]};
const config={questionMode:'ai',aiEnabled:true,shoppingAiEnabled:true,supabaseUrl:'',supabaseKey:''};
const button=name=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===name);
const field=name=>[...document.querySelectorAll('label')].find(l=>{const c=l.cloneNode(true);c.querySelectorAll('input,textarea,select,small').forEach(e=>e.remove());return c.textContent.trim()===name;})?.querySelector('input,textarea,select');
async function click(e){assert.ok(e);await act(async()=>e.click());}
async function fill(e,value){assert.ok(e);await act(async()=>{const proto=e instanceof HTMLTextAreaElement?HTMLTextAreaElement.prototype:e instanceof HTMLSelectElement?HTMLSelectElement.prototype:HTMLInputElement.prototype;Object.getOwnPropertyDescriptor(proto,'value').set.call(e,value);e.dispatchEvent(new Event(e.tagName==='SELECT'?'change':'input',{bubbles:true}));});}
async function submit(form){await act(async()=>form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})));}

test('inventory and navigation never make an automatic paid request',async()=>{
 const calls=[];const api=async(path,method,body)=>{calls.push({path,method,body});return inventory;};
 await act(async()=>root.render(h(PublicShop,{key:'inventory',id:'a',api,config})));
 await click(button('AI chat'));await fill(field('Your message'),'I have $25,000 and commute every day.');
 assert.equal(calls.length,1);assert.equal(field('Your message').value.includes('$25,000'),true);
 assert.equal(document.querySelectorAll('.inventory-card').length,0);
 await click(button('Inventory'));assert.equal(document.querySelectorAll('.inventory-card').length,2);
 assert.equal(calls.length,1);
});

test('system status shows bounded rejection diagnostics and honestly marks older evidence',async()=>{
 const calls=[];
 const api=async(path)=>{calls.push(path);return path==='/diagnostics'
  ? {auth:'ready',database:'connected',drafting:'ready',question_mode:'ai',backend:'running',ai_calls_used:12,ai_call_limit:17}
  : [{task_id:'new',operation:'shopping_assistant',application_outcome:'invalid_output',provider_outcome:'succeeded',rejection:{stage:'claims',reason:'unsupported_number',field:'answer',source_id:null}},
     {task_id:'old',operation:'shopping_assistant',application_outcome:'invalid_output',provider_outcome:'succeeded',rejection:null}];};
 await act(async()=>root.render(h(SystemStatus,{key:'rejections',api})));
 assert.match(document.body.textContent,/12 used \/ 17 total/);
 assert.match(document.body.textContent,/Rejected at claims: unsupported_number · field answer/);
 assert.match(document.body.textContent,/Specific rejection diagnostics were not recorded for this request/);
 assert.deepEqual(calls.sort(),['/assistant/evidence','/diagnostics']);
});

test('multi-turn AI preferences persist and send is explicit',async()=>{
 const calls=[];const api=async(path,method,body)=>{calls.push({path,method,body});if(!method)return inventory;return {preferences:{...prefs,budget_cents:2500000,budget_kind:'vehicle'},answer:'Compare the available choices.',follow_up:'How many passengers?',recommended_ids:[],matches:['a'],sources:[],mode:'live_ai'};};
 await act(async()=>root.render(h(PublicShop,{key:'chat',id:'a',api,config})));
 await click(button('AI chat'));await fill(field('Your message'),'My budget is $25,000.');await submit(field('Your message').closest('form'));
 assert.equal(field('Maximum budget (USD)').value,'25000');
 await fill(field('Your message'),'I need 5 seats.');await submit(field('Your message').closest('form'));
 const sends=calls.filter(c=>c.path.endsWith('/assist'));assert.equal(sends.length,2);assert.equal(sends[1].body.preferences.budget_cents,2500000);assert.equal(sends[1].body.history.length,2);
});

test('the chat shows the current message while waiting and displays the delivered reply',async()=>{
 const calls=[];let finish;
 const api=async(path,method,body)=>{calls.push({path,method,body});if(!method)return inventory;return new Promise(resolve=>{finish=resolve;});};
 await act(async()=>root.render(h(PublicShop,{key:'limited-chat',id:'a',api,config})));
 await click(button('AI chat'));await fill(field('Your message'),'My vehicle budget is $25,000.');await submit(field('Your message').closest('form'));
 assert.match(document.querySelector('[role="log"]').textContent,/My vehicle budget is \$25,000.*Thinking/s);
 assert.equal(button('Send to AI').disabled,true);
 await act(async()=>finish({preferences:{...prefs,budget_cents:2500000,budget_kind:'vehicle'},answer:'I’d prioritize the lower asking price for your commute.',follow_up:'Which features are required?',recommended_ids:[],matches:['a'],sources:[],answer_mode:'partial_ai_explanation',mode:'live_ai'}));
 assert.match(document.querySelector('[role="log"]').textContent,/I’d prioritize the lower asking price for your commute/);
 assert.match(document.querySelector('[role="log"]').textContent,/Some details could not be verified/);
 assert.equal(field('Maximum budget (USD)').value,'25000');
 assert.equal(calls.filter(c=>c.path.endsWith('/assist')).length,1);
 await act(async()=>root.render(h(SystemStatus,{key:'limited-evidence',api:async(path)=>path==='/diagnostics'?{auth:'ready',database:'connected'}:[{task_id:'limited',operation:'shopping_assistant',application_outcome:'accepted_with_limits',provider_outcome:'succeeded',source_ids:['listing:a:r1:price'],rejection:{stage:'sources',reason:'unapproved_source',field:'answer'}}]})));
 assert.match(document.body.textContent,/AI wording omitted at sources: unapproved_source · field answer/);
 assert.doesNotMatch(document.body.textContent,/Rejected at sources/);
});

test('owner AI suggestions stay unsaved and cannot publish without approval',async()=>{
 const calls=[];const api=async(path,method,body)=>{calls.push({path,method,body});if(path.endsWith('/suggest'))return {questions:[{question:'What warranty applies?',reason:'No warranty was supplied.'}]};return {revision:0,published_revision:null,cards:[]};};
 const run=async(fn)=>fn();
 await act(async()=>root.render(h(KnowledgeSetup,{key:'knowledge',api,run,busy:false,notify:()=>{},businessId:'a'})));
 await click(button('Suggest customer questions with AI'));
 assert.equal(field('Customer question').value,'What warranty applies?');assert.equal(field('Owner-provided answer').value,'');
 assert.equal(button('Publish reviewed knowledge').disabled,true);assert.equal(calls.filter(c=>c.method==='PUT'||c.path.endsWith('/publish')).length,0);
});

test('explicit answer review saves approval and later edits keep the published answer separate',async()=>{
 let state={revision:0,published_revision:null,cards:[]},published=[];const calls=[];
 const api=async(path,method,body)=>{
  calls.push({path,method,body});
  if(method==='PUT')state={...state,revision:state.revision+1,cards:structuredClone(body.cards)};
  if(path.endsWith('/publish')){published=structuredClone(state.cards);state={...state,published_revision:state.revision};}
  return structuredClone(state);
 };
 await act(async()=>root.render(h(KnowledgeSetup,{key:'explicit-review',api,run:async(fn)=>fn(),busy:false,notify:()=>{},businessId:'a'})));
 await click(button('+ Add a question'));assert.equal(button('Approve this answer').disabled,true);
 await fill(field('Customer question'),'Are these examples fictional?');await fill(field('Owner-provided answer'),'These are fictional demonstration vehicles.');
 await click(button('Approve this answer'));assert.equal(field('How should the receptionist handle it?').value,'approved');
 await click(button('Save private knowledge'));assert.equal(state.cards[0].status,'approved');assert.equal(published.length,0);
 assert.equal(button('Publish reviewed knowledge').disabled,true);
 await click(document.querySelector('.publish-panel input[type="checkbox"]'));await click(button('Publish reviewed knowledge'));
 assert.equal(published[0].answer,'These are fictional demonstration vehicles.');
 await fill(field('Owner-provided answer'),'Private edit for later review.');assert.equal(field('How should the receptionist handle it?').value,'draft');
 assert.equal(button('Publish reviewed knowledge').disabled,true);await click(button('Save private knowledge'));
 assert.equal(state.revision,2);assert.equal(state.published_revision,1);assert.equal(published[0].answer,'These are fictional demonstration vehicles.');
 assert.equal(calls.filter(c=>c.path.endsWith('/publish')).length,1);
});

test('Find my fit carries selected vehicles and staff submission never displays AI activity',async()=>{
 const calls=[];let finishInquiry;
 const api=async(path,method,body)=>{
  calls.push({path,method,body});if(!method)return inventory;
  if(path.endsWith('/inquiries'))return new Promise(resolve=>{finishInquiry=resolve;});
  return {preferences:prefs,answer:'These are the selected examples.',follow_up:'What matters most?',recommended_ids:[],matches:[],sources:[],mode:'live_ai'};
 };
 await act(async()=>root.render(h(PublicShop,{key:'selected-handoff',id:'a',api,config})));
 for(const input of document.querySelectorAll('.inventory-card input[type="checkbox"]'))await click(input);
 await click(button('AI chat'));await fill(field('Your message'),'Compare my selected vehicles.');await submit(field('Your message').closest('form'));
 assert.deepEqual(calls.find(c=>c.path.endsWith('/assist')).body.selected_ids,['a','b']);
 await click(button('Ask staff to follow up'));await fill(field('Email or phone for follow-up'),'class-test@example.invalid');
 await click(document.querySelector('.staff-help input[type="checkbox"]'));await submit(field('Email or phone for follow-up').closest('form'));
 assert.equal(typeof finishInquiry,'function');assert.equal(button('Send inquiry to staff').disabled,true);
 assert.equal(button('Thinking…'),undefined);assert.equal(document.body.textContent.includes('Checking published information…'),false);
 assert.equal(calls.filter(c=>c.path.endsWith('/assist')).length,1);
 assert.deepEqual(calls.find(c=>c.path.endsWith('/inquiries')).body.listing_ids,['a','b']);
 await act(async()=>finishInquiry({id:'synthetic-inquiry',status:'open'}));
 assert.equal(document.body.textContent.includes('Inquiry saved in the staff inbox.'),true);
});
