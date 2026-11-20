const $ = (id) => document.getElementById(id);
const make = (tag, className, text) => {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text !== undefined) el.textContent = String(text);
  return el;
};
async function apiRequest(path, options) {
  const response = await fetch(path, options);
  const id = response.headers.get('X-Request-ID');
  if (id) {
    const log = $('audit-log');
    log.prepend(make('li', '', new Date().toISOString() + ' | ' + path.split('?')[0] + ' | HTTP ' + response.status + ' | ' + id));
    if (log.children.length > 20) log.lastChild.remove();
  }
  return response;
}
const safeLink = (url) => {
  try {
    const parsed = new URL(url);
    return ['https:', 'http:'].includes(parsed.protocol) ? parsed.href : null;
  } catch { return null; }
};

$('research-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const results = $('results');
  const btn = $('search-btn');
  btn.disabled = true;
  btn.textContent = 'Searching literature…';
  results.replaceChildren(make('div', 'notice', 'Retrieving publication metadata and checking source IDs…'));
  try {
    const response = await apiRequest('/api/research', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        condition: $('condition').value.trim(), question: $('question').value.trim(),
        jurisdiction: $('jurisdiction').value, max_results: Number($('limit').value),
        consent_external_search: $('consent').checked, use_ai: $('use-ai').checked,
        consent_cloud_llm: $('cloud-consent').checked,
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(JSON.stringify(data));
    renderResearch(data);
  } catch (err) {
    results.replaceChildren(make('div', 'notice', `Search error: ${String(err.message || err)}`));
  } finally { $('cloud-consent').checked = false; btn.disabled = false; btn.innerHTML = 'Research evidence <span>↗</span>'; }
});

function renderResearch(data) {
  const results = $('results');
  results.replaceChildren();
  const header = make('div', 'result-heading');
  header.append(make('h2', '', 'Retrieved evidence'),
    make('small', '', `${data.evidence.length} source records · ${data.ai_enabled ? `${data.llm_provider}/${data.llm_model}` : 'metadata only'}`));
  results.append(header);
  if (data.search_queries?.length) {
    const plan = make('details');
    plan.append(make('summary', '', 'Inspect search queries'));
    for (const query of data.search_queries) plan.append(make('p', '', query));
    results.append(plan);
  }
  (data.notices || []).forEach(message => results.append(make('div', 'notice', message)));
  if (!data.evidence.length) {
    results.append(make('div', 'empty-results', 'No indexed articles returned. Try broader medical terms or verify the literature service.'));
    return;
  }
  const grid = make('div', 'evidence-grid');
  data.evidence.forEach((item) => {
    const card = make('article', 'evidence-card');
    const meta = make('div', 'evidence-meta');
    meta.append(make('span', 'evidence-category', item.evidence_category.replaceAll('_', ' ')),
      make('span', '', `${item.year || 'Undated'} · ${item.evidence_id}`));
    card.append(meta, make('h3', '', item.title), make('small', '', item.status.replaceAll('_', ' ') + ' | Retrieved ' + item.collected_at));
    if (item.abstract) card.append(make('p', '', item.abstract));
    const link = make('a', '', 'View source ↗');
    const href = safeLink(item.url);
    if (href) { link.href = href; link.target = '_blank'; link.rel = 'noopener noreferrer'; }
    card.append(link);
    grid.append(card);
  });
  results.append(grid);
  if (data.findings.length) {
    results.append(make('h2', '', 'AI evidence brief · preliminary'));
    data.findings.forEach(f => {
      const note = make('div', 'finding', f.statement);
      note.append(make('small', '', `Sources: ${f.evidence_ids.join(', ')} · AI confidence: ${f.confidence}`));
      results.append(note);
    });
  }
}

// The OR workbench uses bundled synthetic examples; no patient data are uploaded.
const paths = {
  milp: '/api/optimize', cp_sat: '/api/or/cp-sat', mcda: '/api/or/mcda',
  pareto: '/api/or/pareto', scenarios: '/api/or/scenarios',
  monte_carlo: '/api/or/monte-carlo', markov: '/api/or/markov',
  dynamic_programming: '/api/or/dynamic-programming', queueing: '/api/or/queueing',
};
let examples = {};
async function loadExamples() {
  const target = $('optimization-results');
  try {
    const response = await fetch('/static/or_examples.json');
    if (!response.ok) throw new Error('Could not load bundled examples');
    examples = await response.json();
    showExample();
  } catch (err) { target.replaceChildren(make('div', 'notice', String(err))); }
}
function showExample() {
  const payload = examples[$('engine-picker').value];
  $('or-json').value = payload ? JSON.stringify(payload, null, 2) : '';
  $('optimization-results').replaceChildren();
}
$('engine-picker').addEventListener('change', showExample);
$('run-demo').addEventListener('click', async () => {
  const target = $('optimization-results');
  const button = $('run-demo');
  button.disabled = true;
  target.replaceChildren(make('div', 'notice', 'Running mathematical analysis…'));
  try {
    const payload = JSON.parse($('or-json').value);
    const endpoint = paths[$('engine-picker').value];
    const response = await apiRequest(endpoint, {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(JSON.stringify(data, null, 2));
    const result = make('div', 'op-result');
    result.append(make('strong', '', `${data.algorithm || 'milp'} · ${String(data.status).toUpperCase()}`));
    result.append(make('p', '', data.summary || data.explanation || ''));
    const pre = make('pre', 'or-output', JSON.stringify(data.details || {
      selected: data.selected, objective: data.objective, caveats: data.caveats
    }, null, 2));
    result.append(pre);
    (data.assumptions || []).forEach(a => result.append(make('p', 'or-assumption', a)));
    target.replaceChildren(result);
  } catch (err) { target.replaceChildren(make('div', 'notice', String(err.message || err))); }
  finally { button.disabled = false; }
});
loadExamples();


// Server-owned settings: browser never receives provider API tokens.
async function updateLLMStatus() {
  try {
    const response = await apiRequest('/api/llm/status');
    if (!response.ok) throw new Error('Could not load LLM configuration');
    const info = await response.json();
    const configured = Boolean(info.configured);
    $('llm-pill').textContent = configured ? `${info.deployment} / ${info.provider}` : 'Needs configuration';
    $('llm-summary').textContent = configured
      ? `${info.model} · ${info.provider} · ${info.deployment} inference. Endpoint: ${info.base_url}`
      : `LLM not configured: ${info.error || 'Provider is disabled'}`;
  } catch (err) { $('llm-summary').textContent = String(err.message || err); }
}
$('check-llm').addEventListener('click', async () => {
  const button = $('check-llm');
  button.disabled = true;
  $('llm-feedback').replaceChildren(make('div', 'notice', 'Testing inference connection…'));
  try {
    const response = await apiRequest('/api/llm/check?consent_cloud_llm=' + $('probe-consent').checked, {method: 'POST'});
    $('probe-consent').checked = false;
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || JSON.stringify(result));
    $('llm-feedback').replaceChildren(make('div', 'finding',
      `Connected: ${result.deployment} / ${result.provider} / ${result.model}`));
  } catch (err) {
    $('llm-feedback').replaceChildren(make('div', 'notice', `Model not reachable: ${String(err.message || err)}`));
  } finally { button.disabled = false; }
});
$('ask-or-llm').addEventListener('click', async () => {
  const target = $('method-results');
  const button = $('ask-or-llm');
  button.disabled = true;
  target.replaceChildren(make('div', 'notice', 'Checking candidate OR methods with the model…'));
  try {
    const response = await apiRequest('/api/llm/method-advice', {method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        problem: {problem_type: $('or-question').value.trim(),
          has_multiple_criteria: $('adv-criteria').checked,
          need_uncertainty_analysis: $('adv-uncertainty').checked,
          has_resource_constraints: $('adv-resources').checked,
          decisions_are_sequential: $('adv-sequential').checked,
          has_probabilities: $('adv-probabilities').checked,
          is_patient_flow: $('adv-flow').checked},
        consent_cloud_llm: $('or-cloud-consent').checked,
      })});
    const output = await response.json();
    if (!response.ok) throw new Error(output.detail || JSON.stringify(output));
    const box = make('div', 'op-result');
    box.append(make('strong', '', `AI explanation via ${output.model}`),
               make('p', '', output.ai.explanation));
    box.append(make('strong', '', 'Rule-based candidate methods'));
    for (const suggestion of output.routing.suggestions) {
      box.append(make('p', '', `${suggestion.algorithm} — ${suggestion.reason}`));
    }
    if (output.ai.data_needed.length) {
      box.append(make('strong', '', 'Data required'));
      for (const field of output.ai.data_needed) box.append(make('p', '', `• ${field}`));
    }
    target.replaceChildren(box);
  } catch (err) {
    target.replaceChildren(make('div', 'notice', String(err.message || err)));
  } finally { $('or-cloud-consent').checked = false; button.disabled = false; }
});
updateLLMStatus();
