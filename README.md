# Velide by Baloide

**Current release: v1.0.0**

<img src="branding/velide-logo.png" width="112" alt="Velide logo">

**Protect personal information. Keep the context.**

Velide is a local document de-identification app for clinical notes and other sensitive text. Import a document, compare the original with the masked result, review the detections, and copy or export the text. The Windows app uses **Electron and the same interface as the browser version**, including its branding, day/night/system themes and document import tools.

## Download for Windows

| Package | Download | Best for |
| :--- | :--- | :--- |
| **Windows installer · x64** | [Download Velide-Setup.exe](https://github.com/Baloide/velide/releases/latest/download/Velide-Setup.exe) | Recommended: installs for your account and creates desktop and Start menu shortcuts. No Python or Node.js required. |
| **Portable app · x64** | [Download Velide-Windows.zip](https://github.com/Baloide/velide/releases/latest/download/Velide-Windows.zip) | Extract the entire ZIP and run `Velide.exe`. Keep all included folders together. |
| **Installer checksum** | [SHA-256](https://github.com/Baloide/velide/releases/latest/download/Velide-Setup.exe.sha256) | Verify the installer before running it. |
| **Portable checksum** | [SHA-256](https://github.com/Baloide/velide/releases/latest/download/Velide-Windows.zip.sha256) | Verify the ZIP before extracting it. |
| **Source code** | [Browse the repository](https://github.com/Baloide/velide) | Run, inspect or build the project yourself. |

**Release status:** these links become available after the repository owner publishes a GitHub Release containing the files named above. A GitHub source-code ZIP is not the ready-to-run Windows app. Local build outputs are in `dist/`; this folder is excluded from Git and its files must be uploaded as release assets.

The Windows packages bundle Electron, Python and the document parsers. Internet is needed to download the package, but document processing works offline. The current packages are unsigned; Windows or organizational policies may require an additional trust check. Linux and macOS binaries are not provided.

### Install, update and remove

- **Installer:** run `Velide-Setup.exe`, then open **Velide** from your desktop or Start menu. Installation is per user and does not request administrator access. Close Velide before running a newer installer. Uninstall through Windows **Settings → Apps**.
- **Portable:** extract all files and run `Velide.exe`. To create a desktop shortcut without the installer, run `Install.cmd`; it copies the complete app to `%LOCALAPPDATA%\Baloide\ClinicalRedactor`. To update, close the app and repeat with a fresh ZIP. To remove this optional installation, delete that folder and its desktop shortcut.
- Close the Electron window to stop its private local service. A second launch focuses the existing window.
- Language/theme preferences are stored locally; documents are not automatically saved. Uninstalling the installer preserves Electron preferences in `%APPDATA%\Velide` unless you remove that folder yourself.

Verify a download in PowerShell:

```powershell
Get-FileHash .\Velide-Setup.exe -Algorithm SHA256
```

Compare the result with the corresponding `.sha256` file from the same release.

## Language and appearance

Supported languages: **English, Italian, Spanish, German, French, Portuguese, Dutch, Polish, Turkish and Russian**.

An explicitly saved language takes priority. Otherwise Velide selects the first supported system/browser language, including regional forms such as `en-GB`, `pt-BR` or `de-DE`. If no supported language can be detected, it uses **English**. Electron supplies the operating system's language preferences; the browser version uses the browser's preference list. Select the **document's language** before processing: this choice also controls recognition rules, replacement labels, examples and the AI prompt.

- **System** is the default appearance and follows the device's light/dark preference.
- **Day** uses light surfaces with cobalt blue accents.
- **Night** uses dark blue surfaces with periwinkle accents.

Appearance is applied before the page is drawn to reduce a bright flash at startup. Changing it does not alter the document. Preferences are associated with the local origin; a fallback service port can have separate browser preferences.

## How to use Velide

1. Choose the document language and appearance.
2. Drop a digital PDF, DOCX, TXT or Markdown file into the original-text panel, select **Choose file**, paste text, or load a fictional example. No document is loaded automatically at startup.
3. Select the categories to detect and a masking mode.
4. Add any additional names, places or phrases, one per line. These terms are masked case-insensitively even when other categories are disabled.
5. Compare both panels and open **Review replacements**. That list contains original sensitive values: take care when sharing your screen.
6. Use **Copy text**, **Save .txt**, or **Copy for AI**. The AI button only prepares clipboard text; it does not contact ChatGPT, Claude or another service.
7. Use **Clear** to empty the document, result and additional terms.

Processing starts after a short typing pause. Edits invalidate the previous result immediately; export remains disabled until a current response is available. Cancelled or outdated requests cannot overwrite newer work. An import failure preserves the previous original text and displays an error.

### Masking modes

| Mode | English example | Behavior |
| :--- | :--- | :--- |
| `TAG` | `[PATIENT_NAME]` | Localized semantic label. |
| `PSEUDONYM` | `PATIENT_NAME_1` | Consistent replacement of matching values within the current request. |
| `BLOCK` | `████████` | Text blocks with a capped length. |
| `ASTERISK` | `********` | Asterisks with a capped length. |

Pseudonyms reset between requests and are not realistic invented identities. Blocks and asterisks replace text; they do not redact the visual content of the original PDF.

## Document import

| Format | Imported content | Important limitations |
| :--- | :--- | :--- |
| **Digital PDF** | Extractable page text | Up to 200 pages. Columns, layout and reading order may change. Encrypted PDFs are rejected. |
| **DOCX** | Paragraphs, nested tables, headers and footers | Images, footnotes, text boxes, content controls and tracked revisions may not be imported. |
| **TXT / Markdown** | Plain text, including Markdown markers | UTF-8 with or without BOM, UTF-16 with BOM, or Windows-1252. Convert other encodings first. |

Only one document is imported at a time. The original file is never modified. Export produces plain text, not a revised PDF or Word document.

Limits: **10 MiB per upload**, **200,000 extracted characters**, **1,000 DOCX ZIP components**, **30 MiB declared expanded DOCX content**, and **20 levels of nested Word tables**. PDF decoder/page-content output is limited to 5 MiB; additional decoding-work, page-tree and XObject budgets are applied. These budgets do not constitute a total process RAM/CPU quota.

PDFs with no extractable text report that OCR may be needed. Mixed PDFs warn about pages without text; check the original because these may be blank or scanned pages. Unsupported or corrupt files show a localized error. OCR, legacy `.doc`, batch import and in-place PDF redaction are not implemented.

Parsing uses [pypdf](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) and [python-docx](https://python-docx.readthedocs.io/en/latest/api/document.html).

## Recognition and review

Velide uses regular expressions and contextual rules, **not an AI or general-purpose NER model**. It recognizes some labeled names, professional titles, explicit name tables and author lists; matching repetitions; contact details and complete URLs; numeric/text dates; labeled national or clinical identifiers; and some address/facility/location patterns. Italian tax-code patterns and some country-specific identifiers are supported, but not every national variant. Codes are detected rather than validated.

Table-aware rules recognize names and enrollment identifiers separately. CV/profile rules use explicit cues such as LinkedIn profile paths or a name followed by a known profession. Overlapping detections are merged. Additional terms help cover values outside these rules.

**Always review before sharing.** Unlabeled names, indirect identifying details, unusual addresses and mixed-language documents can retain personal information. False positives can also remove useful content. Automatic masking does not guarantee anonymity, GDPR/HIPAA compliance or suitability for a particular clinical workflow.

## Privacy model

- Processing occurs on the user's computer. Electron loads the local interface and launches a private Python service bound to `127.0.0.1`, normally port `8760`, with a free-port fallback.
- Uploaded bytes are streamed into memory without application-created upload files. Original document content is not deliberately written to a database, document history or application logs.
- Fonts, scripts, styles and logos are bundled. Electron blocks external page navigation, popups and external network requests from its application session. The renderer uses a sandbox, context isolation and no Node.js integration.
- The web API sends `Cache-Control: no-store`, a restrictive Content Security Policy and trusted-host checks. These measures do not erase browser history, operating-system swap, crash dumps or clipboard history.
- Clipboard contents and exported files remain under the user's and operating system's control. Review detections and full API responses contain original sensitive values.
- The service has no user authentication or parser process isolation/resource quota. Do not expose it to a network or treat it as a multiuser hosted service.
- No remote AI service, telemetry or automatic document upload is configured. Updating dependencies and distributing signed binaries remain maintenance responsibilities.

## Run from source

Requires Python **3.11+**. The desktop app additionally requires **Node.js 22.12+ and npm**. Internet is needed for the initial dependency installation. Run commands from the repository root.

### Electron desktop on Windows

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
cd desktop/electron
npm ci
npm start
```

`run.bat` performs the Windows setup and starts Electron. Packaged users do not need these development tools.

### Browser interface

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
backend/.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --no-access-log
```

On Linux/macOS use `python3` and `backend/.venv/bin/python`. Open `http://127.0.0.1:8000`; stop the server with `Ctrl+C`. Restart after changing Python code. Reloading the page only refreshes frontend assets.

```bash
docker compose up --build -d
docker compose down
```

Docker exposes the service on loopback only. Its image does not automatically include a Windows release ZIP.

## Build Windows packages

Build on Windows x64 with Python, Node.js and npm:

```powershell
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt -r desktop/requirements-build.txt
backend/.venv/Scripts/python.exe scripts/build_windows.py
```

Alternatively run `build-windows.bat`. The build freezes the private service with PyInstaller, packages Electron with electron-builder, runs a check inside the actual Electron executable, creates a portable ZIP and checks desktop-shortcut installation in project-local test folders. A failed desktop check prevents creation of a new portable ZIP. Electron dependencies are pinned in `package-lock.json`.

| Output | Purpose |
| :--- | :--- |
| `dist/Velide-Setup.exe` | Per-user Windows installer with desktop and Start menu shortcuts. |
| `dist/Velide-Windows.zip` | Complete portable Electron app and optional shortcut installer. |
| `dist/*.sha256` | SHA-256 checksums of both release assets. |
| `dist/electron/win-unpacked/` | Unpacked application for local inspection. |

### Publish on GitHub

See [RELEASING.md](RELEASING.md) for first publication, annotated Git tags and future version updates.

Publication is manual. Create `Baloide/velide`, push the source, and create a release for the matching version. Upload **both packages and both `.sha256` files** listed above. The download table uses GitHub's latest release links, so keep the asset names unchanged. Do not upload real documents, logs, development environments or test profiles. `dist/`, `build/` and `node_modules/` are ignored.

## Development and quality checks

```powershell
backend/.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
backend/.venv/Scripts/python.exe -m unittest discover -s tests -v
backend/.venv/Scripts/python.exe -m ruff check backend/app desktop scripts tests
backend/.venv/Scripts/python.exe -m ruff format --check backend/app desktop scripts tests
backend/.venv/Scripts/python.exe scripts/format_javascript.py --check
node --check desktop/electron/main.cjs
```

Python tests use synthetic documents and cover ingestion, defensive parser limits, recognition, repeated names, masking modes and API validation. `scripts/verify_ui.cjs` uses Playwright to exercise the browser interface, including themes, clipboard/export, ten languages, uploads, failures and stale responses. Set `UI_BASE_URL` and optionally `BROWSER_EXECUTABLE`; generate its synthetic fixtures first with `backend/.venv/Scripts/python.exe scripts/create_ui_fixtures.py`. The Windows build checks the packaged Electron renderer, private service, branding, themes, masking and TXT import. These checks prevent known regressions; they are not accuracy certification.

See [ARCHITECTURE.md](ARCHITECTURE.md) for extension points, data contracts and contribution guidance. The GitHub checks workflow runs Python tests and style/syntax checks when the repository is published.

## API reference

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| GET | `/api/health` | Service name, status and version. |
| GET | `/api/sample?language=en` | Fictional localized example; English default. |
| POST | `/api/ingest/file?format=pdf` | Raw binary import: `pdf`, `docx`, `txt`, `md`. |
| POST | `/api/redact/text` | De-identification with selected options. |
| GET | `/api/downloads` | Local ZIP availability, or `windows: null`. |
| GET | `/download/windows` | Local Windows ZIP, or 404 when not built. |

```json
{
  "text": "Patient: James Smith",
  "options": {
    "language": "en",
    "mask_mode": "TAG",
    "redact_names": true,
    "redact_tax_codes": true,
    "redact_dates": true,
    "redact_contacts": true,
    "redact_locations": true,
    "redact_ids": true,
    "custom_keywords": []
  }
}
```

Options default to English, `TAG`, all categories enabled and no additional terms. Responses include `redacted_text`, `entities_found`, `entities` and `execution_ms`. Entity offsets are Python Unicode indices into the original text, with an exclusive end. The complete response contains original values: share only the reviewed result. Invalid languages, modes or text lengths return 422.

## Troubleshooting

- **Import fails:** ensure the supported file is within limits and the local service is current. Check `/api/health` in browser mode; restart after backend changes.
- **A name remains visible:** select the right document language, add the missing term and review the entire result.
- **Clipboard is unavailable:** select/copy the output manually or save `.txt`.
- **Old Windows appearance:** close the previous app and install the latest Electron package. Old native/Tk builds are superseded.
- **PowerShell shortcut installation is blocked:** run the portable `Velide.exe` directly, or use the standard installer subject to your organization's policies.

## Copyright and license

<img src="branding/baloide-logo.png" width="40" alt="Baloide logo">

**Made by Baloide. Copyright © 2026 Baloide. All rights reserved.**

An explicit source-code license has not yet been selected. Public repository visibility does not grant an open-source license. Choose and add a `LICENSE` before inviting contributions or advertising the project as open source. Bundled third-party dependencies retain their own licenses and notices.
