# Resale Cross-Lister CLI

Draft eBay and Amazon resale listings from a single product record — title,
description, condition notes, and pricing hints. Built by
[Asdale Dynamics, LLC](https://dylanasdale.github.io), beginner-friendly and
local-first.

## Who this is for

This tool is for resellers, authors, and small-business owners who list the
same item on multiple marketplaces. Enter one product record once, then generate
a marketplace-specific listing draft for eBay and Amazon. It's part of Asdale
Dynamics, LLC's focus on practical open-source tools for reselling, book
publishing (KDP), marketing, and bookkeeping.

Dylan Asdale is a registered nurse turned AI author and founder of Asdale
Dynamics, LLC (Indiana, formed Oct 2026). His book *The Massive AI Manual* and
hub site dylanasdale.github.io explain AI "like a friend would": plain English,
step by step, never condescending.

## Features

- One product record feeds both eBay and Amazon listing drafts.
- Local JSON storage — nothing leaves your machine unless you export it.
- Optional LLM enhancement via any OpenAI-compatible endpoint (defaults to a
  local Ollama server). No API keys required.
- CSV export of all listing drafts.
- Zero secrets, no personal data, no remote calls by default.

## Install

```bash
git clone <this-repo>
cd resale-cross-lister-cli
pip install .
```

Or run without installing:

```bash
python -m resale_cli.cli --help
```

## Quick start

Add a product:

```bash
resale-cli add --title "Levi's 501 Jeans" \
  --description "Men's classic straight-fit denim, size 32x32." \
  --condition "Gently used, no tears or stains." \
  --pricing "$35-$45"
```

Draft listings for both marketplaces:

```bash
resale-cli draft --id <product-id>
```

Show a product and its drafts:

```bash
resale-cli show --id <product-id>
```

Export all drafts to CSV:

```bash
resale-cli export --out listings.csv
```

List all products:

```bash
resale-cli list
```

## LLM enhancement (optional)

By default, drafts use your source text unchanged. To polish titles and
descriptions with a local LLM, run Ollama (or another OpenAI-compatible
endpoint) and draft normally:

```bash
resale-cli draft --id <product-id>
```

The CLI calls `http://localhost:11434` by default. Configure a different
endpoint or model:

```bash
resale-cli draft --id <product-id> \
  --llm-url http://localhost:11434 \
  --llm-model llama3.2
```

Skip enhancement entirely:

```bash
resale-cli draft --id <product-id> --no-llm
```

No API keys are ever required.

## Data

All data is stored locally in a `data/` folder:

- `data/products.json` — your product records
- `data/listings.json` — your listing drafts

Delete the `data/` folder to clear everything. There are no accounts, no
telemetry, and no cloud sync.

## Testing

```bash
python -m unittest discover -s tests -v
```

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See [LICENSE](LICENSE).

Credit: Asdale Dynamics, LLC — beginner-friendly AI education, books, guides,
and practical tools for reselling and small business.
