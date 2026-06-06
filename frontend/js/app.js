/**
 * Multilingual Ticket Translator — Frontend Application
 * ======================================================
 * Handles:
 *  - Ticket form submission and API communication
 *  - Progressive loading steps UI
 *  - Result rendering with colour-coded badges
 *  - Example quick-fill buttons
 *  - Copy-to-clipboard for the raw JSON
 */

'use strict';

const API_BASE = 'http://localhost:5000/api';

// ── DOM element references ────────────────────────────────────────────────────
const ticketInput    = document.getElementById('ticketInput');
const submitBtn      = document.getElementById('submitBtn');
const charCount      = document.getElementById('charCount');
const clearBtn       = document.getElementById('clearBtn');
const copyBtn        = document.getElementById('copyBtn');

const placeholder    = document.getElementById('placeholder');
const loadingState   = document.getElementById('loadingState');
const loadingStepTxt = document.getElementById('loadingStepText');
const loadingBar     = document.getElementById('loadingProgress');
const errorState     = document.getElementById('errorState');
const errorMessage   = document.getElementById('errorMessage');
const resultContent  = document.getElementById('resultContent');

// Pipeline step DOM nodes
const pipelineSteps  = document.querySelectorAll('.pipeline-step');

// Stores the last successful result for clipboard copy
let lastResult = null;

// ── Character counter ─────────────────────────────────────────────────────────
ticketInput.addEventListener('input', () => {
  const len = ticketInput.value.length;
  charCount.textContent = `${len} / 5000`;
  charCount.classList.toggle('text-danger', len >= 4800);
});

// ── Clear button ──────────────────────────────────────────────────────────────
clearBtn.addEventListener('click', () => {
  ticketInput.value = '';
  charCount.textContent = '0 / 5000';
  ticketInput.focus();
  resetResults();
});

// ── Example quick-fill buttons ────────────────────────────────────────────────
document.querySelectorAll('.example-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    ticketInput.value = btn.dataset.text;
    charCount.textContent = `${btn.dataset.text.length} / 5000`;
    ticketInput.focus();
  });
});

// ── Main submit function ──────────────────────────────────────────────────────
async function submitTicket() {
  const text = ticketInput.value.trim();

  if (!text) {
    showInputError('Please enter a support ticket message.');
    return;
  }

  setLoadingState(true);
  setActivePipelineStep(1);

  try {
    // Step 1 label — detecting language
    await animateLoadingStep('Step 1: Detecting language…', 20, 1);

    // Step 2 label — translating
    await animateLoadingStep('Step 2: Translating to English…', 45, 2);

    // Step 3 label — AI analysis
    await animateLoadingStep('Step 3: Analysing with Gemini AI…', 70, 3);

    // ── API call ──────────────────────────────────────────────────────────
    const response = await fetch(`${API_BASE}/process-ticket`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticket_text: text }),
    });

    const json = await response.json();

    if (!response.ok || !json.success) {
      throw new Error(json.error || `Server error: ${response.status}`);
    }

    // Step 4 label — assembling output
    await animateLoadingStep('Step 4: Assembling structured output…', 90, 4);
    await sleep(300);
    setActivePipelineStep(5);

    // Render results
    renderResults(json.data);
    lastResult = json.data;

  } catch (err) {
    showError(err.message || 'An unexpected error occurred. Check your API key and server.');
  } finally {
    setLoadingState(false);
  }
}

// ── Render results ────────────────────────────────────────────────────────────
function renderResults(data) {
  // Language & timing
  setText('res-language', `${data.language_name} (${data.detected_language})`);
  setText('res-time',     `${data.processing_time_ms} ms`);

  // Translation
  setText('res-translation', data.translation || '—');

  // Category
  const catEl = document.getElementById('res-category');
  catEl.textContent = data.category || '—';

  // Priority badge
  const priEl = document.getElementById('res-priority');
  priEl.textContent = data.priority || '—';
  priEl.className = `priority-badge ${data.priority || ''}`;

  // Sentiment badge
  const senEl = document.getElementById('res-sentiment');
  senEl.textContent = data.sentiment || '—';
  senEl.className = `sentiment-badge ${data.sentiment || ''}`;

  // Summary & response
  setText('res-summary',  data.summary  || '—');
  setText('res-response', data.response || '—');

  // Keywords
  const kwContainer = document.getElementById('res-keywords');
  kwContainer.innerHTML = '';
  (data.keywords || []).forEach(kw => {
    const chip = document.createElement('span');
    chip.className = 'keyword-chip';
    chip.textContent = kw;
    kwContainer.appendChild(chip);
  });

  // Show results pane with animation
  hideAll();
  resultContent.classList.remove('d-none');
  resultContent.classList.add('fade-in');
  copyBtn.classList.remove('d-none');
}

// ── Loading state helpers ─────────────────────────────────────────────────────
function setLoadingState(on) {
  if (on) {
    hideAll();
    loadingState.classList.remove('d-none');
    submitBtn.classList.add('btn-loading');
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing…';
    copyBtn.classList.add('d-none');
  } else {
    loadingState.classList.add('d-none');
    submitBtn.classList.remove('btn-loading');
    submitBtn.innerHTML = '<i class="bi bi-send-fill me-2"></i>Translate &amp; Analyse';
  }
}

async function animateLoadingStep(label, progress, step) {
  loadingStepTxt.textContent = label;
  loadingBar.style.width = `${progress}%`;
  setActivePipelineStep(step);
  await sleep(500);
}

function setActivePipelineStep(step) {
  pipelineSteps.forEach(el => {
    el.classList.toggle('active', parseInt(el.dataset.step) === step);
  });
}

// ── Error helpers ─────────────────────────────────────────────────────────────
function showError(message) {
  hideAll();
  errorMessage.textContent = message;
  errorState.classList.remove('d-none');
}

function showInputError(message) {
  ticketInput.classList.add('is-invalid');
  setTimeout(() => ticketInput.classList.remove('is-invalid'), 2500);
  alert(message); // Simple fallback — replace with toast in production
}

function resetResults() {
  hideAll();
  placeholder.classList.remove('d-none');
  copyBtn.classList.add('d-none');
  pipelineSteps.forEach(el => el.classList.remove('active'));
  lastResult = null;
}

function hideAll() {
  placeholder.classList.add('d-none');
  loadingState.classList.add('d-none');
  errorState.classList.add('d-none');
  resultContent.classList.add('d-none');
}

// ── Clipboard copy ────────────────────────────────────────────────────────────
function copyResult() {
  if (!lastResult) return;
  navigator.clipboard.writeText(JSON.stringify(lastResult, null, 2)).then(() => {
    copyBtn.innerHTML = '<i class="bi bi-check2 me-1"></i>Copied!';
    setTimeout(() => {
      copyBtn.innerHTML = '<i class="bi bi-clipboard me-1"></i>Copy JSON';
    }, 2000);
  });
}

// ── Utility ───────────────────────────────────────────────────────────────────
function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
