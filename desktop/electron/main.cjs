'use strict';
const {
  app,
  BrowserWindow,
  dialog,
  session
} = require('electron');
const {
  spawn
} = require('node:child_process');
const readline = require('node:readline');
const path = require('node:path');
const fs = require('node:fs');
const smoke = process.argv.includes('--smoke-test');
let service;
let window;
let quitting = false;

function stopService() {
  if (!service) return;
  service.stdin.end();
  const child = service;
  const timeout = setTimeout(() => child.kill(), 6000);
  timeout.unref();
  child.once('exit', () => clearTimeout(timeout));
  service = null;
}

function startService() {
  return new Promise((resolve, reject) => {
    const root = path.resolve(__dirname, '../..');
    const executable = app.isPackaged ? path.join(process.resourcesPath, 'backend/VelideService.exe') :
      (process.env.VELIDE_PYTHON || path.join(root, 'backend/.venv/Scripts/python.exe'));
    const args = app.isPackaged ? [] : [path.join(root, 'desktop/service.py')];
    service = spawn(executable, args, {
      windowsHide: true,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    service.stdin.on('error', () => {});
    const timer = setTimeout(() => reject(new Error('Local service startup timed out')), 45000);
    const lines = readline.createInterface({
      input: service.stdout
    });
    lines.on('line', line => {
      try {
        const url = new URL(JSON.parse(line).url);
        if (url.protocol !== 'http:' || url.hostname !== '127.0.0.1' || !url.port) return;
        clearTimeout(timer);
        lines.close();
        resolve(url.origin);
      } catch {}
    });
    service.stderr.on('data', () => {}); // Do not persist parser or document diagnostics.
    service.once('error', () => {
      clearTimeout(timer);
      reject(new Error('Local service could not start'));
    });
    service.once('exit', () => {
      clearTimeout(timer);
      reject(new Error('Local service stopped'));
      if (!quitting) {
        if (!smoke) dialog.showErrorBox('Velide', 'The local service stopped. Restart Velide to continue.');
        app.exit(1);
      }
    });
  });
}

async function verifyDesktop() {
  const checks = await window.webContents.executeJavaScript(`(async () => {
    const check = (value, message) => {if (!value) throw new Error(message)};
    check(document.title.includes('Velide'), 'Missing Velide title');
    const health = await (await fetch('/api/health')).json();
    check(health.version === ${JSON.stringify(app.getVersion())}, 'API and Electron version mismatch');
    check(document.querySelector('#appVersion').textContent === 'v' + health.version, 'Missing footer version');
    check(document.querySelector('#rawInput').value === '', 'Startup must not preload a document');
    for (const image of document.images) check(image.complete && image.naturalWidth > 0, 'Missing logo');
    check(document.querySelector('footer').textContent.includes(String.fromCharCode(169) + ' 2026 Baloide'), 'Missing copyright');
    check(typeof require === 'undefined' && typeof process === 'undefined', 'Renderer has Node access');
    document.querySelector('#language').value = 'en';
    document.querySelector('#language').dispatchEvent(new Event('change'));
    document.querySelector('#btnLoadSample').click();
    for (let i = 0; i < 100 && document.querySelector('#btnCopy').disabled; i++) await new Promise(r => setTimeout(r, 100));
    check(!document.querySelector('#btnCopy').disabled, 'Redaction unavailable');
    check(document.querySelector('#redactedOutput').value.includes('[PATIENT_NAME]'), 'Missing redaction');
    for (const theme of ['light', 'dark', 'system']) {
      document.querySelector('#appearance').value = theme;
      document.querySelector('#appearance').dispatchEvent(new Event('change'));
      check(theme === 'system' || document.documentElement.dataset.theme === theme, 'Theme failed');
    }
    const response = await fetch('/api/ingest/file?format=txt', {
      method: 'POST', headers: {'Content-Type': 'application/octet-stream'}, body: 'Patient: James Smith'
    });
    check(response.ok && (await response.json()).text.includes('James Smith'), 'Packaged import failed');
    return {language: document.documentElement.lang, theme: document.documentElement.dataset.theme};
  })()`);
  const outputIndex = process.argv.indexOf('--smoke-result');
  if (outputIndex < 0 || !process.argv[outputIndex + 1]) throw new Error('Missing smoke result path');
  const output = process.argv[outputIndex + 1];
  fs.writeFileSync(output, `OK: Electron window, sandbox, bundled backend, logos, themes, English redaction and TXT import. ${JSON.stringify(checks)}\n`);
  const screenshot = await window.webContents.capturePage();
  fs.writeFileSync(output + '.png', screenshot.toPNG());
  // A fresh profile must retain only language/theme preferences after verification.
  await window.webContents.executeJavaScript("document.querySelector('#btnClear').click()");
}

if (!smoke && !app.requestSingleInstanceLock()) app.quit();
else {
  app.on('second-instance', () => {
    if (window) {
      if (window.isMinimized()) window.restore();
      window.focus();
    }
  });
  if (smoke) {
    const index = process.argv.indexOf('--smoke-result');
    if (index >= 0) app.setPath('userData', path.join(path.dirname(process.argv[index + 1]), 'electron-smoke-profile'));
  }
  app.whenReady().then(async () => {
    const origin = await startService();
    const localSession = session.defaultSession;
    localSession.setPermissionRequestHandler((_contents, permission, callback) => callback(permission === 'clipboard-sanitized-write'));
    localSession.setPermissionCheckHandler((_contents, permission) => permission === 'clipboard-sanitized-write');
    localSession.webRequest.onBeforeRequest((details, callback) => {
      callback({
        cancel: !details.url.startsWith(origin + '/')
      });
    });
    window = new BrowserWindow({
      width: 1440,
      height: 1020,
      minWidth: 780,
      minHeight: 650,
      title: 'Velide by Baloide',
      backgroundColor: '#121827',
      show: false,
      autoHideMenuBar: true,
      webPreferences: {
        sandbox: true,
        contextIsolation: true,
        nodeIntegration: false,
        webSecurity: true,
        devTools: !app.isPackaged
      }
    });
    window.webContents.setWindowOpenHandler(() => ({
      action: 'deny'
    }));
    window.webContents.on('will-navigate', (event, url) => {
      if (!url.startsWith(origin + '/')) event.preventDefault();
    });
    const locale = app.getPreferredSystemLanguages().find(value => ['it', 'en', 'es', 'de', 'fr', 'pt', 'nl', 'pl', 'tr', 'ru'].includes(value.toLowerCase().split(/[-_]/)[0])) || 'en';
    await window.loadURL(origin + '/?locale=' + encodeURIComponent(locale));
    if (smoke) {
      await verifyDesktop();
      app.quit();
    } else window.show();
  }).catch(error => {
    quitting = true;
    if (smoke) {
      const index = process.argv.indexOf('--smoke-result');
      if (index >= 0) fs.writeFileSync(process.argv[index + 1], 'FAIL: ' + error.message);
    }
    stopService();
    if (!smoke) dialog.showErrorBox('Velide could not start', 'The local service could not start. Reinstall Velide or retry.');
    app.exit(1);
  });
  app.on('window-all-closed', () => app.quit());
  app.on('before-quit', () => {
    quitting = true;
    stopService();
  });
}
