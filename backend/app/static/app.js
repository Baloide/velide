'use strict';
const getElement = id => document.getElementById(id);
const filterIds = ['chkNames', 'chkTaxCodes', 'chkDates', 'chkContacts', 'chkLocations', 'chkIds'];
const optionKeys = ['redact_names', 'redact_tax_codes', 'redact_dates', 'redact_contacts',
  'redact_locations', 'redact_ids'
];
let savedLanguage;
try {
  savedLanguage = localStorage.getItem('baloide-language');
} catch {}
// Keep an explicit choice; otherwise use the first supported browser preference.
const browserLanguages = Array.isArray(navigator.languages) ? navigator.languages : [];
const systemLocale = new URLSearchParams(location.search).get('locale');
const preferredLanguage = [systemLocale, ...browserLanguages, navigator.language].map(value =>
  typeof value === 'string' ? value.toLowerCase().split(/[-_]/)[0] : '').find(value =>
  Object.hasOwn(translations, value));
let language = Object.hasOwn(translations, savedLanguage) ? savedLanguage :
  (preferredLanguage || 'en');
// Only the current document revision may publish redacted output.
let revision = 0,
  controller, debounceTimer, toastTimer, entities = [],
  statusKey = 'ready';
// Import generation changes only when replacing or editing the source document.
let importing = false,
  importController, importGeneration = 0,
  importedDocument = null,
  importErrorKey = null;
const t = key => translations[language][key];

function status(key) {
  statusKey = key;
  getElement('processStatus').textContent = t(key);
  getElement('processStatus').classList.toggle('error', ['error', 'importFailed', 'importStopped']
    .includes(key));
}

function counters() {
  getElement('charCountInput').textContent =
    `${getElement('rawInput').value.length.toLocaleString(language)} ${t('characters')}`;
  getElement('statEntities').textContent = `${entities.length} ${t('removed')}`;
  getElement('badgeCount').textContent = `${entities.length} ${t('items')}`;
}

function translate() {
  document.documentElement.lang = language;
  getElement('language').value = language;
  document.querySelectorAll('[data-i18n]').forEach(el => el.textContent = t(el.dataset.i18n));
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => el.placeholder = t(el.dataset
    .i18nPlaceholder));
  counters();
  status(statusKey);
  renderImportStatus();
}

function enableExport(enabled) {
  ['btnCopy', 'btnCopyPrompt', 'btnDownload'].forEach(id => getElement(id).disabled = !enabled);
}
/** Discard output immediately when its source or detection options change. */
function invalidate() {
  revision++;
  controller?.abort();
  clearTimeout(debounceTimer);
  getElement('redactedOutput').value = '';
  entities = [];
  getElement('entitiesChips').replaceChildren();
  getElement('entitiesSection').hidden = true;
  getElement('statTime').textContent = '—';
  enableExport(false);
  counters();
  status(getElement('rawInput').value.trim() ? 'processing' : 'ready');
}

function options() {
  return {
    language,
    mask_mode: getElement('maskMode').value,
    ...Object.fromEntries(filterIds.map((id, i) => [optionKeys[i], getElement(id).checked])),
    custom_keywords: getElement('customKeywords').value.split('\n').map(s => s.trim()).filter(
      Boolean)
  };
}

function renderEntities() {
  const fragment = document.createDocumentFragment();
  entities.forEach(entity => {
    const chip = document.createElement('div');
    chip.className = 'entity-chip';
    const kind = document.createElement('b');
    kind.textContent = entity.replacement.replace(/[\[\]]/g, '');
    const original = document.createElement('del');
    original.textContent = entity.original;
    const arrow = document.createElement('span');
    arrow.textContent = '→';
    const replacement = document.createElement('span');
    replacement.textContent = entity.replacement;
    chip.append(kind, original, arrow, replacement);
    fragment.append(chip);
  });
  getElement('entitiesChips').replaceChildren(fragment);
  getElement('entitiesSection').hidden = !entities.length;
}
async function processRedaction() {
  const current = revision;
  if (importing || !getElement('rawInput').value.trim()) return;
  controller = new AbortController();
  try {
    const res = await fetch('/api/redact/text', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text: getElement('rawInput').value,
        options: options()
      }),
      signal: controller.signal
    });
    if (!res.ok) throw new Error('redaction');
    const data = await res.json();
    if (current !== revision) return;
    getElement('redactedOutput').value = data.redacted_text;
    entities = data.entities;
    renderEntities();
    counters();
    getElement('statTime').textContent = `${data.execution_ms} ms`;
    status('done');
    enableExport(true);
  } catch (error) {
    if (error.name !== 'AbortError' && current === revision) {
      status('error');
      enableExport(false);
    }
  }
}

function schedule() {
  invalidate();
  if (importing) {
    status('importingFile');
    return;
  }
  debounceTimer = setTimeout(processRedaction, 250);
}

function toast(key) {
  clearTimeout(toastTimer);
  getElement('toast').textContent = t(key);
  getElement('toast').hidden = false;
  toastTimer = setTimeout(() => getElement('toast').hidden = true, 4000);
}
getElement('appearance').value = appearancePreference;
getElement('appearance').addEventListener('change', () => setAppearance(getElement('appearance')
  .value));
getElement('rawInput').addEventListener('input', () => {
  importErrorKey = null;
  cancelImport();
  schedule();
});
getElement('customKeywords').addEventListener('input', schedule);
[getElement('maskMode'), ...filterIds.map(getElement)].forEach(el => el.addEventListener('change',
  schedule));
getElement('language').addEventListener('change', () => {
  language = getElement('language').value;
  try {
    localStorage.setItem('baloide-language', language);
  } catch {}
  translate();
  schedule();
});
getElement('btnClear').addEventListener('click', () => {
  resetImport();
  getElement('rawInput').value = '';
  getElement('customKeywords').value = '';
  invalidate();
  getElement('rawInput').focus();
});
getElement('btnLoadSample').addEventListener('click', async () => {
  resetImport();
  invalidate();
  const current = revision;
  const requestedLanguage = language;
  try {
    const res = await fetch(`/api/sample?language=${requestedLanguage}`);
    if (!res.ok) throw new Error('sample');
    const data = await res.json();
    if (current !== revision) return;
    getElement('rawInput').value = data.sample;
    schedule();
  } catch {
    if (current === revision) {
      status('ready');
      toast('sampleError');
    }
  }
});
async function copy(withPrompt) {
  if (getElement('btnCopy').disabled) return;
  try {
    await navigator.clipboard.writeText((withPrompt ? t('prompt') + '\n\n---\n' : '') +
      getElement('redactedOutput').value + (withPrompt ? '\n---' : ''));
    toast('copied');
  } catch {
    toast('copyError');
  }
}
getElement('btnCopy').addEventListener('click', () => copy(false));
getElement('btnCopyPrompt').addEventListener('click', () => copy(true));
getElement('btnDownload').addEventListener('click', () => {
  if (getElement('btnDownload').disabled) return;
  const url = URL.createObjectURL(new Blob([getElement('redactedOutput').value], {
    type: 'text/plain;charset=utf-8'
  }));
  const a = document.createElement('a');
  a.href = url;
  a.download = `clinical-redacted-${language}-${new Date().toISOString().slice(0,10)}.txt`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});

const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;
const ingestErrorKeys = new Set(['fileTooLarge', 'unsupportedFile', 'emptyFile', 'unreadableFile',
  'encryptedPdf', 'pdfNoText', 'tooManyPages', 'textTooLong', 'textEncoding',
  'documentTooComplex', 'serviceOutdated'
]);

function renderImportStatus() {
  const element = getElement('importStatus');
  element.hidden = !importing && !importedDocument && !importErrorKey;
  element.classList.toggle('error', Boolean(importErrorKey));
  element.textContent = importing ? t('importingFile') : importErrorKey ? t(importErrorKey) :
    importedDocument ?
    `${t('fileImported')} · ${importedDocument.format.toUpperCase()} · ${importedDocument.characters.toLocaleString(language)} ${t('characters')}` :
    '';
  getElement('fileDropZone').setAttribute('aria-busy', String(importing));
  const warnings = importedDocument?.warnings || [];
  getElement('importNotice').hidden = !warnings.length;
  getElement('importNotice').textContent = warnings.map(key => t(key)).filter(Boolean).join(' ');
}

function cancelImport() {
  importGeneration++;
  importController?.abort();
  importing = false;
  renderImportStatus();
}

function resetImport() {
  cancelImport();
  importedDocument = null;
  importErrorKey = null;
  renderImportStatus();
}
/** Import one local file; stale generations must never replace newer editor text. */
async function ingestFiles(files) {
  resetImport();
  invalidate();
  if (files.length !== 1) {
    importErrorKey = 'oneFileOnly';
    status('importStopped');
    renderImportStatus();
    return;
  }
  const file = files[0];
  const format = file.name.split('.').pop().toLowerCase();
  if (!['pdf', 'docx', 'txt', 'md'].includes(format)) {
    importErrorKey = 'unsupportedFile';
    status('importStopped');
    renderImportStatus();
    return;
  }
  if (file.size > MAX_UPLOAD_BYTES) {
    importErrorKey = 'fileTooLarge';
    status('importStopped');
    renderImportStatus();
    return;
  }
  importing = true;
  const generation = importGeneration;
  importController = new AbortController();
  status('importingFile');
  renderImportStatus();
  try {
    // Send only file bytes and format: the filename never enters the API or export.
    const response = await fetch(`/api/ingest/file?format=${format}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/octet-stream'
      },
      body: file,
      signal: importController.signal
    });
    const data = await response.json().catch(() => null);
    if (generation !== importGeneration) return;
    if (response.status === 404 || response.status === 405) throw new Error('serviceOutdated');
    if (!response.ok) {
      const code = data?.detail?.code;
      throw new Error(ingestErrorKeys.has(code) ? code : response.status === 413 ?
        'fileTooLarge' : 'importFailed');
    }
    if (!data || typeof data.text !== 'string' || !Number.isInteger(data.characters))
      throw new Error('importFailed');
    importing = false;
    importedDocument = data;
    importErrorKey = null;
    getElement('rawInput').value = data.text;
    renderImportStatus();
    schedule();
  } catch (error) {
    if (error.name === 'AbortError' || generation !== importGeneration) return;
    importing = false;
    importErrorKey = ingestErrorKeys.has(error.message) ? error.message : 'importFailed';
    status('importStopped');
    renderImportStatus();
  }
}
getElement('btnChooseFile').addEventListener('click', () => getElement('fileInput').click());
getElement('fileInput').addEventListener('change', () => {
  const files = Array.from(getElement('fileInput').files);
  getElement('fileInput').value = '';
  if (files.length) ingestFiles(files);
});
let dragDepth = 0;
const hasFiles = event => Array.from(event.dataTransfer?.types || []).includes('Files');
getElement('inputPanel').addEventListener('dragenter', event => {
  if (!hasFiles(event)) return;
  event.preventDefault();
  dragDepth++;
  getElement('inputPanel').classList.add('drag-active');
});
getElement('inputPanel').addEventListener('dragover', event => {
  if (hasFiles(event)) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'copy';
  }
});
getElement('inputPanel').addEventListener('dragleave', () => {
  dragDepth = Math.max(0, dragDepth - 1);
  if (!dragDepth) getElement('inputPanel').classList.remove('drag-active');
});
getElement('inputPanel').addEventListener('drop', event => {
  if (!hasFiles(event)) return;
  event.preventDefault();
  dragDepth = 0;
  getElement('inputPanel').classList.remove('drag-active');
  ingestFiles(Array.from(event.dataTransfer.files));
});
// Keep dropped files outside the input panel from navigating away from the document.
for (const type of ['dragover', 'drop']) document.addEventListener(type, event => {
  if (hasFiles(event)) event.preventDefault();
});

translate();
fetch('/api/downloads').then(res => res.json()).then(data => {
  if (data.windows) {
    getElement('windowsDownload').href = data.windows;
    getElement('windowsDownload').hidden = false;
  }
}).catch(() => {});

// Display the version of the service actually processing this document.
fetch('/api/health').then(res => {
  if (!res.ok) throw new Error('Service metadata unavailable');
  return res.json();
}).then(data => {
  if (typeof data.version === 'string' && /^\d+\.\d+\.\d+$/.test(data.version)) {
    getElement('appVersion').textContent = `v${data.version}`;
  }
}).catch(() => {});
