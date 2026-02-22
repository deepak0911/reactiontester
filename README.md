# Competitor Feature Comparison Tool

A tool that discovers top competitors for any company, scrapes their product features from the web, and generates a structured side-by-side comparison — powered by Claude API. Available as both a CLI and a web UI.

## How It Works

1. **Competitor Discovery** — Searches the web (via DuckDuckGo) for competitor information, then uses Claude to identify the top N competitors with their websites.
2. **Feature Extraction** — Scrapes each company's website (homepage, `/features`, `/pricing`, `/product` pages) plus search results, then uses Claude to extract structured feature data organized by category and tier (core/premium/enterprise).
3. **Feature Comparison** — Sends all feature data to Claude for cross-company analysis, producing a unified feature matrix, unique advantages per company, feature gaps, and a competitive positioning summary.
4. **Output** — Displays rich formatted tables in the terminal and saves full JSON results to disk.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Anthropic API key
cp .env.example .env
# Edit .env and add your key
```

## Web UI

Launch the web interface to analyze competitors from your browser:

```bash
python -m src.webapp
```

Then open [http://localhost:5000](http://localhost:5000). Enter a company's website URL and name, pick how many competitors to analyze, and click **Analyze Competitors**. The UI shows real-time progress and renders the full comparison — competitor cards, feature breakdowns, comparison matrix, unique advantages, gaps, and a positioning summary.

## CLI Usage

```bash
# Basic usage
python -m src.main "Slack"

# With explicit company URL and top 3 competitors
python -m src.main "Slack" --company-url https://slack.com --top-n 3

# JSON-only output (for piping to other tools)
python -m src.main "Notion" --json-only

# Custom output directory
python -m src.main "Figma" --output-dir ./reports

# Verbose logging
python -m src.main "Stripe" -v
```

## CLI Options

| Option | Description | Default |
|---|---|---|
| `company` | Name of the target company (required) | — |
| `--company-url` | Website URL (auto-guessed if omitted) | `https://www.<company>.com` |
| `--top-n` | Number of competitors to analyze | 5 |
| `--output-dir` | Directory for JSON output files | `output/` |
| `--json-only` | Print raw JSON instead of tables | off |
| `-v, --verbose` | Enable debug logging | off |

## Output Files

Results are saved as three JSON files in the output directory:

- `<company>_competitors.json` — Discovered competitors with URLs and descriptions
- `<company>_features.json` — Extracted features per company, organized by category
- `<company>_comparison.json` — Full comparison matrix with gaps and advantages

## Architecture

```
src/
├── main.py               # CLI entry point and orchestration
├── webapp.py             # Flask web UI with async job processing
├── competitor_finder.py   # Discover competitors via search + Claude
├── feature_extractor.py   # Scrape and extract features via Claude
├── feature_comparator.py  # Cross-company comparison via Claude
├── output_formatter.py    # Rich terminal output and JSON export
├── web_scraper.py         # HTTP fetching and search utilities
├── templates/
│   ├── index.html        # Input form with live progress
│   └── results.html      # Server-rendered results page
└── static/
    └── style.css         # Dark-themed responsive styles
```

## Requirements

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/)
