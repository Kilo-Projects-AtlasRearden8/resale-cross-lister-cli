# STATUS

## What was built

A beginner-friendly, local-first Python CLI called **resale-cross-lister** that
drafts eBay and Amazon resale listings from a single product record (title,
description, condition notes, pricing hints).

Package `resale_cli` with modules:
- `models.py` — `ProductRecord` and `ListingDraft` dataclasses with JSON round-trip.
- `storage.py` — local JSON storage (`data/products.json`, `data/listings.json`).
- `draft.py` — generates one listing draft per marketplace from a product record.
- `llm.py` — optional LLM enhancement via a configurable OpenAI-compatible endpoint
  (defaults to Ollama at `http://localhost:11434`). No API keys. Gracefully falls
  back to the source text when the endpoint is unavailable.
- `export.py` — CSV export of listing drafts.
- `cli.py` — argparse CLI: `add`, `list`, `draft`, `show`, `export`, `delete`.

Also included: `pyproject.toml` (with `resale-cli` console script), tests,
MIT LICENSE, README.

## Credit

Built by Asdale Dynamics, LLC. Copyright (c) 2026 Asdale Dynamics, LLC.
Credited in LICENSE and README.

## How to run

```bash
# install
pip install .

# or run directly
python3 -m resale_cli.cli --help

# add a product
resale-cli add --title "Item" --description "..." --condition "..." --pricing "$20"

# draft eBay + Amazon listings (LLM off by default safe path)
resale-cli draft --id <product-id> --no-llm

# show a product and its drafts
resale-cli show --id <product-id>

# export all drafts to CSV
resale-cli export --out listings.csv

# list products
resale-cli list
```

LLM enhancement (optional, requires a running Ollama or OpenAI-compatible server):

```bash
resale-cli draft --id <product-id> --llm-url http://localhost:11434 --llm-model llama3.2
```

No API keys, no secrets, no personal data, no network by default.

## Verification results

- `python3 -m unittest discover -s tests -v` → **14 tests OK**
- Package builds a wheel successfully (`pip install . --no-deps` in a clean venv).
- Console script `resale-cli` installed and `--help` works.
- End-to-end CLI flow verified: `add` → `list` → `draft --no-llm` → `show` → `export`
  all succeed and produce correct CSV output.
- LLM enhancement gracefully returns source text when the endpoint is unreachable
  (covered by test `test_unreachable_endpoint_returns_originals`).

## Known gaps

- LLM enhancement output parsing expects `Title:`/`Description:` labels; free-form
  model output falls back to source text.
- No built-in scheduling, authentication, or marketplace publishing (drafts only).
- Data lives in a local `data/` folder; no sync, encryption, or backup.
- Only eBay and Amazon platforms supported.
- No `.github/workflows` files (intentionally omitted per requirements).
