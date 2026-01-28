"""
Report generation utilities for the Unified Audit Tool.

Supports multiple output formats:
    - CSV: Detailed results and summary statistics
    - HTML: Interactive reports with filtering
"""

try:
    from reports.csv_export import (
        export_to_csv,
        generate_summary_report,
        export_to_html,
    )
except ImportError:
    export_to_csv = None
    generate_summary_report = None
    export_to_html = None

__all__ = [
    "export_to_csv",
    "generate_summary_report",
    "export_to_html",
]
