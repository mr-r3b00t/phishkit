# Safe EML & PDF Viewer

Two self-contained, **offline** tools for safely inspecting emails and PDFs that may be
phishing or malware. Everything is parsed and rendered **locally in your browser** —
nothing is ever uploaded, and nothing in the email or PDF is allowed to execute.

| Page | File | Opens by |
|------|------|----------|
| Landing page | [`index.html`](index.html) | double-click |
| EML viewer | [`eml.html`](eml.html) | double-click |
| PDF viewer / extractor | [`pdf.html`](pdf.html) | double-click |

`index.html` is a landing page that links to both tools — it's also what GitHub Pages serves
at the site root.

---

## Quick start

1. Open `index.html` for the landing page, or go straight to a tool:
2. **Email:** open `eml.html`, then drag an `.eml` file onto the window (or use **Open .eml…**).
3. **PDF:** open `pdf.html`, then drag a `.pdf` onto the window (or use **Open .pdf…**).

No install, no server, no internet connection required. Works on Windows/macOS/Linux in any
modern browser. The two pages link to each other in the top bar.

> **Optional:** for a large/complex PDF you can get a faster (background-worker) parse by
> serving the folder instead of opening `file://` directly:
> ```
> python -m http.server
> ```
> then open `http://localhost:8000/pdf.html`. This is purely a performance option — the
> tools are fully functional from a plain double-click.

---

## EML viewer (`eml.html`)

Parses MIME email (multipart, quoted-printable / base64, charset decoding, RFC 2047 headers)
and shows:

- **Security verdict** — overall ✅ / ⚠️ / ⛔ judgement with itemised findings.
- **Authentication** — parses `Authentication-Results` for **SPF / DKIM / DMARC** pass/fail,
  and flags DMARC `reject` policies.
- **Spoofing checks** — From vs Reply-To mismatch, envelope (Return-Path) mismatch,
  display-name-shows-different-address tricks.
- **Tabs:** Message (rendered HTML), Plain text, **Links**, Raw source.

### How it stays safe
- The HTML body renders inside an **`<iframe sandbox="">` with no `allow-scripts`** — email
  JavaScript can never run, even if sanitisation missed something.
- A strict **Content-Security-Policy** inside the frame blocks all remote resources.
- **Remote images/fonts are blocked by default** (defeats tracking pixels) with an explicit
  opt-in button + warning.
- **Links are non-clickable** in the body; the **Links** tab lists every destination
  (with Proofpoint/`urldefense` and Outlook **SafeLinks** unwrapped) for safe inspection.
- HTML is additionally sanitised (scripts, `<iframe>`/`<object>`/`<form>`, `on*` handlers,
  `javascript:` URLs removed).
- **Attachments** never auto-open; dangerous extensions are flagged and saved as
  `application/octet-stream`.

---

## PDF viewer / extractor (`pdf.html`)

Renders PDF pages and statically extracts/inspects content while treating the file as hostile.

- **Threat verdict** — ✅ / ⚠️ / ⛔ with itemised findings.
- **Structural scan** (pdfid-style, with hex-name de-obfuscation) for auto-action / scripting
  / payload indicators: `/OpenAction`, `/AA`, `/JavaScript`, `/JS`, `/Launch`, `/EmbeddedFile`,
  `/SubmitForm`, `/URI`, `/XFA`, `/RichMedia`, `/ObjStm`, `/Encrypt`, …
- **Link risk** — unwraps gateway links, flags raw-IP hosts, punycode, and commonly-abused
  free hosting (`*.workers.dev`, `*.vercel.app`, `*.pages.dev`, etc.).
- **Tabs:** Pages (rendered), Text, **Links**, **JavaScript** (any embedded script, shown
  inert), Structure (keyword summary + XMP metadata).

### How it stays safe
- **PDF JavaScript never executes.** Pages are drawn to **canvas only** — no annotation /
  forms / XFA layer is built, so links and widgets appear as drawn but are completely inert.
  pdf.js runs with `isEvalSupported:false` and `enableXfa:false`.
- Embedded JavaScript is **extracted and displayed as plain text** — recovered, never run.
- Embedded files save as `application/octet-stream` with dangerous-extension warnings;
  password-protected PDFs are detected and explained rather than blindly opened.

Rendering uses Mozilla **pdf.js 3.11.174**, vendored locally in [`lib/`](lib/) so the tool
stays fully offline. The classic (UMD) build is used so it works from a plain `file://`
double-click (the worker falls back to the main thread when a real Worker can't be spawned).

---

## Files

```
index.html        Landing page (links to both tools; GitHub Pages root)
eml.html          Safe EML viewer (standalone)
pdf.html          Safe PDF viewer / extractor (standalone)
lib/
  pdf.js          Vendored Mozilla pdf.js 3.11.174 (UMD)
  pdf.worker.js   Vendored pdf.js worker (used as main-thread fallback on file://)
README.md         This file
```

### Sample / test files (safe to delete)
```
Message.eml                                       A real phishing sample (spoofed WeTransfer)
TECHNICAL SPECIFICATIONS ... DELIVERY DETAILS.pdf The PDF lure referenced by that email
benign.pdf, malicious.pdf                         Synthetic PDFs for testing detection
make_test_pdfs.py                                 Regenerates the two synthetic PDFs
```

---

## Privacy & limitations

- **Privacy:** all processing is client-side; no file content leaves your machine.
- These tools help you **triage** suspicious files — they reduce risk, they don't guarantee
  safety. Static analysis can't catch everything, and a "clean" verdict is not a green light
  to click links or open attachments you weren't expecting.
- **Never visit a link or open an attachment** found in a suspicious message just because the
  document itself rendered without incident. The viewer deliberately makes links non-clickable
  so you have to make that decision consciously, elsewhere.
