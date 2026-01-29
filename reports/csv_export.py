#!/usr/bin/env python3
"""
CSV Export Module - Site-based Architecture with Design System Linter Support
Generates CSV reports and saves them to the site's reports directory

Location: ~/scripts/audit_tool/reports/csv_export.py

Required imports by main.py:
- generate_all_reports
- get_site_report_dir
- get_reports_base_dir
"""

import csv
import os
from datetime import datetime
from urllib.parse import urlparse


# =============================================================================
# DIRECTORY FUNCTIONS (Required by main.py)
# =============================================================================

def get_reports_base_dir(base_url, site_path=None):
    """
    Determines the base directory for reports.
    Matches the import expected by main.py.
    
    Args:
        base_url: The site URL being audited
        site_path: Optional path to site directory (e.g., ~/sites/lastingchange.co)
    
    Returns:
        Path to the reports directory
    """
    if site_path:
        return os.path.join(site_path, 'reports')
    
    # Fallback to domain-based folder
    domain = urlparse(base_url).netloc.replace('www.', '')
    return os.path.join('reports', domain)


def get_site_report_dir(base_url, site_path=None):
    """
    Gets the site report directory and ensures it exists.
    Matches the import expected by main.py.
    
    Args:
        base_url: The site URL being audited
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
    domain = url.replace('https://', '').replace('http://', '').replace('www.', '')
    domain = domain.split('/')[0]
    return domain.replace('.', '_')


def generate_timestamp():
    """Generate a timestamp string for filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# =============================================================================
# REPORT GENERATORS
# =============================================================================

def generate_color_report(results, output_dir):
    """
    Generate CSV report for color audit findings.
    Includes Variable Candidate and Source Context columns.
    
    Args:
        results: Dict containing color audit results
        output_dir: Directory to save the report
    
    Returns:
        Path to the generated CSV file
    """
    filename = f"color_audit_{generate_timestamp()}.csv"
    filepath = os.path.join(output_dir, filename)
    
    color_issues = [i for i in results.get('issues', []) if i.get('type') == 'color']
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header with new columns
        writer.writerow([
            'Page URL',
            'Element',
            'CSS Selector',
            'Property',
            'Found Value',
            'Variable Candidate',
            'Match Type',
            'Source Context',
            'Severity',
            'Notes'
        ])
        
        # Data rows
        for issue in color_issues:
            writer.writerow([
                issue.get('page_url', ''),
                issue.get('element', ''),
                issue.get('selector', ''),
                issue.get('property', ''),
                issue.get('found_value', ''),
                issue.get('variable_candidate', ''),
                issue.get('match_type', ''),
                issue.get('source_context', ''),
                issue.get('severity', 'medium'),
                issue.get('notes', '')
            ])
    
    return filepath


def generate_font_report(results, output_dir):
    """
    Generate CSV report for font/typography audit findings.
    Includes Variable Candidate and Source Context columns.
    
    Args:
        results: Dict containing font audit results
        output_dir: Directory to save the report
    
    Returns:
        Path to the generated CSV file
    """
    filename = f"font_audit_{generate_timestamp()}.csv"
    filepath = os.path.join(output_dir, filename)
    
    font_issues = [i for i in results.get('issues', []) if i.get('type') == 'font']
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header with new columns
        writer.writerow([
            'Page URL',
            'Element',
            'CSS Selector',
            'Property',
            'Found Value',
            'Variable Candidate',
            'Font Size',
            'Font Weight',
            'Line Height',
            'Source Context',
            'Severity',
            'Notes'
        ])
        
        # Data rows
        for issue in font_issues:
            writer.writerow([
                issue.get('page_url', ''),
                issue.get('element', ''),
                issue.get('selector', ''),
                issue.get('property', ''),
                issue.get('found_value', ''),
                issue.get('variable_candidate', ''),
                issue.get('font_size', ''),
                issue.get('font_weight', ''),
                issue.get('line_height', ''),
                issue.get('source_context', ''),
                issue.get('severity', 'medium'),
                issue.get('notes', '')
            ])
    
    return filepath


def generate_spacing_report(results, output_dir):
    """
    Generate CSV report for spacing audit findings.
    Includes Variable Candidate and Source Context columns.
    
    Args:
        results: Dict containing spacing audit results
        output_dir: Directory to save the report
    
    Returns:
        Path to the generated CSV file
    """
    filename = f"spacing_audit_{generate_timestamp()}.csv"
    filepath = os.path.join(output_dir, filename)
    
    spacing_issues = [i for i in results.get('issues', []) if i.get('type') == 'spacing']
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header with new columns
        writer.writerow([
            'Page URL',
            'Element',
            'CSS Selector',
            'Property',
            'Found Value',
            'Variable Candidate',
            'Match Type',
            'Source Context',
            'Severity',
            'Notes'
        ])
        
        # Data rows
        for issue in spacing_issues:
            writer.writerow([
                issue.get('page_url', ''),
                issue.get('element', ''),
                issue.get('selector', ''),
                issue.get('property', ''),
                issue.get('found_value', ''),
                issue.get('variable_candidate', ''),
                issue.get('match_type', ''),
                issue.get('source_context', ''),
                issue.get('severity', 'medium'),
                issue.get('notes', '')
            ])
    
    return filepath


def generate_image_report(results, output_dir):
    """
    Generate CSV report for image audit findings.
    
    Args:
        results: Dict containing image audit results
        output_dir: Directory to save the report
    
    Returns:
        Path to the generated CSV file
    """
    filename = f"image_audit_{generate_timestamp()}.csv"
    filepath = os.path.join(output_dir, filename)
    
    image_issues = [i for i in results.get('issues', []) if i.get('type') == 'image']
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'Page URL',
            'Image URL',
            'Alt Text',
            'Issue Type',
            'Current Size (KB)',
            'Recommended Size (KB)',
            'Dimensions',
            'Format',
            'Severity',
            'Notes'
        ])
        
        # Data rows
        for issue in image_issues:
            writer.writerow([
                issue.get('page_url', ''),
                issue.get('image_url', ''),
                issue.get('alt_text', ''),
                issue.get('issue_subtype', ''),
                issue.get('current_size', ''),
                issue.get('recommended_size', ''),
                issue.get('dimensions', ''),
                issue.get('format', ''),
                issue.get('severity', 'medium'),
                issue.get('notes', '')
            ])
    
    return filepath


def generate_seo_report(results, output_dir):
    """
    Generate CSV report for SEO audit findings.

    Args:
        results: Dict containing SEO audit results
        output_dir: Directory to save the report

    Returns:
        Path to the generated CSV file
    """
    filename = f"seo_audit_{generate_timestamp()}.csv"
    filepath = os.path.join(output_dir, filename)

    seo_issues = [i for i in results.get('issues', []) if i.get('type') == 'seo']

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'Page URL',
            'Element',
            'Property',
            'Expected',
            'Found',
            'Status'
        ])

        # Data rows
        for issue in seo_issues:
            writer.writerow([
                issue.get('url', ''),
                issue.get('element', ''),
                issue.get('property', ''),
                issue.get('expected', ''),
                issue.get('found', ''),
                issue.get('status', '')
            ])

    return filepath


def generate_content_report(results, output_dir):
    """
    Generate CSV report for content audit findings.

    Args:
        results: Dict containing content audit results
        output_dir: Directory to save the report

    Returns:
        Path to the generated CSV file
    """
    filename = f"content_audit_{generate_timestamp()}.csv"
    filepath = os.path.join(output_dir, filename)

    content_issues = [i for i in results.get('issues', []) if i.get('type') == 'content']

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'Page URL',
            'Element',
            'Property',
            'Expected',
            'Found',
            'Status',
            'Context'
        ])

        # Data rows
        for issue in content_issues:
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


def generate_design_report(results, output_dir):
    """
    Generate CSV report for all design audit findings (colors, textures, sections).

    Args:
        results: Dict containing design audit results
        output_dir: Directory to save the report

    Returns:
        Path to the generated CSV file
    """
    filename = f"design_audit_{generate_timestamp()}.csv"
    filepath = os.path.join(output_dir, filename)

    # Include color, texture, and section types
    design_issues = [i for i in results.get('issues', [])
                     if i.get('type') in ('color', 'texture', 'section')]

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'Page URL',
            'Type',
            'Element',
            'Full Selector',
            'Property',
            'Expected',
            'Found',
            'Status',
            'Source Context'
        ])

        # Data rows
        for issue in design_issues:
            writer.writerow([
                issue.get('url', ''),
                issue.get('type', ''),
                issue.get('element', ''),
                issue.get('full_selector', ''),
                issue.get('property', ''),
                issue.get('expected', ''),
                issue.get('found', ''),
                issue.get('status', ''),
                issue.get('source_context', '')
            ])

    return filepath


def generate_variable_candidates_report(results, output_dir):
    """
    Generate a dedicated CSV report for all variable candidates.
    This is a consolidated view of all hard-coded values that should be variables.
    
    Args:
        results: Dict containing all audit results
        output_dir: Directory to save the report
    
    Returns:
        Path to the generated CSV file
    """
    filename = f"variable_candidates_{generate_timestamp()}.csv"
    filepath = os.path.join(output_dir, filename)
    
    # Filter issues that have variable candidates
    candidates = [i for i in results.get('issues', []) if i.get('variable_candidate')]
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'Issue Type',
            'Page URL',
            'Element',
            'CSS Selector',
            'Property',
            'Found Value',
            'Variable Candidate',
            'Match Type',
            'Source Context',
            'Severity',
            'Remediation'
        ])
        
        # Data rows
        for issue in candidates:
            # Generate remediation suggestion
            var_name = issue.get('variable_candidate', '')
            found_val = issue.get('found_value', '')
            remediation = f"Replace '{found_val}' with 'var(--{var_name.lower().replace('/', '-')})'"
            
            writer.writerow([
                issue.get('type', ''),
                issue.get('page_url', ''),
                issue.get('element', ''),
                issue.get('selector', ''),
                issue.get('property', ''),
                found_val,
                var_name,
                issue.get('match_type', ''),
                issue.get('source_context', ''),
                issue.get('severity', 'medium'),
                remediation
            ])
    
    return filepath


def generate_summary_report(results, url, output_dir):
    """
    Generate a summary CSV with counts and overview.
    Includes breakdown by source context (hiding spots).
    
    Args:
        results: Dict containing all audit results
        url: The audited site URL
        output_dir: Directory to save the report
    
    Returns:
        Path to the generated CSV file
    """
    filename = f"audit_summary_{generate_timestamp()}.csv"
    filepath = os.path.join(output_dir, filename)
    
    issues = results.get('issues', [])
    summary = results.get('summary', {})

    # Count by type - match actual types from plugins
    color_count = len([i for i in issues if i.get('type') == 'color'])
    texture_count = len([i for i in issues if i.get('type') == 'texture'])
    section_count = len([i for i in issues if i.get('type') == 'section'])
    seo_count = len([i for i in issues if i.get('type') == 'seo'])
    content_count = len([i for i in issues if i.get('type') == 'content'])
    
    # Count by severity
    high_count = len([i for i in issues if i.get('severity') == 'high'])
    medium_count = len([i for i in issues if i.get('severity') == 'medium'])
    low_count = len([i for i in issues if i.get('severity') == 'low'])
    
    # Count by source context (hiding spots)
    source_counts = summary.get('by_source_context', {})
    if not source_counts:
        # Build from issues if not in summary
        for issue in issues:
            source = issue.get('source_context', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
    
    # Count variable candidates
    variable_candidate_count = len([i for i in issues if i.get('variable_candidate')])
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        writer.writerow(['Audit Summary Report'])
        writer.writerow(['Generated', datetime.now().isoformat()])
        writer.writerow(['Site URL', url])
        writer.writerow([])
        
        writer.writerow(['Issues by Type'])
        writer.writerow(['Type', 'Count'])
        writer.writerow(['Colors', color_count])
        writer.writerow(['Textures', texture_count])
        writer.writerow(['Sections', section_count])
        writer.writerow(['SEO', seo_count])
        writer.writerow(['Content', content_count])
        writer.writerow(['TOTAL', len(issues)])
        writer.writerow([])
        
        writer.writerow(['Issues by Severity'])
        writer.writerow(['Severity', 'Count'])
        writer.writerow(['High', high_count])
        writer.writerow(['Medium', medium_count])
        writer.writerow(['Low', low_count])
        writer.writerow([])
        
        writer.writerow(['Issues by Source Context (Hiding Spots)'])
        writer.writerow(['Source', 'Count'])
        for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
            writer.writerow([source, count])
        writer.writerow([])
        
        writer.writerow(['Design System Linter'])
        writer.writerow(['Variable Candidates Found', variable_candidate_count])
        writer.writerow(['Percentage of Issues', f"{(variable_candidate_count / len(issues) * 100):.1f}%" if issues else "0%"])
    
    return filepath


# =============================================================================
# HTML REPORT GENERATORS
# =============================================================================

def generate_html_report(results, url, output_dir):
    """
    Generate an HTML summary report with all audit findings.

    Args:
        results: Dict containing all audit results
        url: The audited site URL
        output_dir: Directory to save the report

    Returns:
        Path to the generated HTML file
    """
    filename = f"audit_report_{generate_timestamp()}.html"
    filepath = os.path.join(output_dir, filename)

    issues = results.get('issues', [])

    # Count by type
    color_count = len([i for i in issues if i.get('type') == 'color'])
    texture_count = len([i for i in issues if i.get('type') == 'texture'])
    section_count = len([i for i in issues if i.get('type') == 'section'])
    seo_count = len([i for i in issues if i.get('type') == 'seo'])
    content_count = len([i for i in issues if i.get('type') == 'content'])

    # Count by status
    pass_count = len([i for i in issues if 'Match' in str(i.get('status', '')) or 'range' in str(i.get('status', '')).lower()])
    warn_count = len([i for i in issues if 'Near' in str(i.get('status', '')) or 'Review' in str(i.get('status', ''))])
    fail_count = len([i for i in issues if 'Mismatch' in str(i.get('status', '')) or 'Missing' in str(i.get('status', '')) or 'Rogue' in str(i.get('status', ''))])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audit Report - {url}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        h1 {{ font-size: 1.5rem; margin-bottom: 5px; }}
        .meta {{ opacity: 0.8; font-size: 0.9rem; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-value {{ font-size: 2rem; font-weight: bold; }}
        .stat-label {{ font-size: 0.85rem; color: #666; }}
        .pass {{ color: #27ae60; }}
        .warn {{ color: #f39c12; }}
        .fail {{ color: #e74c3c; }}
        section {{ background: white; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; }}
        section h2 {{ background: #34495e; color: white; padding: 12px 20px; font-size: 1.1rem; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
        th, td {{ padding: 10px 15px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #ecf0f1; font-weight: 600; }}
        tr:hover {{ background: #f8f9fa; }}
        .status-pass {{ color: #27ae60; }}
        .status-warn {{ color: #f39c12; }}
        .status-fail {{ color: #e74c3c; }}
        .truncate {{ max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.85rem; }}
    </style>
</head>
<body>
    <header>
        <h1>Site Audit Report</h1>
        <p class="meta">{url} | Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </header>

    <div class="summary">
        <div class="stat-card">
            <div class="stat-value">{len(issues)}</div>
            <div class="stat-label">Total Issues</div>
        </div>
        <div class="stat-card">
            <div class="stat-value pass">{pass_count}</div>
            <div class="stat-label">Passed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value warn">{warn_count}</div>
            <div class="stat-label">Warnings</div>
        </div>
        <div class="stat-card">
            <div class="stat-value fail">{fail_count}</div>
            <div class="stat-label">Failed</div>
        </div>
    </div>

    <div class="summary">
        <div class="stat-card"><div class="stat-value">{color_count}</div><div class="stat-label">Colors</div></div>
        <div class="stat-card"><div class="stat-value">{texture_count}</div><div class="stat-label">Textures</div></div>
        <div class="stat-card"><div class="stat-value">{section_count}</div><div class="stat-label">Sections</div></div>
        <div class="stat-card"><div class="stat-value">{seo_count}</div><div class="stat-label">SEO</div></div>
        <div class="stat-card"><div class="stat-value">{content_count}</div><div class="stat-label">Content</div></div>
    </div>
"""

    def get_status_class(status):
        status_str = str(status)
        if 'Match' in status_str or 'range' in status_str.lower():
            return 'status-pass'
        elif 'Near' in status_str or 'Review' in status_str or 'Thin' in status_str:
            return 'status-warn'
        return 'status-fail'

    def escape_html(text):
        if text is None:
            return ''
        return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    # Design issues section
    design_issues = [i for i in issues if i.get('type') in ('color', 'texture', 'section')]
    if design_issues:
        html_content += """
    <section>
        <h2>Design Audit ({} issues)</h2>
        <table>
            <tr><th>Type</th><th>Element</th><th>Property</th><th>Expected</th><th>Found</th><th>Status</th></tr>
""".format(len(design_issues))
        for issue in design_issues[:100]:  # Limit to 100 for performance
            html_content += f"""            <tr>
                <td>{escape_html(issue.get('type', ''))}</td>
                <td class="truncate">{escape_html(issue.get('element', ''))}</td>
                <td>{escape_html(issue.get('property', ''))}</td>
                <td class="truncate">{escape_html(issue.get('expected', ''))}</td>
                <td>{escape_html(issue.get('found', ''))}</td>
                <td class="{get_status_class(issue.get('status'))}">{escape_html(issue.get('status', ''))}</td>
            </tr>
"""
        if len(design_issues) > 100:
            html_content += f'            <tr><td colspan="6">... and {len(design_issues) - 100} more issues (see CSV for full list)</td></tr>\n'
        html_content += "        </table>\n    </section>\n"

    # SEO issues section
    seo_issues = [i for i in issues if i.get('type') == 'seo']
    if seo_issues:
        html_content += """
    <section>
        <h2>SEO Audit ({} issues)</h2>
        <table>
            <tr><th>Element</th><th>Property</th><th>Expected</th><th>Found</th><th>Status</th></tr>
""".format(len(seo_issues))
        for issue in seo_issues[:100]:
            html_content += f"""            <tr>
                <td>{escape_html(issue.get('element', ''))}</td>
                <td>{escape_html(issue.get('property', ''))}</td>
                <td class="truncate">{escape_html(issue.get('expected', ''))}</td>
                <td class="truncate">{escape_html(issue.get('found', ''))}</td>
                <td class="{get_status_class(issue.get('status'))}">{escape_html(issue.get('status', ''))}</td>
            </tr>
"""
        if len(seo_issues) > 100:
            html_content += f'            <tr><td colspan="5">... and {len(seo_issues) - 100} more issues</td></tr>\n'
        html_content += "        </table>\n    </section>\n"

    # Content issues section
    content_issues = [i for i in issues if i.get('type') == 'content']
    if content_issues:
        html_content += """
    <section>
        <h2>Content Audit ({} issues)</h2>
        <table>
            <tr><th>Element</th><th>Property</th><th>Expected</th><th>Found</th><th>Status</th></tr>
""".format(len(content_issues))
        for issue in content_issues[:100]:
            html_content += f"""            <tr>
                <td>{escape_html(issue.get('element', ''))}</td>
                <td>{escape_html(issue.get('property', ''))}</td>
                <td class="truncate">{escape_html(issue.get('expected', ''))}</td>
                <td class="truncate">{escape_html(issue.get('found', ''))}</td>
                <td class="{get_status_class(issue.get('status'))}">{escape_html(issue.get('status', ''))}</td>
            </tr>
"""
        if len(content_issues) > 100:
            html_content += f'            <tr><td colspan="5">... and {len(content_issues) - 100} more issues</td></tr>\n'
        html_content += "        </table>\n    </section>\n"

    html_content += """
    <footer>
        Generated by Site Audit Tool
    </footer>
</body>
</html>
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return filepath


# =============================================================================
# MAIN ENTRY POINT (Required by main.py)
# =============================================================================

def generate_all_reports(results, url, site_path=None):
    """
    Generate all CSV reports for the audit results.
    This is the main entry point called by main.py.

    Args:
        results: List of audit result dicts OR dict with 'issues' key
        url: The audited site URL
        site_path: Path to site directory (e.g., ~/sites/lastingchange.co)

    Returns:
        Dict mapping report type to file path
    """
    output_dir = get_site_report_dir(url, site_path)

    print(f"Generating CSV reports in: {output_dir}")

    # Handle both list format (from engine) and dict format (legacy)
    if isinstance(results, list):
        issues = results
        # Wrap in dict for sub-functions that expect it
        results = {'issues': issues}
    else:
        issues = results.get('issues', [])

    generated_files = []

    # Count issues by actual type
    design_issues = [i for i in issues if i.get('type') in ('color', 'texture', 'section')]
    seo_issues = [i for i in issues if i.get('type') == 'seo']
    content_issues = [i for i in issues if i.get('type') == 'content']

    # Generate Design report (colors, textures, sections)
    if design_issues:
        path = generate_design_report(results, output_dir)
        generated_files.append(path)
        print(f"  ✓ Design report: {os.path.basename(path)} ({len(design_issues)} issues)")

    # Generate SEO report
    if seo_issues:
        path = generate_seo_report(results, output_dir)
        generated_files.append(path)
        print(f"  ✓ SEO report: {os.path.basename(path)} ({len(seo_issues)} issues)")

    # Generate Content report
    if content_issues:
        path = generate_content_report(results, output_dir)
        generated_files.append(path)
        print(f"  ✓ Content report: {os.path.basename(path)} ({len(content_issues)} issues)")

    # Generate variable candidates report (Design System Linter output)
    variable_candidates = [i for i in issues if i.get('variable_candidate')]
    if variable_candidates:
        path = generate_variable_candidates_report(results, output_dir)
        generated_files.append(path)
        print(f"  ✓ Variable candidates: {os.path.basename(path)} ({len(variable_candidates)} candidates)")
    
    # Always generate summary CSV
    summary_path = generate_summary_report(results, url, output_dir)
    generated_files.append(summary_path)
    print(f"  ✓ Summary report: {os.path.basename(summary_path)}")

    # Always generate HTML report
    html_path = generate_html_report(results, url, output_dir)
    generated_files.append(html_path)
    print(f"  ✓ HTML report: {os.path.basename(html_path)}")

    # Return dict of all generated files
    return {
        'summary': summary_path,
        'html': html_path,
        'all_files': generated_files,
        'output_dir': output_dir,
        'issue_count': len(issues)
    }
