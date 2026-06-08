const statusCodeElement = document.querySelector('.status-code');
const tipElement = document.querySelector('.tip');
const httpStatusElement = document.querySelector('.http-status');

function bodyClassForStatus(status) {
  const first = String(status)[0];
  if ('12345'.includes(first)) return `status-${first}`;
  return 'status-4';
}

function normalizeCode(raw) {
  const text = String(raw).replace(/\D/g, '');
  if (text.length >= 3) return text.slice(-3);
  return text;
}

function isStaticHost() {
  const host = window.location.hostname;
  return host.endsWith('github.io') || host.endsWith('.pages.dev');
}

function isStandaloneMode() {
  if (window.__STATIC_SITE__ === true) return true;
  if (window.location.protocol === 'file:') return true;
  if (/\.html$/i.test(window.location.pathname)) return true;
  if (isStaticHost()) return true;
  return false;
}

function getPageBasePath() {
  const path = window.location.pathname;
  if (/\.html$/i.test(path)) {
    return path.replace(/[^/]+$/, '');
  }
  if (!path.endsWith('/')) {
    return `${path}/`;
  }
  return path;
}

function getCodeFromPath() {
  if (window.__STATUS_CODE__) return window.__STATUS_CODE__;

  const path = window.location.pathname.replace(/\/$/, '');
  const segments = path.split('/').filter(Boolean);
  const last = segments[segments.length - 1];

  if (/^\d{3}$/.test(last)) return last;

  const fileMatch = window.location.pathname.match(/(\d{3})\.html$/i);
  if (fileMatch) return fileMatch[1];

  if (last === 'index.html' || last === '') return '200';

  return '200';
}

function getUrlForCode(code) {
  if (isStandaloneMode()) {
    const base = getPageBasePath();
    const file = code === '200' ? 'index.html' : `${code}.html`;
    return `${base}${file}`;
  }
  return code === '200' && window.location.pathname.match(/^\/?$/) ? '/' : `/${code}`;
}

function placeCursorAtEnd(el) {
  const range = document.createRange();
  const sel = window.getSelection();
  range.selectNodeContents(el);
  range.collapse(false);
  sel.removeAllRanges();
  sel.addRange(range);
}

function applyPayload(payload, httpStatus) {
  const code = payload.code;
  const desc = payload.description.includes(' - ')
    ? payload.description.split(' - ').slice(1).join(' - ')
    : payload.description;

  const isEditing = document.activeElement === statusCodeElement;
  const currentCode = normalizeCode(statusCodeElement.textContent);
  if (!isEditing || currentCode !== code) {
    statusCodeElement.textContent = code;
    if (isEditing) placeCursorAtEnd(statusCodeElement);
  }

  document.body.className = bodyClassForStatus(httpStatus);
  tipElement.textContent = `${httpStatus} ${payload.phrase} - ${desc}`;
  httpStatusElement.textContent = `HTTP/1.1 ${httpStatus} ${payload.phrase}`;
  document.title = `HTTP ${httpStatus}`;
  return code;
}

function getApiBase() {
  if (typeof window.__API_BASE__ === 'string') return window.__API_BASE__;
  if (isStandaloneMode()) return null;
  return '';
}

let lastNavigatedCode = getCodeFromPath();
let lastHttpStatus = 200;
let lastPayload = null;
let navigateSeq = 0;

function resolveLocally(code, { updateHistory = true } = {}) {
  const payload = buildPayload(code);
  const httpStatus = payload.status;
  applyPayload(payload, httpStatus);
  lastNavigatedCode = code;
  lastHttpStatus = httpStatus;
  lastPayload = payload;

  if (updateHistory) {
    history.pushState({ code, httpStatus, payload }, '', getUrlForCode(code));
  }
}

async function resolveFromServer(code, { updateHistory = true } = {}) {
  code = normalizeCode(code);
  if (code.length !== 3) return;

  const apiBase = getApiBase();
  if (apiBase === null) {
    resolveLocally(code, { updateHistory });
    return;
  }

  const seq = ++navigateSeq;
  tipElement.style.opacity = '0.6';

  try {
    const res = await fetch(`${apiBase}/api/${code}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const contentType = res.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) throw new Error('Not JSON');

    const payload = await res.json();
    if (seq !== navigateSeq) return;

    applyPayload(payload, res.status);
    lastNavigatedCode = code;
    lastHttpStatus = res.status;
    lastPayload = payload;

    if (updateHistory) {
      history.pushState({ code, httpStatus: res.status, payload }, '', getUrlForCode(code));
    }
  } catch {
    if (seq !== navigateSeq) return;
    resolveLocally(code, { updateHistory });
  } finally {
    if (seq === navigateSeq) {
      tipElement.style.opacity = '1';
    }
  }
}

function initFromUrl() {
  const initial = window.__INITIAL__ || buildPayload(getCodeFromPath());
  const httpStatus = initial.status ?? httpStatusForCode(initial.code);
  const code = applyPayload(initial, httpStatus);
  lastNavigatedCode = code;
  lastHttpStatus = httpStatus;
  lastPayload = initial;

  history.replaceState({ code, httpStatus, payload: initial }, '', getUrlForCode(code));
}

statusCodeElement.addEventListener('input', () => {
  let code = normalizeCode(statusCodeElement.textContent);
  if (code.length > 3) code = code.slice(-3);

  if (code !== statusCodeElement.textContent) {
    statusCodeElement.textContent = code;
    placeCursorAtEnd(statusCodeElement);
  }

  if (code.length === 3 && code !== lastNavigatedCode) {
    resolveFromServer(code);
  }
});

statusCodeElement.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    e.preventDefault();
    resolveFromServer(statusCodeElement.textContent);
    statusCodeElement.blur();
  }
});

statusCodeElement.addEventListener('blur', () => {
  const code = normalizeCode(statusCodeElement.textContent);
  if (code.length !== 3 && lastPayload) {
    applyPayload(lastPayload, lastHttpStatus);
  }
});

statusCodeElement.addEventListener('click', (e) => {
  if (e.detail === 2) {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(statusCodeElement);
    selection.removeAllRanges();
    selection.addRange(range);
  }
});

window.addEventListener('popstate', (e) => {
  const state = e.state;
  if (state?.payload) {
    applyPayload(state.payload, state.httpStatus);
    lastNavigatedCode = state.code;
    lastHttpStatus = state.httpStatus;
    lastPayload = state.payload;
    return;
  }
  resolveFromServer(getCodeFromPath(), { updateHistory: false });
});

initFromUrl();
