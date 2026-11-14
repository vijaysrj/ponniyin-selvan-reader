# Ponniyin Selvan Reader

Static web app (one `index.html` + `data/`), no build step. Live on Vercel; every push to `main` redeploys.
(Vercel, Netlify, GitHub Pages, or `python3 -m http.server`).

- `data/manifest.json`: books, chapter titles, reading minutes, and illustration hints (setting + time of day).
- `data/<book>/<chapter>.json`: `{book, n, title, paras[]}` Tamil text.
- `tools/build_data.py`: rebuilds `data/` from the source corpora:
  - github.com/Rahulvks/Ponniyin-Selvan- (chapter files from chennailibrary.com; Book 1 ch 1–45, Books 2–5 complete)
  - github.com/VeereshElango/text_generation_ponniyin_selvan (clean full text, used for Book 1 ch 46–57)
  - github.com/nitin-varma/Ponniyn-Selvan-RNN-Chatbot-Assignment (PDF text, used only for Book 1 ch 46–57 boundaries)
- Illustrations are drawn in code (SVG) inside index.html; no image files.

## Editing
Edit `src.html`, then run `python3 tools/bundle.py . index.html --standalone` to produce the deployable `index.html` (a full HTML document with the mobile viewport tag). Without `--standalone` it writes the fragment used for the Claude artifact preview. The bundle embeds the manifest and
each book's text (gzip + base64, decoded in the browser with DecompressionStream), because the Claude artifact viewer
did not let the page fetch the separate `data/` files. `data/` remains as a fallback for old browsers.
