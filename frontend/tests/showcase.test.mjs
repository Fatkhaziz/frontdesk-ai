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
 await click(button('Find my fit'));await click(button('I have $25,000 and commute every day. What should I consider?'));
 assert.equal(calls.length,1);assert.equal(field('Your message').value.includes('$25,000'),true);
 assert.equal(document.querySelectorAll('.inventory-card').length,0);
 await click(button('Inventory'));assert.equal(document.querySelectorAll('.inventory-card').length,2);
 assert.equal(calls.length,1);
});

test('multi-turn AI preferences persist and send is explicit',async()=>{
 const calls=[];const api=async(path,method,body)=>{calls.push({path,method,body});if(!method)return inventory;return {preferences:{...prefs,budget_cents:2500000,budget_kind:'vehicle'},answer:'Compare the available choices.',follow_up:'How many passengers?',recommended_ids:[],matches:['a'],sources:[],mode:'live_ai'};};
 await act(async()=>root.render(h(PublicShop,{key:'chat',id:'a',api,config})));
 await click(button('Find my fit'));await fill(field('Your message'),'My budget is $25,000.');await submit(field('Your message').closest('form'));
 assert.equal(field('Maximum budget (USD)').value,'25000');
 await fill(field('Your message'),'I need 5 seats.');await submit(field('Your message').closest('form'));
 const sends=calls.filter(c=>c.path.endsWith('/assist'));assert.equal(sends.length,2);assert.equal(sends[1].body.preferences.budget_cents,2500000);assert.equal(sends[1].body.history.length,2);
});

test('owner AI suggestions stay unsaved and cannot publish without approval',async()=>{
 const calls=[];const api=async(path,method,body)=>{calls.push({path,method,body});if(path.endsWith('/suggest'))return {questions:[{question:'What warranty applies?',reason:'No warranty was supplied.'}]};return {revision:0,published_revision:null,cards:[]};};
 const run=async(fn)=>fn();
 await act(async()=>root.render(h(KnowledgeSetup,{key:'knowledge',api,run,busy:false,notify:()=>{},businessId:'a'})));
 await click(button('Suggest customer questions with AI'));
 assert.equal(field('Customer question').value,'What warranty applies?');assert.equal(field('Owner-provided answer').value,'');
 assert.equal(button('Publish reviewed knowledge').disabled,true);assert.equal(calls.filter(c=>c.method==='PUT'||c.path.endsWith('/publish')).length,0);
});
