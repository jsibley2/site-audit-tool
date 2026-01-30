#!/usr/bin/env python3
"""
CSV Export Module - Site-based Architecture with Design System Linter Support
Generates CSV and HTML reports and saves them to the site's reports directory

Location: ~/scripts/audit_tool/reports/csv_export.py

Required imports by main.py:
- generate_all_reports
- get_site_report_dir
- get_reports_base_dir

Features:
- Variable Candidate column for hard-coded values that should be variables
- Source Context column identifying where styles are defined (hiding spots)
- Dedicated variable remediation report
- Enhanced summary with linter coverage metrics
- HTML report with filterable tables and visual styling
"""

import csv
import os
from datetime import datetime
from urllib.parse import urlparse


# =============================================================================
# DIRECTORY FUNCTIONS (Required by main.py)
# =============================================================================

def get_reports_base_dir(base_url=None, site_path=None):
    """
    Determines the base directory for reports.
    Matches the import expected by main.py.

    Args:
        base_url: The site URL being audited (optional)
        site_path: Optional path to site directory (e.g., ~/sites/lastingchange.co)

    Returns:
        Path to the reports directory
    """
    if site_path:
        return os.path.join(site_path, 'reports')

    if base_url:
        # Fallback to domain-based folder
        domain = urlparse(base_url).netloc.replace('www.', '')
        return os.path.join('reports', domain)

    return 'reports'


def get_site_report_dir(base_url=None, site_path=None):
    """
    Gets the site report directory and ensures it exists.
    Matches the import expected by main.py.

    Args:
        base_url: The site URL being audited (optional)
        site_path: Optional path to site directory

    Returns:
        Path to the reports directory (created if it doesn't exist)
    """
    report_dir = get_reports_base_dir(base_url, site_path)

    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    return report_dir


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def sanitize_filename(url):
    """
    Convert a URL to a safe filename component.

    Args:
        url: The site URL

    Returns:
        Sanitized string suitable for filenames
    """
    if not url:
        return "unknown"
    domain = url.replace('https://', '').replace('http://', '').replace('www.', '')
    domain = domain.split('/')[0]
    return domain.replace('.', '_')


def generate_timestamp():
    """Generate a timestamp string for filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def escape_html(text):
    """Escape HTML special characters."""
    if text is None:
        return ''
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def truncate(text, max_length=50):
    """Truncate text with ellipsis."""
    if not text:
        return ''
    text = str(text)
    if len(text) > max_length:
        return text[:max_length - 3] + '...'
    return text


# =============================================================================
# CSV REPORT GENERATORS
# =============================================================================

def generate_color_report(issues, output_dir):
    """Generate CSV report for color audit findings."""
    filename = f"color_audit_{generate_timestamp()}.csv"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Page URL', 'Element', 'Full Selector', 'Parent Context',
            'Property', 'Expected', 'Found', 'Status', 'Source Context', 'Text Snippet'
        ])
        for issue in issues:
            writer.writerow([
                issue.get('url', ''),
                issue.get('element', ''),
                issue.get('full_selector', ''),
                issue.get('parent_context', ''),
                issue.get('property', ''),
                issue.get('expected', ''),
                issue.get('found', ''),
                issue.get('status', ''),
                issue.get('source_context', ''),
                issue.get('text_snippet', '')
            ])
    return filepath


def generate_seo_report(issues, output_dir):
    """Generate CSV report for SEO audit findings."""
    filename = f"seo_audit_{generate_timestamp()}.csv"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Page URL', 'Element', 'Property', 'Expected', 'Found', 'Status', 'Context'
        ])
        for issue in issues:
            writer.writerow([
                issue.get('url', ''),
                issue.get('element', ''),
                issue.get('property', ''),
                issue.get('expected', ''),
                issue.get('found', ''),
                issue.get('status', ''),
                issue.get('context', '')
            ])
    return filepath


def generate_content_report(issues, output_dir):
    """Generate CSV report for content audit findings."""
    filename = f"content_audit_{generate_timestamp()}.csv"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Page URL', 'Element', 'Property', 'Expected', 'Found', 'Status', 'Context'
        ])
        for issue in issues:
            writer.writerow([
                issue.get('url', ''),
                issue.get('element', ''),
                issue.get('property', ''),
                issue.get('expected', ''),
                issue.get('found', ''),
                issue.get('status', ''),
                issue.get('context', '')
            ])
    return filepath


def generate_design_report(issues, output_dir):
    """Generate CSV report for design audit findings (colors, textures, sections)."""
    filename = f"design_audit_{generate_timestamp()}.csv"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Page URL', 'Type', 'Element', 'Full Selector', 'Parent Context',
            'Property', 'Expected', 'Found', 'Status', 'Source Context', 'Text Snippet'
        ])
        for issue in issues:
            writer.writerow([
                issue.get('url', ''),
                issue.get('type', ''),
                issue.get('element', ''),
                issue.get('full_selector', ''),
                issue.get('parent_context', ''),
                issue.get('property', ''),
                issue.get('expected', ''),
                issue.get('found', ''),
                issue.get('status', ''),
                issue.get('source_context', ''),
                issue.get('text_snippet', '')
            ])
    return filepath


def generate_variable_candidates_report(issues, output_dir):
    """Generate a dedicated CSV report for all variable candidates."""
    candidates = [i for i in issues if i.get('variable_candidate')]
    if not candidates:
        return None

    filename = f"variable_candidates_{generate_timestamp()}.csv"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Type', 'Page URL', 'Element', 'Property', 'Found Value',
            'Variable Candidate', 'Source Context'
        ])
        for issue in candidates:
            writer.writerow([
                issue.get('type', ''),
                issue.get('url', ''),
                issue.get('element', ''),
                issue.get('property', ''),
                issue.get('found', ''),
                issue.get('variable_candidate', ''),
                issue.get('source_context', '')
            ])
    return filepath


def generate_summary_report(issues, url, output_dir):
    """Generate a summary CSV with counts and source context breakdown."""
    filename = f"audit_summary_{generate_timestamp()}.csv"
    filepath = os.path.join(output_dir, filename)

    # Count by type
    type_counts = {}
    source_counts = {}
    status_counts = {'pass': 0, 'warn': 0, 'fail': 0}

    for issue in issues:
        # Count by type
        issue_type = issue.get('type', 'unknown')
        type_counts[issue_type] = type_counts.get(issue_type, 0) + 1

        # Count by source context
        source = issue.get('source_context', 'Unknown')
        status = str(issue.get('status', ''))

        # Only count non-passing items in source breakdown
        if '✅' not in status and 'Match' not in status:
            source_counts[source] = source_counts.get(source, 0) + 1

        # Count by status
        if '✅' in status or 'Match' in status:
            status_counts['pass'] += 1
        elif '⚠️' in status or 'Near' in status or 'Thin' in status:
            status_counts['warn'] += 1
        else:
            status_counts['fail'] += 1

    total = len(issues)
    pass_rate = (status_counts['pass'] / total * 100) if total > 0 else 0

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        writer.writerow(['Audit Summary Report'])
        writer.writerow(['Generated', datetime.now().isoformat()])
        writer.writerow(['Site URL', url or 'Unknown'])
        writer.writerow([])

        writer.writerow(['Overall Statistics'])
        writer.writerow(['Total Checked', total])
        writer.writerow(['Passed', status_counts['pass']])
        writer.writerow(['Warnings', status_counts['warn']])
        writer.writerow(['Failed', status_counts['fail']])
        writer.writerow(['Pass Rate', f"{pass_rate:.1f}%"])
        writer.writerow([])

        writer.writerow(['Issues by Type'])
        writer.writerow(['Type', 'Count'])
        for issue_type, count in sorted(type_counts.items()):
            writer.writerow([issue_type.capitalize(), count])
        writer.writerow([])

        if source_counts:
            writer.writerow(['Issues by Source Context (Hiding Spots)'])
            writer.writerow(['Source', 'Count'])
            for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
                writer.writerow([source, count])

    return filepath


# =============================================================================
# HTML REPORT GENERATOR - Matches sophisticated report format
# =============================================================================

def generate_html_report(issues, url, output_dir):
    """
    Generate an interactive HTML report matching the sophisticated format with:
    - Summary cards (Total, Passed, Warnings, Failed, Pass Rate)
    - Issues by Source section with count chips
    - Legend for source types
    - Filterable table with Type, Status, Source dropdowns + search
    - Color swatches for hex values
    - Full Selector and Parent Context columns
    """
    filename = f"audit_all_{generate_timestamp()}.html"
    filepath = os.path.join(output_dir, filename)

    # Extract domain for title
    domain = 'Unknown Site'
    if url:
        parsed = urlparse(url)
        domain = parsed.netloc or url.replace('https://', '').replace('http://', '').split('/')[0]

    # Calculate statistics
    total = len(issues)
    pass_count = 0
    warn_count = 0
    fail_count = 0

    type_set = set()
    source_counts = {}

    for issue in issues:
        status = str(issue.get('status', ''))
        issue_type = issue.get('type', 'unknown')
        source = issue.get('source_context', 'Unknown')

        type_set.add(issue_type)

        if '✅' in status or 'Match' in status or 'range' in status.lower():
            pass_count += 1
        elif '⚠️' in status or 'Near' in status or 'Thin' in status or 'Review' in status:
            warn_count += 1
        else:
            fail_count += 1
            # Only count failing items in source breakdown
            source_counts[source] = source_counts.get(source, 0) + 1

    pass_rate = (pass_count / total * 100) if total > 0 else 0

    # Build type options for filter
    type_options = ''.join(f'<option value="{t}">{t}</option>' for t in sorted(type_set))

    # Build source chips
    source_chips = ''
    for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        source_chips += f'<div class="source-tag">{escape_html(source)}<span class="count">{count}</span></div>\n'

    # Build table rows
    table_rows = ''
    for issue in issues:
        status = str(issue.get('status', ''))
        issue_type = issue.get('type', 'unknown')
        source = issue.get('source_context', '') or ''
        found = issue.get('found', '') or ''

        # Determine status class and data attribute
        if '✅' in status or 'Match' in status or 'range' in status.lower():
            status_class = 'status-pass'
            status_data = 'pass'
        elif '⚠️' in status or 'Near' in status or 'Thin' in status or 'Review' in status:
            status_class = 'status-warn'
            status_data = 'warn'
        else:
            status_class = 'status-fail'
            status_data = 'fail'

        # Determine source class
        source_lower = source.lower()
        if 'inline' in source_lower:
            source_class = 'source-inline'
            source_data = 'inline'
        elif 'class' in source_lower:
            source_class = 'source-class'
            source_data = 'class'
        elif 'global' in source_lower:
            source_class = 'source-global'
            source_data = 'global'
        elif 'embed' in source_lower or 'custom' in source_lower:
            source_class = 'source-embed'
            source_data = 'embed'
        elif 'external' in source_lower:
            source_class = 'source-external'
            source_data = 'external'
        else:
            source_class = 'source-external'
            source_data = 'other'

        # Color swatch for hex values
        color_swatch = ''
        if found.startswith('#'):
            color_swatch = f'<span class="color-swatch" style="background-color: {escape_html(found)};"></span>'

        # Build row
        row_url = issue.get('url', '')
        full_selector = issue.get('full_selector', '')
        parent_context = issue.get('parent_context', '')
        prop = issue.get('property', '')
        expected = issue.get('expected', '')
        text_snippet = issue.get('text_snippet', '')

        table_rows += f'''<tr data-type="{escape_html(issue_type)}" data-status="{status_data}" data-source="{source_data}">
                    <td title="{escape_html(row_url)}">{escape_html(truncate(row_url, 40))}</td>
                    <td>{escape_html(issue_type)}</td>
                    <td><span class="full-selector" title="{escape_html(full_selector)}">{escape_html(truncate(full_selector, 45))}</span></td>
                    <td><span class="parent-context" title="{escape_html(parent_context)}">{escape_html(truncate(parent_context, 35))}</span></td>
                    <td>{escape_html(prop)}</td>
                    <td>{escape_html(truncate(expected, 30))}</td>
                    <td>{color_swatch}{escape_html(found)}</td>
                    <td class="{status_class}">{escape_html(status)}</td>
                    <td><span class="source-context {source_class}">{escape_html(truncate(source, 50))}</span></td>
                    <td><span class="text-snippet" title="{escape_html(text_snippet)}">{escape_html(truncate(text_snippet, 30))}</span></td>
                </tr>
'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audit Report: {escape_html(domain)}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #1a1a2e;
            background: #f5f5f5;
            padding: 2rem;
        }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        h1 {{ color: #002d68; margin-bottom: 0.5rem; }}
        h2 {{ color: #003153; margin: 1.5rem 0 1rem 0; font-size: 1.25rem; }}
        .subtitle {{ color: #6b7280; margin-bottom: 2rem; }}

        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .card h3 {{
            font-size: 0.875rem;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .card .value {{
            font-size: 2rem;
            font-weight: bold;
            color: #002d68;
        }}
        .card.passed .value {{ color: #059669; }}
        .card.warnings .value {{ color: #d97706; }}
        .card.failed .value {{ color: #dc2626; }}

        .source-breakdown {{
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .source-breakdown h2 {{ margin-top: 0; }}
        .source-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin-top: 1rem;
        }}
        .source-tag {{
            background: #f3f4f6;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
        }}
        .source-tag .count {{
            font-weight: bold;
            color: #dc2626;
            margin-left: 0.5rem;
        }}

        .legend {{
            background: white;
            border-radius: 8px;
            padding: 1rem 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
        }}

        .filter-bar {{
            margin-bottom: 1rem;
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }}
        .filter-bar select, .filter-bar input {{
            padding: 0.5rem 1rem;
            border: 1px solid #e5e5e5;
            border-radius: 4px;
            font-size: 0.875rem;
        }}
        .filter-bar input[type="text"] {{ min-width: 250px; }}
        .filter-bar label {{ font-size: 0.875rem; color: #6b7280; }}

        .table-container {{ overflow-x: auto; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            font-size: 0.875rem;
        }}
        th {{
            background: #002d68;
            color: white;
            padding: 0.75rem 1rem;
            text-align: left;
            font-weight: 600;
            white-space: nowrap;
            cursor: pointer;
            user-select: none;
            position: relative;
        }}
        th:hover {{
            background: #003d88;
        }}
        th .sort-arrow {{
            display: inline-block;
            margin-left: 0.5rem;
            opacity: 0.5;
            font-size: 0.7rem;
        }}
        th.sort-asc .sort-arrow::after {{
            content: '▲';
            opacity: 1;
        }}
        th.sort-desc .sort-arrow::after {{
            content: '▼';
            opacity: 1;
        }}
        th:not(.sort-asc):not(.sort-desc) .sort-arrow::after {{
            content: '▲▼';
            font-size: 0.6rem;
        }}
        td {{
            padding: 0.6rem 1rem;
            border-bottom: 1px solid #e5e5e5;
            max-width: 250px;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        tr:hover td {{ background: #f9fafb; }}

        .status-pass {{ color: #059669; font-weight: 600; }}
        .status-warn {{ color: #d97706; font-weight: 600; }}
        .status-fail {{ color: #dc2626; font-weight: 600; }}

        .full-selector {{
            font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
            font-size: 0.8rem;
            background: #f3f4f6;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            color: #4c1d95;
        }}
        .parent-context {{
            font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
            font-size: 0.75rem;
            color: #6b7280;
        }}
        .source-context {{
            font-size: 0.75rem;
            padding: 0.2rem 0.5rem;
            border-radius: 3px;
            white-space: nowrap;
        }}
        .source-inline {{ background: #fef3c7; color: #92400e; }}
        .source-class {{ background: #dbeafe; color: #1e40af; }}
        .source-global {{ background: #f3e8ff; color: #6b21a8; }}
        .source-embed {{ background: #fee2e2; color: #991b1b; }}
        .source-external {{ background: #e5e7eb; color: #374151; }}

        .color-swatch {{
            display: inline-block;
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 1px solid rgba(0,0,0,0.2);
            vertical-align: middle;
            margin-right: 0.5rem;
        }}
        .text-snippet {{
            font-size: 0.75rem;
            color: #6b7280;
            font-style: italic;
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Audit Report: {escape_html(domain)}</h1>
        <p class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Site: {escape_html(domain)}</p>

        <div class="summary-cards">
            <div class="card">
                <h3>Total Checked</h3>
                <div class="value">{total}</div>
            </div>
            <div class="card passed">
                <h3>Passed ✅</h3>
                <div class="value">{pass_count}</div>
            </div>
            <div class="card warnings">
                <h3>Warnings ⚠️</h3>
                <div class="value">{warn_count}</div>
            </div>
            <div class="card failed">
                <h3>Failed ❌</h3>
                <div class="value">{fail_count}</div>
            </div>
            <div class="card">
                <h3>Pass Rate</h3>
                <div class="value">{pass_rate:.1f}%</div>
            </div>
        </div>

        <div class="source-breakdown">
            <h2>🔍 Issues by Source ("Hiding Spot")</h2>
            <p style="color: #6b7280; font-size: 0.875rem;">Where non-passing styles are coming from:</p>
            <div class="source-list">
                {source_chips}
            </div>
        </div>

        <div class="legend">
            <div class="legend-item"><span class="source-context source-inline">Inline Style</span> Directly on element</div>
            <div class="legend-item"><span class="source-context source-class">Class Style</span> From Webflow class</div>
            <div class="legend-item"><span class="source-context source-global">Global Style</span> Inherited from Body</div>
            <div class="legend-item"><span class="source-context source-embed">Custom Code</span> From Embed block</div>
            <div class="legend-item"><span class="source-context source-external">External CSS</span> From stylesheet</div>
        </div>

        <div class="filter-bar">
            <label>Filter by:</label>
            <select id="typeFilter" onchange="filterTable()">
                <option value="">All Types</option>
                {type_options}
            </select>
            <select id="statusFilter" onchange="filterTable()">
                <option value="">All Statuses</option>
                <option value="pass">✅ Passed</option>
                <option value="warn">⚠️ Warnings</option>
                <option value="fail">❌ Failed</option>
            </select>
            <select id="sourceFilter" onchange="filterTable()">
                <option value="">All Sources</option>
                <option value="inline">Inline Style</option>
                <option value="class">Class Style</option>
                <option value="global">Global Style</option>
                <option value="embed">Custom Code</option>
                <option value="external">External CSS</option>
            </select>
            <input type="text" id="searchInput" placeholder="Search selectors, properties..." onkeyup="filterTable()">
        </div>

        <div class="table-container">
            <table id="resultsTable">
                <thead>
                    <tr>
                        <th onclick="sortTable(0)">URL<span class="sort-arrow"></span></th>
                        <th onclick="sortTable(1)">Type<span class="sort-arrow"></span></th>
                        <th onclick="sortTable(2)">Full Selector<span class="sort-arrow"></span></th>
                        <th onclick="sortTable(3)">Parent Context<span class="sort-arrow"></span></th>
                        <th onclick="sortTable(4)">Property<span class="sort-arrow"></span></th>
                        <th onclick="sortTable(5)">Expected<span class="sort-arrow"></span></th>
                        <th onclick="sortTable(6)">Found<span class="sort-arrow"></span></th>
                        <th onclick="sortTable(7)">Status<span class="sort-arrow"></span></th>
                        <th onclick="sortTable(8)">Source<span class="sort-arrow"></span></th>
                        <th onclick="sortTable(9)">Text Snippet<span class="sort-arrow"></span></th>
                    </tr>
                </thead>
                <tbody>
                {table_rows}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        let currentSortCol = -1;
        let sortAsc = true;

        function filterTable() {{
            const typeFilter = document.getElementById('typeFilter').value.toLowerCase();
            const statusFilter = document.getElementById('statusFilter').value;
            const sourceFilter = document.getElementById('sourceFilter').value;
            const searchInput = document.getElementById('searchInput').value.toLowerCase();
            const rows = document.querySelectorAll('#resultsTable tbody tr');

            rows.forEach(row => {{
                const type = row.dataset.type.toLowerCase();
                const status = row.dataset.status;
                const source = row.dataset.source;
                const text = row.textContent.toLowerCase();

                const typeMatch = !typeFilter || type.includes(typeFilter);
                const statusMatch = !statusFilter || status === statusFilter;
                const sourceMatch = !sourceFilter || source === sourceFilter;
                const searchMatch = !searchInput || text.includes(searchInput);

                row.style.display = typeMatch && statusMatch && sourceMatch && searchMatch ? '' : 'none';
            }});
        }}

        function sortTable(colIndex) {{
            const table = document.getElementById('resultsTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const headers = table.querySelectorAll('th');

            // Toggle sort direction if clicking the same column
            if (currentSortCol === colIndex) {{
                sortAsc = !sortAsc;
            }} else {{
                sortAsc = true;
                currentSortCol = colIndex;
            }}

            // Update header classes for visual feedback
            headers.forEach((th, i) => {{
                th.classList.remove('sort-asc', 'sort-desc');
                if (i === colIndex) {{
                    th.classList.add(sortAsc ? 'sort-asc' : 'sort-desc');
                }}
            }});

            // Sort rows
            rows.sort((a, b) => {{
                const aText = a.cells[colIndex].textContent.trim().toLowerCase();
                const bText = b.cells[colIndex].textContent.trim().toLowerCase();

                // Try numeric comparison first
                const aNum = parseFloat(aText);
                const bNum = parseFloat(bText);
                if (!isNaN(aNum) && !isNaN(bNum)) {{
                    return sortAsc ? aNum - bNum : bNum - aNum;
                }}

                // Fall back to string comparison
                if (aText < bText) return sortAsc ? -1 : 1;
                if (aText > bText) return sortAsc ? 1 : -1;
                return 0;
            }});

            // Re-append sorted rows
            rows.forEach(row => tbody.appendChild(row));
        }}
    </script>
</body>
</html>
'''

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    return filepath


# =============================================================================
# ROGUE COLORS SUMMARY HTML REPORT
# =============================================================================

def generate_rogue_colors_summary_html(issues, url, output_dir):
    """
    Generate an HTML summary report for rogue (non-matching) colors showing:
    - Overall counts by color value
    - Counts by page
    - Counts by source context
    """
    filename = f"rogue_colors_summary_{generate_timestamp()}.html"
    filepath = os.path.join(output_dir, filename)

    # Extract domain for title
    domain = 'Unknown Site'
    if url:
        parsed = urlparse(url)
        domain = parsed.netloc or url.replace('https://', '').replace('http://', '').split('/')[0]

    # Filter for rogue colors (color type + not passing)
    rogue_colors = []
    for issue in issues:
        if issue.get('type') != 'color':
            continue
        status = str(issue.get('status', ''))
        if '✅' in status or 'Match' in status or 'range' in status.lower():
            continue  # Skip passing colors
        rogue_colors.append(issue)

    if not rogue_colors:
        return None

    # Aggregate by color value
    color_counts = {}
    for issue in rogue_colors:
        color = issue.get('found', 'Unknown')
        if color not in color_counts:
            color_counts[color] = {'count': 0, 'pages': set(), 'sources': set(), 'properties': set()}
        color_counts[color]['count'] += 1
        color_counts[color]['pages'].add(issue.get('url', 'Unknown'))
        color_counts[color]['sources'].add(issue.get('source_context', 'Unknown'))
        color_counts[color]['properties'].add(issue.get('property', 'Unknown'))

    # Aggregate by page
    page_counts = {}
    for issue in rogue_colors:
        page = issue.get('url', 'Unknown')
        if page not in page_counts:
            page_counts[page] = {'count': 0, 'colors': set(), 'sources': set()}
        page_counts[page]['count'] += 1
        page_counts[page]['colors'].add(issue.get('found', 'Unknown'))
        page_counts[page]['sources'].add(issue.get('source_context', 'Unknown'))

    # Aggregate by source
    source_counts = {}
    for issue in rogue_colors:
        source = issue.get('source_context', 'Unknown')
        if source not in source_counts:
            source_counts[source] = {'count': 0, 'colors': set(), 'pages': set()}
        source_counts[source]['count'] += 1
        source_counts[source]['colors'].add(issue.get('found', 'Unknown'))
        source_counts[source]['pages'].add(issue.get('url', 'Unknown'))

    # Build color rows (sorted by count descending)
    color_rows = ''
    for color, data in sorted(color_counts.items(), key=lambda x: -x[1]['count']):
        swatch = ''
        if color.startswith('#'):
            swatch = f'<span class="color-swatch" style="background-color: {escape_html(color)};"></span>'
        pages_list = ', '.join(sorted(data['pages']))
        sources_list = ', '.join(sorted(data['sources']))
        props_list = ', '.join(sorted(data['properties']))
        color_rows += f'''<tr>
            <td>{swatch}<code>{escape_html(color)}</code></td>
            <td class="count-cell">{data['count']}</td>
            <td>{len(data['pages'])}</td>
            <td title="{escape_html(props_list)}">{escape_html(truncate(props_list, 40))}</td>
            <td title="{escape_html(sources_list)}">{escape_html(truncate(sources_list, 40))}</td>
        </tr>
'''

    # Build page rows (sorted by count descending)
    page_rows = ''
    for page, data in sorted(page_counts.items(), key=lambda x: -x[1]['count']):
        colors_preview = ', '.join(list(data['colors'])[:5])
        if len(data['colors']) > 5:
            colors_preview += f' (+{len(data["colors"]) - 5} more)'
        sources_list = ', '.join(sorted(data['sources']))
        page_rows += f'''<tr>
            <td title="{escape_html(page)}">{escape_html(truncate(page, 50))}</td>
            <td class="count-cell">{data['count']}</td>
            <td>{len(data['colors'])}</td>
            <td title="{escape_html(sources_list)}">{escape_html(truncate(sources_list, 40))}</td>
        </tr>
'''

    # Build source rows (sorted by count descending)
    source_rows = ''
    for source, data in sorted(source_counts.items(), key=lambda x: -x[1]['count']):
        source_lower = source.lower()
        if 'inline' in source_lower:
            source_class = 'source-inline'
        elif 'class' in source_lower:
            source_class = 'source-class'
        elif 'global' in source_lower:
            source_class = 'source-global'
        elif 'embed' in source_lower or 'custom' in source_lower:
            source_class = 'source-embed'
        else:
            source_class = 'source-external'
        colors_preview = ', '.join(list(data['colors'])[:5])
        if len(data['colors']) > 5:
            colors_preview += f' (+{len(data["colors"]) - 5} more)'
        source_rows += f'''<tr>
            <td><span class="source-badge {source_class}">{escape_html(source)}</span></td>
            <td class="count-cell">{data['count']}</td>
            <td>{len(data['colors'])}</td>
            <td>{len(data['pages'])}</td>
        </tr>
'''

    total_rogue = len(rogue_colors)
    unique_colors = len(color_counts)
    pages_affected = len(page_counts)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rogue Colors Summary: {escape_html(domain)}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #1a1a2e;
            background: #f5f5f5;
            padding: 2rem;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ color: #dc2626; margin-bottom: 0.5rem; }}
        h2 {{ color: #003153; margin: 2rem 0 1rem 0; font-size: 1.25rem; border-bottom: 2px solid #e5e5e5; padding-bottom: 0.5rem; }}
        .subtitle {{ color: #6b7280; margin-bottom: 2rem; }}

        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 4px solid #dc2626;
        }}
        .card h3 {{
            font-size: 0.875rem;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .card .value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #dc2626;
        }}
        .card.neutral .value {{ color: #002d68; }}
        .card.neutral {{ border-left-color: #002d68; }}

        .section {{
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .section h2 {{ margin-top: 0; border: none; padding: 0; margin-bottom: 1rem; }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }}
        th {{
            background: #002d68;
            color: white;
            padding: 0.75rem 1rem;
            text-align: left;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
        }}
        th:hover {{ background: #003d88; }}
        th .sort-arrow {{
            display: inline-block;
            margin-left: 0.5rem;
            opacity: 0.5;
            font-size: 0.7rem;
        }}
        th.sort-asc .sort-arrow::after {{ content: '▲'; opacity: 1; }}
        th.sort-desc .sort-arrow::after {{ content: '▼'; opacity: 1; }}
        th:not(.sort-asc):not(.sort-desc) .sort-arrow::after {{ content: '▲▼'; font-size: 0.6rem; }}
        td {{
            padding: 0.6rem 1rem;
            border-bottom: 1px solid #e5e5e5;
        }}
        tr:hover td {{ background: #f9fafb; }}
        .count-cell {{
            font-weight: bold;
            color: #dc2626;
            font-size: 1.1rem;
        }}

        .color-swatch {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 4px;
            border: 1px solid rgba(0,0,0,0.2);
            vertical-align: middle;
            margin-right: 0.5rem;
        }}
        code {{
            background: #f3f4f6;
            padding: 0.2rem 0.5rem;
            border-radius: 3px;
            font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
            font-size: 0.85rem;
        }}

        .source-badge {{
            font-size: 0.8rem;
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            white-space: nowrap;
        }}
        .source-inline {{ background: #fef3c7; color: #92400e; }}
        .source-class {{ background: #dbeafe; color: #1e40af; }}
        .source-global {{ background: #f3e8ff; color: #6b21a8; }}
        .source-embed {{ background: #fee2e2; color: #991b1b; }}
        .source-external {{ background: #e5e7eb; color: #374151; }}

        .tabs {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}
        .tab {{
            padding: 0.5rem 1rem;
            background: #e5e7eb;
            border: none;
            border-radius: 4px 4px 0 0;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
        }}
        .tab.active {{
            background: #002d68;
            color: white;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Rogue Colors Summary</h1>
        <p class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Site: {escape_html(domain)}</p>

        <div class="summary-cards">
            <div class="card">
                <h3>Total Rogue Colors</h3>
                <div class="value">{total_rogue}</div>
            </div>
            <div class="card neutral">
                <h3>Unique Colors</h3>
                <div class="value">{unique_colors}</div>
            </div>
            <div class="card neutral">
                <h3>Pages Affected</h3>
                <div class="value">{pages_affected}</div>
            </div>
            <div class="card neutral">
                <h3>Source Types</h3>
                <div class="value">{len(source_counts)}</div>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('colors')">By Color</button>
            <button class="tab" onclick="showTab('pages')">By Page</button>
            <button class="tab" onclick="showTab('sources')">By Source</button>
        </div>

        <div id="colors" class="tab-content active">
            <div class="section">
                <h2>🔴 Rogue Colors by Value</h2>
                <p style="color: #6b7280; margin-bottom: 1rem;">Colors found that don't match the design system palette:</p>
                <table id="colorsTable">
                    <thead>
                        <tr>
                            <th onclick="sortTable('colorsTable', 0)">Color<span class="sort-arrow"></span></th>
                            <th onclick="sortTable('colorsTable', 1)">Occurrences<span class="sort-arrow"></span></th>
                            <th onclick="sortTable('colorsTable', 2)">Pages<span class="sort-arrow"></span></th>
                            <th onclick="sortTable('colorsTable', 3)">Properties<span class="sort-arrow"></span></th>
                            <th onclick="sortTable('colorsTable', 4)">Sources<span class="sort-arrow"></span></th>
                        </tr>
                    </thead>
                    <tbody>
                        {color_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <div id="pages" class="tab-content">
            <div class="section">
                <h2>📄 Rogue Colors by Page</h2>
                <p style="color: #6b7280; margin-bottom: 1rem;">Pages with the most rogue color issues:</p>
                <table id="pagesTable">
                    <thead>
                        <tr>
                            <th onclick="sortTable('pagesTable', 0)">Page URL<span class="sort-arrow"></span></th>
                            <th onclick="sortTable('pagesTable', 1)">Issues<span class="sort-arrow"></span></th>
                            <th onclick="sortTable('pagesTable', 2)">Unique Colors<span class="sort-arrow"></span></th>
                            <th onclick="sortTable('pagesTable', 3)">Sources<span class="sort-arrow"></span></th>
                        </tr>
                    </thead>
                    <tbody>
                        {page_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <div id="sources" class="tab-content">
            <div class="section">
                <h2>📍 Rogue Colors by Source</h2>
                <p style="color: #6b7280; margin-bottom: 1rem;">Where the rogue colors are coming from (hiding spots):</p>
                <table id="sourcesTable">
                    <thead>
                        <tr>
                            <th onclick="sortTable('sourcesTable', 0)">Source<span class="sort-arrow"></span></th>
                            <th onclick="sortTable('sourcesTable', 1)">Issues<span class="sort-arrow"></span></th>
                            <th onclick="sortTable('sourcesTable', 2)">Unique Colors<span class="sort-arrow"></span></th>
                            <th onclick="sortTable('sourcesTable', 3)">Pages Affected<span class="sort-arrow"></span></th>
                        </tr>
                    </thead>
                    <tbody>
                        {source_rows}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const sortState = {{}};

        function showTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            document.querySelector(`[onclick="showTab('${{tabId}}')"]`).classList.add('active');
        }}

        function sortTable(tableId, colIndex) {{
            const table = document.getElementById(tableId);
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const headers = table.querySelectorAll('th');

            const stateKey = tableId + '_' + colIndex;
            sortState[stateKey] = !sortState[stateKey];
            const sortAsc = sortState[stateKey];

            // Update header classes
            headers.forEach((th, i) => {{
                th.classList.remove('sort-asc', 'sort-desc');
                if (i === colIndex) {{
                    th.classList.add(sortAsc ? 'sort-asc' : 'sort-desc');
                }}
            }});

            rows.sort((a, b) => {{
                const aText = a.cells[colIndex].textContent.trim().toLowerCase();
                const bText = b.cells[colIndex].textContent.trim().toLowerCase();
                const aNum = parseFloat(aText);
                const bNum = parseFloat(bText);
                if (!isNaN(aNum) && !isNaN(bNum)) {{
                    return sortAsc ? aNum - bNum : bNum - aNum;
                }}
                if (aText < bText) return sortAsc ? -1 : 1;
                if (aText > bText) return sortAsc ? 1 : -1;
                return 0;
            }});

            rows.forEach(row => tbody.appendChild(row));
        }}
    </script>
</body>
</html>
'''

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    return filepath


# =============================================================================
# MAIN ENTRY POINT (Required by main.py)
# =============================================================================

def generate_all_reports(results, url=None, site_path=None):
    """
    Generate all reports (CSV, HTML, summary) for the audit results.
    This is the main entry point called by main.py.

    Args:
        results: List of audit result dicts from main.py
                 (NOT a dict with 'issues' key - it's the raw list)
        url: The audited site URL
        site_path: Path to site directory (e.g., ~/sites/lastingchange.co)

    Returns:
        Dict mapping report type to file path
    """
    output_dir = get_site_report_dir(url, site_path)

    print(f"Generating reports in: {output_dir}")

    # Handle both list and dict formats
    if isinstance(results, dict):
        issues = results.get('issues', [])
    else:
        issues = results

    generated_files = {}

    # Categorize issues by type
    color_issues = [i for i in issues if i.get('type') == 'color']
    texture_issues = [i for i in issues if i.get('type') == 'texture']
    section_issues = [i for i in issues if i.get('type') == 'section']
    seo_issues = [i for i in issues if i.get('type') == 'seo']
    content_issues = [i for i in issues if i.get('type') == 'content']

    # Design issues = color + texture + section
    design_issues = color_issues + texture_issues + section_issues

    # Generate type-specific CSV reports
    if design_issues:
        path = generate_design_report(design_issues, output_dir)
        generated_files['design'] = path
        print(f"  ✓ Design report: {os.path.basename(path)} ({len(design_issues)} issues)")

    # Generate rogue colors summary HTML
    if color_issues:
        rogue_path = generate_rogue_colors_summary_html(color_issues, url, output_dir)
        if rogue_path:
            generated_files['rogue_colors'] = rogue_path
            rogue_count = sum(1 for i in color_issues if '✅' not in str(i.get('status', '')) and 'Match' not in str(i.get('status', '')))
            print(f"  ✓ Rogue colors summary: {os.path.basename(rogue_path)} ({rogue_count} rogue colors)")

    if seo_issues:
        path = generate_seo_report(seo_issues, output_dir)
        generated_files['seo'] = path
        print(f"  ✓ SEO report: {os.path.basename(path)} ({len(seo_issues)} issues)")

    if content_issues:
        path = generate_content_report(content_issues, output_dir)
        generated_files['content'] = path
        print(f"  ✓ Content report: {os.path.basename(path)} ({len(content_issues)} issues)")

    # Generate variable candidates report
    variable_candidates_path = generate_variable_candidates_report(issues, output_dir)
    if variable_candidates_path:
        generated_files['variable_candidates'] = variable_candidates_path
        candidate_count = sum(1 for i in issues if i.get('variable_candidate'))
        print(f"  ✓ Variable candidates: {os.path.basename(variable_candidates_path)} ({candidate_count} candidates)")

    # Generate summary CSV
    summary_path = generate_summary_report(issues, url, output_dir)
    generated_files['summary'] = summary_path
    print(f"  ✓ Summary report: {os.path.basename(summary_path)}")

    # Generate HTML report
    html_path = generate_html_report(issues, url, output_dir)
    generated_files['html'] = html_path
    print(f"  ✓ HTML report: {os.path.basename(html_path)}")

    return generated_files
