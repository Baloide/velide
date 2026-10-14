const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {
  chromium
} = require('playwright');
const baseURL = process.env.UI_BASE_URL || 'http://127.0.0.1:8766';
(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.BROWSER_EXECUTABLE
  });
  for (const [locale, expected] of [
      ['en-GB', 'en'],
      ['it-IT', 'it'],
      ['pt-BR', 'pt'],
      ['ja-JP', 'en']
    ]) {
    const languageContext = await browser.newContext({
      locale
    });
    const languagePage = await languageContext.newPage();
    await languagePage.goto(baseURL);
    await languagePage.waitForFunction(() => document.querySelector('#processStatus').textContent.length > 0);
    assert.equal(await languagePage.locator('#language').inputValue(), expected);
    await languagePage.locator('#language').selectOption('fr');
    await languagePage.reload();
    assert.equal(await languagePage.locator('#language').inputValue(), 'fr');
    await languageContext.close();
  }
  const context = await browser.newContext({
    viewport: {
      width: 1440,
      height: 1060
    },
    locale: 'it-IT',
    permissions: ['clipboard-read', 'clipboard-write']
  });
  const page = await context.newPage();
  const errors = [];
  const external = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => {
    if (!request.url().startsWith(baseURL)) external.push(request.url());
  });
  await page.goto(baseURL);
  await page.waitForFunction(() => document.querySelector('#processStatus').textContent.length >
    0);
  assert.equal(await page.locator('#rawInput').inputValue(), '');
  assert.equal(await page.locator('#btnCopy').isDisabled(), true);
  // System is the default; explicit overrides survive a reload and ignore OS changes.
  await page.emulateMedia({
    colorScheme: 'dark'
  });
  await page.waitForFunction(() => document.documentElement.dataset.theme === 'dark');
  assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
  await page.locator('#appearance').selectOption('light');
  assert.equal(await page.locator('html').getAttribute('data-theme'), 'light');
  await page.reload();
  assert.equal(await page.locator('#appearance').inputValue(), 'light');
  assert.equal(await page.locator('html').getAttribute('data-theme'), 'light');
  await page.locator('#appearance').selectOption('dark');
  await page.emulateMedia({
    colorScheme: 'light'
  });
  assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
  await page.locator('#appearance').selectOption('system');
  assert.equal(await page.locator('html').getAttribute('data-theme'), 'light');
  await page.emulateMedia({
    colorScheme: 'dark'
  });
  await page.waitForFunction(() => document.documentElement.dataset.theme === 'dark');
  assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
  await page.locator('#appearance').selectOption('light');
  for (const language of ['it', 'en', 'es', 'de', 'fr', 'pt', 'nl', 'pl', 'tr', 'ru']) {
    await page.locator('#language').selectOption(language);
    await page.locator('#btnLoadSample').click();
    await page.waitForFunction(() => !document.querySelector('#btnCopy').disabled);
    assert.equal(await page.locator('html').getAttribute('lang'), language);
    assert.match(await page.locator('#redactedOutput').inputValue(), /\[/);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > window
      .innerWidth), false);
  }
  await page.locator('#language').selectOption('it');
  await page.locator('#btnLoadSample').click();
  await page.waitForFunction(() => !document.querySelector('#btnCopy').disabled);
  await page.locator('#btnCopy').click();
  assert.match(await page.evaluate(() => navigator.clipboard.readText()), /NOME_PAZIENTE/);
  await page.locator('#btnCopyPrompt').click();
  assert.match(await page.evaluate(() => navigator.clipboard.readText()),
    /senza inventare dati mancanti/);
  const [download] = await Promise.all([page.waitForEvent('download'), page.locator(
    '#btnDownload').click()]);
  assert.match(download.suggestedFilename(), /^clinical-redacted-it-/);
  await page.locator('#maskMode').selectOption('PSEUDONYM');
  await page.waitForFunction(() => !document.querySelector('#btnCopy').disabled);
  assert.match(await page.locator('#redactedOutput').inputValue(), /NOME_PAZIENTE_1/);
  await page.locator('#maskMode').selectOption('TAG');
  await page.waitForFunction(() => !document.querySelector('#btnCopy').disabled);
  fs.mkdirSync('screenshots', {
    recursive: true
  });
  await page.locator('#toast').waitFor({
    state: 'hidden'
  });
  await page.screenshot({
    path: 'screenshots/desktop.png',
    fullPage: true
  });
  const beforeTheme = await page.locator('#redactedOutput').inputValue();
  await page.locator('#appearance').selectOption('dark');
  assert.equal(await page.locator('#redactedOutput').inputValue(), beforeTheme);
  assert.equal(await page.locator('#btnCopy').isDisabled(), false);
  // Remove hover and allow the short background transition to finish.
  await page.mouse.move(5, 5);
  await page.waitForTimeout(200);
  assert.equal(await page.locator('#btnDownload').evaluate(el => getComputedStyle(el)
    .backgroundColor), 'rgb(27, 36, 56)');
  await page.screenshot({
    path: 'screenshots/night.png',
    fullPage: true
  });
  await page.locator('#appearance').selectOption('light');
  await page.setViewportSize({
    width: 390,
    height: 844
  });
  for (const language of ['it', 'en', 'es', 'de', 'fr', 'pt', 'nl', 'pl', 'tr', 'ru']) {
    await page.locator('#language').selectOption(language);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > window
      .innerWidth), false);
  }
  await page.locator('#language').selectOption('it');
  await page.waitForFunction(() => !document.querySelector('#btnCopy').disabled);
  await page.screenshot({
    path: 'screenshots/mobile.png',
    fullPage: true
  });
  await page.setViewportSize({
    width: 1440,
    height: 1060
  });
  // Treat hostile document values as plain text; never execute them as HTML.
  const hostile = '<img src=x onerror="window.__injected=1">';
  await page.locator('#customKeywords').fill(hostile);
  await page.locator('#rawInput').fill(hostile);
  await page.waitForFunction(() => !document.querySelector('#btnCopy').disabled);
  await page.locator('#entitiesSection').evaluate(el => el.open = true);
  assert.equal(await page.locator('#entitiesChips img').count(), 0);
  assert.equal(await page.evaluate(() => window.__injected), undefined);
  assert.equal(await page.locator('#redactedOutput').inputValue(), '[DATO_RISERVATO]');
  // Immediately invalidate stale output and handle a failed request visibly.
  await page.route('**/api/redact/text', route => route.fulfill({
    status: 500,
    body: 'failed'
  }));
  await page.locator('#rawInput').fill('Paziente: Maria Verdi');
  assert.equal(await page.locator('#btnCopy').isDisabled(), true);
  await page.waitForFunction(() => document.querySelector('#processStatus').classList.contains(
    'error'));
  assert.equal(await page.locator('#redactedOutput').inputValue(), '');
  await page.unroute('**/api/redact/text');
  // A delayed response cannot overwrite a cleared document.
  await page.route('**/api/redact/text', async route => {
    await new Promise(resolve => setTimeout(resolve, 700));
    try {
      await route.continue();
    } catch {}
  });
  await page.locator('#rawInput').fill('Paziente: Maria Verdi');
  await page.waitForTimeout(300);
  await page.locator('#btnClear').click();
  await page.waitForTimeout(900);
  assert.equal(await page.locator('#redactedOutput').inputValue(), '');
  assert.equal(await page.locator('#rawInput').inputValue(), '');
  assert.equal(await page.locator('#btnCopy').isDisabled(), true);

  // Import real documents through the file picker and redact automatically.
  await page.locator('#btnClear').click();
  for (const name of ['note.pdf', 'note.docx']) {
    await page.locator('#fileInput').setInputFiles(path.join('build', 'upload-fixtures', name));
    await page.waitForFunction(() => !document.querySelector('#btnCopy').disabled);
    assert.match(await page.locator('#rawInput').inputValue(), /Mario Rossi/);
    assert.doesNotMatch(await page.locator('#redactedOutput').inputValue(), /Mario Rossi/);
    assert.equal(await page.locator('#importNotice').isVisible(), true);
  }
  assert.match(await page.locator('#rawInput').inputValue(), /135\/85/);
  await page.locator('#fileInput').setInputFiles(path.join('build', 'upload-fixtures',
    'partial.pdf'));
  await page.waitForFunction(() => !document.querySelector('#btnCopy').disabled);
  assert.match(await page.locator('#importNotice').textContent(), /Alcune pagine/);
  // Drag-and-drop also uses the local extraction API. Never render a source filename.
  const dragData = await page.evaluateHandle(() => {
    const transfer = new DataTransfer();
    transfer.items.add(new File(['Paziente: Mario Rossi'], 'private-name.txt', {
      type: 'text/plain'
    }));
    return transfer;
  });
  await page.dispatchEvent('#inputPanel', 'drop', {
    dataTransfer: dragData
  });
  await page.waitForFunction(() => !document.querySelector('#btnCopy').disabled);
  assert.match(await page.locator('#redactedOutput').inputValue(), /NOME_PAZIENTE/);
  assert.doesNotMatch(await page.locator('#importStatus').textContent(), /private-name/);
  // Text and Markdown, plus a rejected legacy Word file and a corrupt PDF.
  await page.locator('#fileInput').setInputFiles({
    name: 'note.md',
    mimeType: 'text/markdown',
    buffer: Buffer.from('Paziente: Maria Verdi')
  });
  await page.waitForFunction(() => !document.querySelector('#btnCopy').disabled);
  assert.doesNotMatch(await page.locator('#redactedOutput').inputValue(), /Maria Verdi/);
  for (const name of ['old.doc', 'broken.pdf']) {
    await page.locator('#fileInput').setInputFiles({
      name,
      mimeType: 'application/octet-stream',
      buffer: Buffer.from('broken')
    });
    await page.waitForFunction(() => document.querySelector('#importStatus').classList.contains(
      'error'));
    assert.match(await page.locator('#rawInput').inputValue(), /Maria Verdi/);
    assert.equal(await page.locator('#btnCopy').isDisabled(), true);
  }

  // Reproduce a stale backend that serves the new static UI but lacks ingestion.
  await page.route('**/api/ingest/file?*', route => route.fulfill({
    status: 404,
    contentType: 'application/json',
    body: JSON.stringify({
      detail: 'Not Found'
    })
  }));
  await page.locator('#fileInput').setInputFiles({
    name: 'note.txt',
    mimeType: 'text/plain',
    buffer: Buffer.from('Paziente: Mario Rossi')
  });
  await page.waitForFunction(() => document.querySelector('#importStatus').classList.contains(
    'error'));
  assert.match(await page.locator('#importStatus').textContent(), /versione precedente/);
  assert.match(await page.locator('#processStatus').textContent(), /Caricamento interrotto/);
  assert.notEqual(await page.locator('#importStatus').textContent(), await page.locator(
    '#processStatus').textContent());
  assert.equal(await page.locator('#btnCopy').isDisabled(), true);
  await page.unroute('**/api/ingest/file?*');

  // A delayed file import must never repopulate a cleared editor.
  await page.route('**/api/ingest/file?*', async route => {
    await new Promise(resolve => setTimeout(resolve, 700));
    try {
      await route.continue();
    } catch {}
  });
  await page.locator('#fileInput').setInputFiles({
    name: 'note.txt',
    mimeType: 'text/plain',
    buffer: Buffer.from('Paziente: Mario Rossi')
  });
  await page.waitForFunction(() => document.querySelector('#fileDropZone').getAttribute(
    'aria-busy') === 'true');
  await page.locator('#btnClear').click();
  await page.waitForTimeout(900);
  assert.equal(await page.locator('#rawInput').inputValue(), '');
  assert.equal(await page.locator('#redactedOutput').inputValue(), '');
  await page.unroute('**/api/ingest/file?*');
  // Upload messages are translated, with no horizontal overflow in any language.
  for (const language of ['it', 'en', 'es', 'de', 'fr', 'pt', 'nl', 'pl', 'tr', 'ru']) {
    await page.locator('#language').selectOption(language);
    await page.locator('#fileInput').setInputFiles({
      name: 'wrong.doc',
      mimeType: 'application/octet-stream',
      buffer: Buffer.from('broken')
    });
    assert.equal(await page.locator('#importStatus').isVisible(), true);
    assert.doesNotMatch(await page.locator('#importStatus').textContent(), /undefined/);
    await page.setViewportSize({
      width: 390,
      height: 844
    });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > window
      .innerWidth), false);
    await page.setViewportSize({
      width: 1440,
      height: 1060
    });
  }
  await page.locator('#language').selectOption('it');
  await page.locator('#fileInput').setInputFiles(path.join('build', 'upload-fixtures',
    'note.docx'));
  await page.waitForFunction(() => !document.querySelector('#btnCopy').disabled);
  await page.locator('#appearance').selectOption('light');
  await page.mouse.move(5, 5);
  await page.waitForTimeout(200);
  await page.screenshot({
    path: 'screenshots/import.png',
    fullPage: true
  });
  await page.locator('#appearance').selectOption('dark');
  await page.mouse.move(5, 5);
  await page.waitForTimeout(200);
  await page.screenshot({
    path: 'screenshots/import-night.png',
    fullPage: true
  });

  // Reproduce the roster and author-list layout reported by the user.
  await page.locator('#btnClear').click();
  await page.locator('#rawInput').fill(
    'Problem Statement\nNome\tMatricola\nLa Magna Davide\t0512121375\nCiccarelli Raffaele\t0512121405\nManzolillo Matteo\t0512121666\nScritto da: Ciccarelli Raffaele, La Magna Davide, Manzolillo Matteo\nRevision History'
  );
  await page.waitForFunction(() => !document.querySelector('#btnCopy').disabled);
  const corrected = await page.locator('#redactedOutput').inputValue();
  for (const name of ['La Magna Davide', 'Ciccarelli Raffaele', 'Manzolillo Matteo']) assert
    .equal(corrected.includes(name), false);
  assert.equal(corrected.includes('[TELEFONO]'), false);
  assert.equal((corrected.match(/\[ID_CARTELLA\]/g) || []).length, 3);
  assert.equal(corrected.includes('Problem Statement'), true);

  // CV excerpt: preserve training, mask the whole wrapped link and the profile owner.
  await page.locator('#btnClear').click();
  await page.locator('#rawInput').fill(
    'Contatta\nwww.linkedin.com/in/giampiero-\nbartolomei-314046224 (LinkedIn)\nCompetenze principali\nPrototipazione rapida\nDispositivi Medici\nCorso di Formazione Generale e\nSpecifica per Lavoratori\nGiampiero Bartolomei\nBioEngineer Specialist & Researcher at Math Biology\nRoma, Lazio, Italia'
  );
  await page.waitForFunction(() => !document.querySelector('#btnCopy').disabled);
  const profileResult = await page.locator('#redactedOutput').inputValue();
  assert.equal(profileResult.includes('Giampiero Bartolomei'), false);
  assert.equal(profileResult.includes('linkedin.com'), false);
  assert.equal(profileResult.includes('[TELEFONO]'), false);
  assert.equal(profileResult.includes('Corso di Formazione Generale e'), true);
  assert.equal(profileResult.includes('Roma, Lazio, Italia'), false);
  assert.equal(profileResult.includes('Dispositivi Medici'), true);
  await page.mouse.move(5, 5);
  await page.waitForTimeout(200);
  await page.screenshot({
    path: 'screenshots/profile-recognition.png',
    fullPage: true
  });

  assert.deepEqual(errors, []);
  assert.deepEqual(external, []);
  await browser.close();
  console.log(
    'UI verified: ten languages, day/night/system, persistence, desktop/mobile, clipboard, TXT, pseudonyms, custom terms, injection, errors, stale responses, PDF/DOCX/TXT/MD picker/drop, partial PDFs, import errors/cancellation, no external requests.'
  );
})().catch(error => {
  console.error(error);
  process.exit(1);
});
