## Brick viewer catalog repo

Repository contains catalog of LEGO bricks, molds, colors and catalogs.

### Local development

`python3 scripts/serve.py` serves `data/` on `http://localhost:8001/` with CORS, which is where the app's local `settings.json` points. See the app's `docs/testing.md`.

`python3 scripts/build.py` downloads the Rebrickable bulk CSVs into `raw/` and builds the catalog into `data/`. Use `--offline` to reuse `raw/`, `--subset subsets/sample.txt` for a small catalog, and `--out DIR` to write elsewhere. See `docs/refresh.md`.

Catalog data comes from [Rebrickable](https://rebrickable.com/downloads/).
