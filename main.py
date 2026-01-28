"""
================================================================================
MAIN.PY - Unified Audit Tool CLI Entry Point
================================================================================
Command-line interface for running website audits with automatic organization
of reports into site-specific subdirectories.

Usage:
    python main.py <url> --site <path> [options]

Examples:
    # Run all audits on a site
    python main.py https://lastingchange.co --site ~/sites/lastingchange.co --all

    # Run only design audit
    python main.py https://lastingchange.co --site ~/sites/lastingchange.co --type design

    # Run SEO audit with custom max pages
    python main.py https://lastingchange.co --site ~/sites/lastingchange.co --type seo --max-pages 20

    # Audit staging site using production config
    python main.py https://staging.lastingchange.co --site ~/sites/lastingchange.co --all

    # List all reports for a site
    python main.py --site ~/sites/lastingchange.co --list-reports

Reports are automatically saved to:
    <site_path>/reports/audit_<type>_<timestamp>.csv
    <site_path>/reports/audit_<type>_<timestamp>_summary.csv
    <site_path>/reports/audit_<type>_<timestamp>.html

Author: Built with Claude in BoodleBox
Date: January 2026
================================================================================
"""

import argparse
import sys
import os
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urlparse

# Import core modules
from engine import AuditEngine
from config import DEFAULT_MAX_PAGES, DEFAULT_RATE_LIMIT, EXCLUDED_PATTERNS

# Import plugins
from plugins.audit_design import DesignAuditor
from plugins.audit_seo import SEOAuditor
from plugins.audit_content import ContentAuditor

# Import report generators (updated with site-specific directories)
from reports.csv_export import (
    generate_all_reports,
    get_site_report_dir,
    get_reports_base_dir
)


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def get_site_name(url: str) -> str:
    """
    Extract a clean site name from a URL for display purposes.

    Args:
        url: The URL to extract the domain from

    Returns:
        Clean domain name (e.g., "lastingchange.co")
    """
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    # Handle edge cases
    if not domain:
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]

    # Remove www. prefix
    if domain.startswith("www."):
        domain = domain[4:]

    return domain or "unknown_site"


def list_site_reports(url: str = None, site_path: str = None) -> List[str]:
    """
    List all audit reports for a specific site.

    Args:
        url: The site URL to list reports for (used if site_path not provided)
        site_path: Direct path to site directory

    Returns:
        List of report file paths, sorted newest first
    """
    if site_path:
        site_dir = os.path.join(site_path, 'reports')
    else:
        site_name = get_site_name(url) if url else "unknown"
        reports_base = get_reports_base_dir(url, site_path)
        site_dir = os.path.join(reports_base, site_name)

    if not os.path.exists(site_dir):
        return []

    reports = []
    for file in os.listdir(site_dir):
        if file.startswith("audit_") or file.endswith(".csv"):
            filepath = os.path.join(site_dir, file)
            reports.append(filepath)

    # Sort by modification time, newest first
    reports.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    return reports


def list_all_sites(base_sites_dir: str = None) -> List[str]:
    """
    List all sites that have audit reports.

    Args:
        base_sites_dir: Base directory containing site folders (e.g., ~/sites)

    Returns:
        List of site domain names with existing reports
    """
    if base_sites_dir and os.path.exists(base_sites_dir):
        sites = []
        for item in os.listdir(base_sites_dir):
            item_path = os.path.join(base_sites_dir, item)
            reports_path = os.path.join(item_path, 'reports')
            # Only include directories that have a reports subfolder
            if os.path.isdir(item_path) and os.path.exists(reports_path):
                sites.append(item)
        return sorted(sites)
    
    # Fallback to old behavior
    reports_base = "reports"
    if not os.path.exists(reports_base):
        return []

    sites = []
    for item in os.listdir(reports_base):
        item_path = os.path.join(reports_base, item)
        # Only include directories (not files like csv_export.py)
        if os.path.isdir(item_path) and not item.startswith("__"):
            sites.append(item)

    return sorted(sites)


def print_reports_summary(url: str = None, site_path: str = None):
    """
    Print a summary of available reports.

    Args:
        url: Optional URL to filter reports for a specific site
        site_path: Optional direct path to site directory
    """
    if site_path or url:
        # List reports for a specific site
        site_name = os.path.basename(site_path) if site_path else get_site_name(url)
        reports = list_site_reports(url, site_path)

        if not reports:
            print(f"\n📁 No reports found for {site_name}")
            if site_path:
                print(f"   Reports directory: {os.path.join(site_path, 'reports')}")
            return

        print(f"\n📁 Reports for {site_name}:")
        print("-" * 60)

        for report in reports:
            filename = os.path.basename(report)
            mtime = datetime.fromtimestamp(os.path.getmtime(report))
            size = os.path.getsize(report)
            print(f"  {filename}")
            print(f"    Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    Size: {size:,} bytes")
            print()

    else:
        # List all sites with reports
        # Try ~/sites as default base
        home = os.path.expanduser("~")
        base_sites_dir = os.path.join(home, "sites")
        
        sites = list_all_sites(base_sites_dir)

        if not sites:
            print("\n📁 No audit reports found.")
            print("   Run an audit to generate reports:")
            print("   python main.py https://example.com --site ~/sites/example.com --all")
            return

        print("\n📁 Sites with audit reports:")
        print("-" * 60)

        for site in sites:
            site_dir = os.path.join(base_sites_dir, site, 'reports')
            if os.path.exists(site_dir):
                report_count = len([f for f in os.listdir(site_dir) if f.endswith('.csv')])
                print(f"  {site} ({report_count} reports)")

        print("\nTo see reports for a specific site:")
        print("  python main.py --site ~/sites/example.com --list-reports")


def load_site_palette(site_path: str):
    """
    Dynamically load palette.py from a site directory.

    Args:
        site_path: Path to the site directory containing palette.py

    Returns:
        The loaded palette module, or None if not found
    """
    palette_path = os.path.join(site_path, 'palette.py')
    
    if not os.path.exists(palette_path):
        print(f"⚠️ No palette.py found at {palette_path}")
        return None
    
    import importlib.util
    spec = importlib.util.spec_from_file_location("palette", palette_path)
    palette_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(palette_module)
    
    return palette_module


# ==============================================================================
# MAIN FUNCTION
# ==============================================================================

def main():
    """
    Main entry point for the Unified Audit Tool.
    Parses command-line arguments and runs the appropriate audits.
    """

    # =========================================================================
    # ARGUMENT PARSING
    # =========================================================================

    parser = argparse.ArgumentParser(
        description="Unified Audit Tool - Crawl and audit websites for design, SEO, and content issues.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py https://lastingchange.co --site ~/sites/lastingchange.co --all
  python main.py https://lastingchange.co --site ~/sites/lastingchange.co --type design
  python main.py https://staging.example.com --site ~/sites/example.com --all
  python main.py --site ~/sites/lastingchange.co --list-reports
  python main.py --list-sites

Reports are saved to: <site_path>/reports/
        """
    )

    # URL argument (optional if just listing)
    parser.add_argument(
        "url",
        nargs="?",
        default=None,
        help="The starting URL to crawl (e.g., https://lastingchange.co)"
    )

    # Site path argument (NEW - required for site-based architecture)
    parser.add_argument(
        "--site", "-s",
        default=None,
        help="Path to site directory containing palette.py and reports folder (e.g., ~/sites/lastingchange.co)"
    )

    # Audit type selection
    parser.add_argument(
        "--type", "-t",
        choices=["design", "seo", "content", "all"],
        default="all",
        help="Type of audit to run (default: all)"
    )

    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Run all audit types (same as --type all)"
    )

    # Palette selection (for design audits - legacy support)
    parser.add_argument(
        "--palette", "-p",
        default=None,
        help="Palette name for design audits (overrides palette.py from --site)"
    )

    # Crawler options
    parser.add_argument(
        "--max-pages", "-m",
        type=int,
        default=DEFAULT_MAX_PAGES,
        help=f"Maximum pages to crawl (default: {DEFAULT_MAX_PAGES})"
    )

    parser.add_argument(
        "--rate-limit", "-r",
        type=float,
        default=DEFAULT_RATE_LIMIT,
        help=f"Seconds between requests (default: {DEFAULT_RATE_LIMIT})"
    )

    # Output options
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Custom output filename (without extension). Default: auto-generated with timestamp"
    )

    parser.add_argument(
        "--format", "-f",
        choices=["csv", "html", "both"],
        default="both",
        help="Output format (default: both)"
    )

    # Report listing options
    parser.add_argument(
        "--list-reports", "-l",
        action="store_true",
        help="List all reports for the specified site (or all sites if no URL given)"
    )

    parser.add_argument(
        "--list-sites",
        action="store_true",
        help="List all sites that have audit reports"
    )

    # Verbosity
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle --all flag
    if args.all:
        args.type = "all"

    # Expand ~ in site path
    if args.site:
        args.site = os.path.expanduser(args.site)

    # =========================================================================
    # HANDLE LISTING COMMANDS
    # =========================================================================

    if args.list_sites:
        print_reports_summary()
        return 0

    if args.list_reports:
        print_reports_summary(args.url, args.site)
        return 0

    # =========================================================================
    # VALIDATE ARGUMENTS
    # =========================================================================

    if not args.url:
        parser.print_help()
        print("\n❌ Error: URL is required to run an audit.")
        print("   Example: python main.py https://lastingchange.co --site ~/sites/lastingchange.co --all")
        return 1

    if not args.site:
        parser.print_help()
        print("\n❌ Error: --site is required to specify where to find palette.py and save reports.")
        print("   Example: python main.py https://lastingchange.co --site ~/sites/lastingchange.co --all")
        return 1

    if not os.path.exists(args.site):
        print(f"\n❌ Error: Site directory does not exist: {args.site}")
        print("   Create it with: mkdir -p " + args.site)
        return 1

    # Ensure URL has a scheme
    if not args.url.startswith(("http://", "https://")):
        args.url = "https://" + args.url

    # =========================================================================
    # SETUP
    # =========================================================================

    site_name = get_site_name(args.url)
    report_dir = get_site_report_dir(args.url, args.site)

    print("=" * 60)
    print("UNIFIED AUDIT TOOL")
    print("=" * 60)
    print(f"Target URL:  {args.url}")
    print(f"Site Name:   {site_name}")
    print(f"Site Path:   {args.site}")
    print(f"Audit Type:  {args.type}")
    print(f"Max Pages:   {args.max_pages}")
    print(f"Rate Limit:  {args.rate_limit}s")
    print(f"Output Dir:  {report_dir}")
    print("=" * 60)
    print()

    # =========================================================================
    # LOAD SITE PALETTE
    # =========================================================================

    palette_module = None
    if args.type in ["design", "all"]:
        palette_module = load_site_palette(args.site)
        if palette_module:
            print(f"✓ Loaded palette from {args.site}/palette.py")
        elif args.palette:
            print(f"  Using legacy palette: {args.palette}")

    # =========================================================================
    # INITIALIZE AUDITORS
    # =========================================================================

    auditors = {}

    if args.type in ["design", "all"]:
        try:
            # Pass palette module or legacy palette name
            if palette_module:
                auditors["design"] = DesignAuditor(palette_module=palette_module)
            elif args.palette:
                auditors["design"] = DesignAuditor(palette_name=args.palette)
            else:
                auditors["design"] = DesignAuditor()
            print("✓ Design Auditor initialized")
        except Exception as e:
            print(f"⚠️ Design Auditor failed to initialize: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()

    if args.type in ["seo", "all"]:
        try:
            auditors["seo"] = SEOAuditor()
            print("✓ SEO Auditor initialized")
        except Exception as e:
            print(f"⚠️ SEO Auditor failed to initialize: {e}")

    if args.type in ["content", "all"]:
        try:
            auditors["content"] = ContentAuditor()
            print("✓ Content Auditor initialized")
        except Exception as e:
            print(f"⚠️ Content Auditor failed to initialize: {e}")

    if not auditors:
        print("\n❌ No auditors could be initialized. Check your plugins directory.")
        return 1

    print()

    # =========================================================================
    # CREATE COMBINED AUDIT CALLBACK
    # =========================================================================

    def combined_audit_callback(url: str, html: str) -> List[Dict[str, Any]]:
        """
        Run all enabled auditors on a page and combine results.

        Args:
            url: The URL being audited
            html: The HTML content

        Returns:
            Combined list of audit results from all auditors
        """
        all_results = []

        for auditor_name, auditor in auditors.items():
            try:
                results = auditor.audit(url, html)

                # Handle both single dict and list of dicts
                if isinstance(results, dict):
                    results = [results]

                # Tag each result with the auditor type
                for result in results:
                    if "type" not in result:
                        result["type"] = auditor_name

                all_results.extend(results)

                if args.verbose:
                    print(f"    [{auditor_name}] Found {len(results)} items")

            except Exception as e:
                print(f"    [ERROR] {auditor_name} auditor failed: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()

        return all_results

    # =========================================================================
    # RUN CRAWLER
    # =========================================================================

    engine = AuditEngine(
        base_url=args.url,
        max_pages=args.max_pages,
        excluded_patterns=EXCLUDED_PATTERNS,
        rate_limit=args.rate_limit,
        verbose=args.verbose
    )

    print("Starting crawl...")
    print()

    results = engine.run(combined_audit_callback)

    print()

    # =========================================================================
    # GENERATE REPORTS
    # =========================================================================

    if not results:
        print("⚠️ No results to export. Check if the URL is accessible.")
        return 1

    print("Generating reports...")
    print()

    # Determine report type for filename
    report_type = f"audit_{args.type}"

    # Generate all reports (CSV, summary, HTML) in site-specific directory
    generated_files = generate_all_reports(
        results=results,
        url=args.url,
        site_path=args.site
    )

    print()

    # =========================================================================
    # SUMMARY
    # =========================================================================

    print("=" * 60)
    print("AUDIT COMPLETE")
    print("=" * 60)

    # Print statistics
    total = len(results)
    passed = sum(1 for r in results if "✅" in str(r.get("status", "")))
    warnings = sum(1 for r in results if "⚠️" in str(r.get("status", "")))
    failed = sum(1 for r in results if "❌" in str(r.get("status", "")))

    print(f"Total items checked: {total}")
    print(f"  ✅ Passed:   {passed}")
    print(f"  ⚠️  Warnings: {warnings}")
    print(f"  ❌ Failed:   {failed}")
    print()
    print(f"Pass rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")
    print()

    # Print generated file locations
    print("📁 Reports saved to:")
    if isinstance(generated_files, dict):
        output_dir = generated_files.get('output_dir', '')
        all_files = generated_files.get('all_files', [])
        if all_files:
            for filepath in all_files:
                print(f"   {os.path.basename(filepath)}")
            print(f"\n   Directory: {output_dir}")
        else:
            print(f"   {generated_files.get('summary', 'No files generated')}")
    else:
        # Legacy: single path string
        print(f"   {generated_files}")

    print()
    print(f"To list all reports for this site:")
    print(f"   python main.py --site {args.site} --list-reports")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
