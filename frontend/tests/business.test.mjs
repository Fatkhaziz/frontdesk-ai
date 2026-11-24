import { test } from 'node:test';
import assert from 'node:assert/strict';
import { JSDOM } from 'jsdom';

const dom = new JSDOM('<!doctype html><div id="root"></div>', { url: 'http://localhost/' });
for (const key of ['window', 'document', 'HTMLElement', 'HTMLInputElement', 'HTMLTextAreaElement', 'HTMLSelectElement', 'Event', 'MouseEvent']) globalThis[key] = dom.window[key];
globalThis.IS_REACT_ACT_ENVIRONMENT = true;
const { createElement: h, act } = await import('react');
const { createRoot } = await import('react-dom/client');
const { default: PublicBusiness } = await import('../src/PublicBusiness.tsx');
const { default: BusinessSettings } = await import('../src/BusinessSettings.tsx');
const { exampleProfile } = await import('../src/business.ts');
const root = createRoot(document.getElementById('root'));
const text = () => document.body.textContent;
const button = name => [...document.querySelectorAll('button')].find(b => b.textContent.trim() === name);
const field = name => [...document.querySelectorAll('label')].find(label => {
  const copy = label.cloneNode(true);
  copy.querySelectorAll('input,textarea,select').forEach(control => control.remove());
  return copy.textContent.trim() === name;
})?.querySelector('input,textarea,select');
async function click(element) { assert.ok(element); await act(async () => element.click()); }
async function fill(element, value) {
  assert.ok(element);
  await act(async () => {
    const prototype = element instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : element instanceof HTMLSelectElement ? HTMLSelectElement.prototype : HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(prototype, 'value').set.call(element, value);
    element.dispatchEvent(new Event(element.tagName === 'SELECT' ? 'change' : 'input', { bubbles: true }));
  });
}
async function submit(form) { await act(async () => form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))); }

test('public business form uses its own service questions and preserves a retry key after a failed save', async () => {
  const profile = { ...exampleProfile('Demo Salon', 'salon'), revision: 2 };
  const calls = [];
  let fail = true;
  const api = async (path, method, body) => {
    calls.push({ path, method, body });
    if (!method) return profile;
    if (path.endsWith('/questions')) return { answer: 'Please ask our staff.', handoff: true };
    if (fail) { fail = false; throw Error('Connection interrupted. Please try again.'); }
    return { id: 'saved-inquiry' };
  };
  await act(async () => root.render(h(PublicBusiness, { id: 'salon', api })));
  assert.match(text(), /Demo Salon/);
  await fill(field('Service'), profile.services[0].id);
  const question = profile.services[0].questions[0];
  assert.ok(field(question.label + ' (required)'));
  assert.ok(!field('What is the year, make and model of your vehicle? (required)'));
  await fill(field(question.label + ' (required)'), 'Any stylist');
  await fill(field('Message'), 'Haircut inquiry');
  await fill(field('Your email or phone'), 'customer@example.invalid');
  const inquiryForm = field('Message').closest('form');
  await submit(inquiryForm);
  assert.match(text(), /Connection interrupted/);
  assert.doesNotMatch(text(), /Your inquiry is saved/);
  await submit(inquiryForm);
  const saves = calls.filter(c => c.path.endsWith('/inquiries'));
  assert.equal(saves.length, 2);
  assert.equal(saves[0].body.request_key, saves[1].body.request_key);
  assert.equal(saves[1].body.expected_revision, 2);
  assert.deepEqual(saves[1].body.answers, { [question.id]: 'Any stylist' });
  assert.match(text(), /Your inquiry is saved/);
  assert.match(text(), /No appointment has been reserved/);
  assert.equal(field('Message').value, '');
  await fill(field('Your question'), 'Unknown policy?');
  await submit(field('Your question').closest('form'));
  assert.equal(field('Message').value, 'Unknown policy?');
  assert.equal(calls.filter(c => c.path.endsWith('/inquiries')).length, 2);
  await act(async () => root.render(null));
});

test('owners must save changed settings and approve the saved revision before publication; staff cannot edit', async () => {
  let workspace = { id: 'salon', name: 'Demo Salon', role: 'owner', revision: 1, profile: exampleProfile('Demo Salon', 'salon'), published_revision: 1 };
  const calls = [], notices = [];
  const props = {
    busy: false,
    api: async (path, method, body) => {
      calls.push({ path, method, body });
      if (path === '/business/profile') workspace = { ...workspace, profile: body.profile, revision: workspace.revision + 1 };
    },
    run: fn => fn(),
    notify: message => notices.push(message),
    refresh: async () => { root.render(h(BusinessSettings, { ...props, workspace })); },
  };
  await act(async () => root.render(h(BusinessSettings, { ...props, workspace })));
  assert.equal(button('Publish approved settings').disabled, true);
  await fill(field('Business name'), 'Updated Salon');
  assert.equal(document.querySelector('input[type=checkbox]:disabled') !== null, true);
  await click(button('Save private settings'));
  assert.equal(calls[0].body.expected_revision, 1);
  assert.equal(calls[0].body.profile.name, 'Updated Salon');
  const approval = [...document.querySelectorAll('label')].find(l => l.textContent.includes('I reviewed the saved settings')).querySelector('input');
  await click(approval);
  assert.equal(button('Publish approved settings').disabled, false);
  await click(button('Publish approved settings'));
  assert.equal(calls[1].body.expected_revision, 2);
  assert.equal(calls[1].body.confirm_approval, true);
  assert.match(notices.join(' '), /Approved business settings published/);
  await fill(field('Price in USD, blank for staff quote'), '1.001');
  assert.equal(button('Save private settings').disabled, true);
  assert.equal(button('Publish approved settings').disabled, true);
  workspace = { ...workspace, role: 'staff' };
  await act(async () => root.render(h(BusinessSettings, { ...props, workspace })));
  assert.equal(field('Business name').matches(':disabled'), true);
  assert.equal(button('Save private settings').matches(':disabled'), true);
  await act(async () => root.render(null));
});

test('business Q&A shows mode, published evidence and handoff without submitting an inquiry', async () => {
  const profile = { ...exampleProfile('Demo Studio', 'photography_studio'), revision: 3 };
  let result = { answer: 'A portrait session takes 60 minutes.', handoff: false, mode: 'live_ai', revision: 3,
    sources: [{ id: 'studio:r3:duration', label: 'Portrait session duration', revision: 3, text: 'A portrait session takes 60 minutes.' }] };
  let inquiries = 0;
  const api = async (path, method) => {
    if (!method) return profile;
    if (path.endsWith('/inquiries')) { inquiries++; return {}; }
    return result;
  };
  await act(async () => root.render(h(PublicBusiness, { id: 'studio', api })));
  assert.match(text(), /Photography studio/);
  await fill(field('Your question'), 'How long would a portrait take?');
  await submit(field('Your question').closest('form'));
  assert.match(text(), /Live AI · checked published evidence/);
  assert.match(text(), /Portrait session duration · revision 3/);
  assert.equal(document.querySelector('blockquote').textContent, result.sources[0].text);
  result = { answer: 'Please send an inquiry.', handoff: true, mode: 'error', revision: 3, reason: 'stale_source', sources: [] };
  await submit(field('Your question').closest('form'));
  assert.match(text(), /Error · answer unavailable/);
  assert.equal(document.querySelectorAll('blockquote').length, 0);
  assert.equal(inquiries, 0);
  assert.equal(field('Message').value, 'How long would a portrait take?');
  await act(async () => root.render(null));
});
