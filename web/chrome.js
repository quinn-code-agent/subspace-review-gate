/* Browser interaction only. Transport remains portable Annotation + feedback-only Relay Result. */
const $ = (id) => document.getElementById(id);
const state = { comments: [], quote: '', draftRange: null, savedRanges: [], identityKey: 'subspace-reviewer-name-v1' };
const esc = (s) => { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; };
const identity = (name) => {
  const slug = name.trim().toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9._@-]/g, '');
  return slug ? `person:${slug}` : '';
};
function currentIdentity() { return identity(localStorage.getItem(state.identityKey) || ''); }
function renderIdentity() {
  const name = localStorage.getItem(state.identityKey) || 'Not set';
  $('identity-chip').innerHTML = `<i class="identity-dot"></i><div><div class="identity-name">${esc(name)}</div><div class="identity-portable">${esc(currentIdentity() || 'person:<name>')}</div></div><button class="change" id="identity-edit">Change</button>`;
  $('identity-edit').onclick = showIdentity;
}
function showIdentity() { $('identity-cover').hidden = false; $('identity-name').value = localStorage.getItem(state.identityKey) || ''; }
function setIdentity(name) { if (!identity(name)) return; localStorage.setItem(state.identityKey, name.trim()); $('identity-cover').hidden = true; renderIdentity(); }
function clearDraft() { CSS.highlights?.delete('subspace-draft'); state.draftRange = null; }
function paintSaved() { if (!CSS.highlights) return; CSS.highlights.delete('subspace-saved'); if (state.savedRanges.length) CSS.highlights.set('subspace-saved', new Highlight(...state.savedRanges)); }
function closeCompose() { clearDraft(); $('compose').hidden = true; $('mobile-compose').hidden = true; }
function openCompose() {
  const s = getSelection(); const range = s.rangeCount ? s.getRangeAt(0).cloneRange() : null;
  if (!range || !s.toString().trim() || !$('artifact').contains(range.commonAncestorContainer)) return;
  state.quote = s.toString().trim(); state.draftRange = range; CSS.highlights?.set('subspace-draft', new Highlight(range));
  if (matchMedia('(max-width:800px)').matches) { $('mobileQuote').textContent = state.quote; $('mobile-compose').hidden = false; }
  else { $('composeQuote').textContent = state.quote; $('compose').hidden = false; }
}
function render() {
  $('count').textContent = state.comments.length;
  $('empty').hidden = !!state.comments.length;
  $('cards').innerHTML = state.comments.map((comment, index) => `<div class="comment ${index === state.comments.length - 1 ? 'active' : ''}"><div class="comment-head"><span class="who">${esc(comment.by)} · just now</span><button class="jump" data-index="${index}">Jump to</button></div><p class="quote">${esc(comment.quote)}</p><p class="body">${esc(comment.feedback)}</p></div>`).join('');
  document.querySelectorAll('.jump').forEach((button) => button.onclick = () => state.savedRanges[+button.dataset.index]?.startContainer?.parentElement?.scrollIntoView({ behavior: 'smooth', block: 'center' }));
  $('send').disabled = !(state.comments.length || $('note').value.trim());
}
function commit(text) {
  if (!text.trim() || !state.draftRange) return;
  state.comments.push({ quote: state.quote, feedback: text.trim(), by: currentIdentity() }); state.savedRanges.push(state.draftRange);
  clearDraft(); paintSaved(); $('composeText').value = ''; $('mobileText').value = ''; getSelection().removeAllRanges(); closeCompose(); render();
}
async function submit() {
  const reviewer = currentIdentity(); if (!reviewer) return showIdentity();
  $('status').textContent = 'Submitting…';
  try {
    const response = await fetch('/api/submit', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ reviewer, comments: state.comments, overall_note: $('note').value.trim() }) });
    const body = await response.json(); if (!response.ok) throw Error(body.error); $('status').textContent = `Submitted Result ${body.result_id}`;
  } catch (error) { $('status').textContent = `Error: ${error.message}`; }
}
function boot() {
  $('handle').onclick = () => document.body.classList.toggle('collapsed');
  $('identity-confirm').onclick = () => setIdentity($('identity-name').value);
  $('composeAdd').onclick = () => commit($('composeText').value); $('composeCancel').onclick = closeCompose;
  $('mobileAdd').onclick = () => commit($('mobileText').value); $('mobileCancel').onclick = closeCompose;
  $('stage').addEventListener('mouseup', () => setTimeout(openCompose)); $('mobile-action').onclick = openCompose;
  $('note').oninput = render; $('send').onclick = submit;
  localStorage.getItem(state.identityKey) ? renderIdentity() : showIdentity(); render();
}
window.subspaceChrome = { boot, render, openCompose, closeCompose, state };
