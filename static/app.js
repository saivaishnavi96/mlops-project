const $ = (id) => document.getElementById(id);
const runBtn = $('run-btn');

function percent(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—';
  return `${(Number(value) * 100).toFixed(1)}%`;
}
function metric(id, value) { $(id).textContent = percent(value); }

async function loadMetrics() {
  try {
    const response = await fetch('/api/metrics');
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Could not load metrics');
    const a = data.model_a || {}, b = data.model_b || {};
    metric('accuracy-a', a.accuracy); metric('accuracy-b', b.accuracy);
    metric('table-a-acc', a.accuracy); metric('table-a-pre', a.precision); metric('table-a-rec', a.recall); metric('table-a-f1', a.f1_score);
    metric('table-b-acc', b.accuracy); metric('table-b-pre', b.precision); metric('table-b-rec', b.recall); metric('table-b-f1', b.f1_score);
  } catch (error) {
    $('accuracy-a').innerHTML = '—<small> accuracy</small>';
    $('accuracy-b').innerHTML = '—<small> accuracy</small>';
    showError('Metrics are unavailable. Check that your model files and results CSV are in place.');
  }
}
function showError(message) { const box = $('error'); box.textContent = message; box.hidden = false; }
function intentLabel(value) { return String(value || 'Unknown').replaceAll('_', ' ').replace(/\b\w/g, c => c.toUpperCase()); }

async function compare() {
  const question = $('question').value.trim();
  $('error').hidden = true;
  if (!question) { showError('Please enter a customer question first.'); $('question').focus(); return; }
  runBtn.disabled = true; runBtn.querySelector('span').textContent = 'Comparing…';
  try {
    const response = await fetch('/api/predict', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question, selected_model:$('selected-model').value})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Prediction failed');
    $('result-area').hidden = false;
    $('intent-a').textContent = intentLabel(data.model_a.intent);
    $('intent-b').textContent = intentLabel(data.model_b.intent);
    $('latency-a').textContent = `Response time: ${Number(data.model_a.latency_ms).toFixed(3)} ms`;
    $('latency-b').textContent = `Response time: ${Number(data.model_b.latency_ms).toFixed(3)} ms`;
    $('response-a').textContent = data.model_a.response;
    $('response-b').textContent = data.model_b.response;
    const agree = data.model_a.intent === data.model_b.intent;
    $('agreement').textContent = agree ? '✓ Models agree' : 'Models differ';
    $('agreement').classList.toggle('no', !agree);
    $('recommendation').textContent = data.recommended_model;
    $('recommendation-note').textContent = `Test accuracy — Model A: ${percent(data.accuracy_a)} · Model B: ${percent(data.accuracy_b)}. This overall score does not guarantee the correct prediction for this individual question.`;
    $('result-area').scrollIntoView({behavior:'smooth',block:'nearest'});
  } catch (error) { showError(error.message); }
  finally { runBtn.disabled = false; runBtn.querySelector('span').textContent = 'Compare models'; }
}
runBtn.addEventListener('click', compare);
$('question').addEventListener('keydown', e => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') compare(); });
document.querySelectorAll('[data-example]').forEach(button => button.addEventListener('click', () => { $('question').value = button.dataset.example; $('question').focus(); }));
loadMetrics();
