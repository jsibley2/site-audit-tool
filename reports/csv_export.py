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
    
    # Count by type
    color_count = len([i for i in issues if i.get('type') == 'color'])
    font_count = len([i for i in issues if i.get('type') == 'font'])
    spacing_count = len([i for i in issues if i.get('type') == 'spacing'])
    image_count = len([i for i in issues if i.get('type') == 'image'])
    
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
        writer.writerow(['Fonts', font_count])
        writer.writerow(['Spacing', spacing_count])
        writer.writerow(['Images', image_count])
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
# MAIN ENTRY POINT (Required by main.py)
# =============================================================================

def generate_all_reports(results, url, site_path=None):
    """
    Generate all CSV reports for the audit results.
    This is the main entry point called by main.py.
    
    Args:
        results: Dict containing all audit results
        url: The audited site URL
        site_path: Path to site directory (e.g., ~/sites/lastingchange.co)
    
    Returns:
        Path to the summary report (main output file)
    """
    output_dir = get_site_report_dir(url, site_path)
    
    print(f"Generating CSV reports in: {output_dir}")
    
    issues = results.get('issues', [])
    audit_types = results.get('audit_types', [])
    
    generated_files = []
    
    # Generate type-specific reports only if there are issues of that type
    if 'colors' in audit_types:
        color_issues = [i for i in issues if i.get('type') == 'color']
        if color_issues:
            path = generate_color_report(results, output_dir)
            generated_files.append(path)
            print(f"  ✓ Color report: {os.path.basename(path)} ({len(color_issues)} issues)")
    
    if 'fonts' in audit_types:
        font_issues = [i for i in issues if i.get('type') == 'font']
        if font_issues:
            path = generate_font_report(results, output_dir)
            generated_files.append(path)
            print(f"  ✓ Font report: {os.path.basename(path)} ({len(font_issues)} issues)")
    
    if 'spacing' in audit_types:
        spacing_issues = [i for i in issues if i.get('type') == 'spacing']
        if spacing_issues:
            path = generate_spacing_report(results, output_dir)
            generated_files.append(path)
            print(f"  ✓ Spacing report: {os.path.basename(path)} ({len(spacing_issues)} issues)")
    
    if 'images' in audit_types:
        image_issues = [i for i in issues if i.get('type') == 'image']
        if image_issues:
            path = generate_image_report(results, output_dir)
            generated_files.append(path)
            print(f"  ✓ Image report: {os.path.basename(path)} ({len(image_issues)} issues)")
    
    # Generate variable candidates report (Design System Linter output)
    variable_candidates = [i for i in issues if i.get('variable_candidate')]
    if variable_candidates:
        path = generate_variable_candidates_report(results, output_dir)
        generated_files.append(path)
        print(f"  ✓ Variable candidates: {os.path.basename(path)} ({len(variable_candidates)} candidates)")
    
    # Always generate summary
    summary_path = generate_summary_report(results, url, output_dir)
    generated_files.append(summary_path)
    print(f"  ✓ Summary report: {os.path.basename(summary_path)}")
    
    return summary_path
