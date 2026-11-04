# ScandiOCR leaderboard

The leaderboard, dataset descriptions and prediction comparison are built with Astro
and deployed from this repository to [GitHub Pages](https://v4ldesalnikov.github.io/OCR-eval/).

With Node.js 24 installed:

```sh
cd website
npm ci
npm run dev
```

Open http://localhost:4321/OCR-eval/. Run `npm test` and `npm run build` before publishing.
Pushing changes here to `main` deploys the site through `.github/workflows/deploy-website.yml`.

`public/catalog.json` is the current leaderboard snapshot, including the Danish
Fraktur pilot. `public/results.json` remains the frozen Scandinavian OCR v1 snapshot.
`public/examples/catalog.json` indexes 120 attributed input images (10 per task)
and their saved predictions; `public/examples/index.json` retains the v1 gallery.
Full reports for every model
are stored in [resultsScandiOCReval](https://github.com/V4ldeSalnikov/resultsScandiOCReval).
The website builds from its checked-in snapshot and does not need API credentials.

To publish the completed reports from the local frozen runs, from the evaluator root:

```sh
python scripts/publish_danish_fraktur.py --output ../resultsScandiOCReval
```

This verifies saved references, sample counts and scores, exports public fields, and
updates the report links in the website catalogue and exports the examples. It
preserves the fixed v1 task lists and snapshot. It does not run model inference.
The scripts in `website/scripts/` rebuild aggregate snapshots and the example gallery
from the original local runs; use `--help` for their arguments.
