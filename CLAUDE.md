# Site Audit Tool

Python CLI tool for auditing websites for design system compliance, SEO, and content issues.

## Quick Start

```bash
# Audit a single site
python main.py https://example.com --site ~/sites/example.com --all

# Run specific audit type
python main.py https://example.com --site ~/sites/example.com --type design

# List reports for a site
python main.py --site ~/sites/example.com --list-reports
```

## Architecture

```
main.py              # CLI entry point (argparse)
├── engine.py        # AuditEngine - crawls pages, orchestrates plugins
├── config.py        # DEFAULT_MAX_PAGES, RATE_LIMIT, EXCLUDED_PATTERNS
├── plugins/
│   ├── audit_design.py   # DesignAuditor - checks design system compliance
│   ├── audit_seo.py      # SEOAuditor - meta tags, headings, links
│   └── audit_content.py  # ContentAuditor - text quality checks
└── reports/
    └── csv_export.py     # Report generation and file output
```

## Data Flow

1. `main.py` parses args, loads site config from `~/sites/{domain}/palette.py`
2. `AuditEngine` crawls the site, calls each plugin per page
3. Plugins return audit results as **list of dicts** (not a single dict)
4. `csv_export.py` writes reports to `{site_path}/reports/`

## Key Exports from csv_export.py

```python
from reports.csv_export import (
    generate_all_reports,    # Main entry point for report generation
    get_site_report_dir,     # Returns {site_path}/reports/
    get_reports_base_dir,    # Resolves report directory from URL or path
)
```

## Known Issues

- **Results are a LIST**: `main.py` passes plugin results as a list of audit findings, not a dict. Functions expecting `results['items']` will fail.
- Zone.Identifier files appear in WSL - these are Windows artifacts, ignored via .gitignore

## Site Configuration

Site configs live outside this repo at `~/sites/{domain}/`:
```
~/sites/example.com/
├── palette.py       # Design tokens (colors, fonts, spacing)
├── reports/         # Generated audit reports
└── assets/          # Site-specific assets
```

## Tech Stack

- Python 3.11 (via asdf)
- BeautifulSoup4 for HTML parsing
- No database - file-based reports (CSV, HTML)
