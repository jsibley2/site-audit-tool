#!/usr/bin/env python3
"""
Design Auditor - Core Audit Engine
Scans pages for design system violations and identifies hard-coded values
that should be replaced with variables.

Location: ~/scripts/audit_tool/core/design_auditor.py
"""

import re
from urllib.parse import urljoin
from datetime import datetime


# =============================================================================
# COLOR UTILITIES
# =============================================================================

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_lab(rgb):
    """Convert RGB to LAB color space for Delta E calculation."""
    # Normalize RGB values
    r, g, b = [x / 255.0 for x in rgb]
    
    # Apply gamma correction
    r = ((r + 0.055) / 1.055) ** 2.4 if r > 0.04045 else r / 12.92
    g = ((g + 0.055) / 1.055) ** 2.4 if g > 0.04045 else g / 12.92
    b = ((b + 0.055) / 1.055) ** 2.4 if b > 0.04045 else b / 12.92
    
    # Convert to XYZ
    x = (r * 0.4124564 + g * 0.3575761 + b * 0.1804375) / 0.95047
    y = (r * 0.2126729 + g * 0.7151522 + b * 0.0721750) / 1.00000
    z = (r * 0.0193339 + g * 0.1191920 + b * 0.9503041) / 1.08883
    
    # Convert to LAB
    x = x ** (1/3) if x > 0.008856 else (7.787 * x) + (16/116)
    y = y ** (1/3) if y > 0.008856 else (7.787 * y) + (16/116)
    z = z ** (1/3) if z > 0.008856 else (7.787 * z) + (16/116)
    
    L = (116 * y) - 16
    a = 500 * (x - y)
    b = 200 * (y - z)
    
    return (L, a, b)


def delta_e(color1, color2):
    """Calculate CIE Delta E (color difference) between two colors."""
    lab1 = rgb_to_lab(hex_to_rgb(color1))
    lab2 = rgb_to_lab(hex_to_rgb(color2))
    
    return ((lab1[0] - lab2[0]) ** 2 + 
            (lab1[1] - lab2[1]) ** 2 + 
            (lab1[2] - lab2[2]) ** 2) ** 0.5


# =============================================================================
# VALUE DETECTION PATTERNS
# =============================================================================

# Regex patterns for detecting hard-coded values
PATTERNS = {
    'hex_color': re.compile(r'#([0-9A-Fa-f]{3}){1,2}\b'),
    'rgb_color': re.compile(r'rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(?:,\s*[\d.]+\s*)?\)'),
    'pixel_value': re.compile(r'\b(\d+)px\b'),
    'rem_value': re.compile(r'\b([\d.]+)rem\b'),
    'em_value': re.compile(r'\b([\d.]+)em\b'),
}


def extract_colors_from_css(css_text):
    """Extract all color values from CSS text."""
    colors = []
    
    # Find hex colors
    for match in PATTERNS['hex_color'].finditer(css_text):
        colors.append({
            'value': match.group(0),
            'type': 'hex',
            'position': match.start()
        })
    
    # Find RGB/RGBA colors
    for match in PATTERNS['rgb_color'].finditer(css_text):
        colors.append({
            'value': match.group(0),
            'type': 'rgb',
            'position': match.start()
        })
    
    return colors


def extract_spacing_from_css(css_text):
    """Extract all spacing/size values from CSS text."""
    values = []
    
    for match in PATTERNS['pixel_value'].finditer(css_text):
        values.append({
            'value': match.group(0),
            'numeric': int(match.group(1)),
            'unit': 'px',
            'position': match.start()
        })
    
    for match in PATTERNS['rem_value'].finditer(css_text):
        values.append({
            'value': match.group(0),
            'numeric': float(match.group(1)),
            'unit': 'rem',
            'position': match.start()
        })
    
    return values


# =============================================================================
# VARIABLE CANDIDATE DETECTION
# =============================================================================

def find_variable_candidate(value, value_to_variable_map, tolerances=None):
    """
    Check if a hard-coded value matches a design system variable.
    
    Args:
        value: The raw value found in CSS (e.g., "#0A1F44", "24px")
        value_to_variable_map: Dict mapping values to variable names
        tolerances: Optional dict with tolerance settings
    
    Returns:
        Dict with variable_name and match_type, or None if no match
    """
    tolerances = tolerances or {'color_delta_e': 3.0, 'spacing_px': 2}
    
    # Normalize the value for lookup
    normalized = value.lower().strip()
    
    # Direct match
    if normalized in value_to_variable_map:
        return {
            'variable_name': value_to_variable_map[normalized],
            'match_type': 'exact'
        }
    
    # Check uppercase version
    if value.upper() in value_to_variable_map:
        return {
            'variable_name': value_to_variable_map[value.upper()],
            'match_type': 'exact'
        }
    
    # For hex colors, try near-match using Delta E
    if normalized.startswith('#'):
        for known_value, var_name in value_to_variable_map.items():
            if known_value.startswith('#'):
                try:
                    diff = delta_e(normalized, known_value)
                    if diff <= tolerances['color_delta_e']:
                        return {
                            'variable_name': var_name,
                            'match_type': 'near',
                            'delta_e': round(diff, 2)
                        }
                except:
                    continue
    
    # For pixel values, try near-match within tolerance
    px_match = PATTERNS['pixel_value'].match(value)
    if px_match:
        found_px = int(px_match.group(1))
        for known_value, var_name in value_to_variable_map.items():
            known_match = PATTERNS['pixel_value'].match(known_value)
            if known_match:
                known_px = int(known_match.group(1))
                if abs(found_px - known_px) <= tolerances['spacing_px']:
                    return {
                        'variable_name': var_name,
                        'match_type': 'near',
                        'difference_px': found_px - known_px
                    }
    
    return None


# =============================================================================
# SOURCE CONTEXT DETECTION (Hiding Spots)
# =============================================================================

def detect_source_context(element_data):
    """
    Determine where a style is coming from (the "hiding spot").
    
    Args:
        element_data: Dict with element information from the scraper
    
    Returns:
        String indicating the source context
    """
    # Check for inline styles
    if element_data.get('has_inline_style'):
        return 'Inline Style'
    
    # Check for Webflow custom code embed
    if element_data.get('in_embed') or element_data.get('parent_is_embed'):
        return 'Custom Code Embed'
    
    # Check for global custom code
    if element_data.get('from_head') or element_data.get('from_footer'):
        return 'Global Custom Code'
    
    # Check for component override
    if element_data.get('is_component_override'):
        return 'Component Override'
    
    # Check for combo class
    if element_data.get('has_combo_class'):
        return 'Combo Class'
    
    # Default to standard class
    return 'Class Style'


# =============================================================================
# MAIN AUDIT FUNCTIONS
# =============================================================================

def audit_colors(page_data, palette, verbose=False):
    """
    Audit a page for color violations.
    
    Args:
        page_data: Dict containing scraped page data
        palette: Loaded palette module with BRAND_COLORS and VALUE_TO_VARIABLE
        verbose: Enable verbose logging
    
    Returns:
        List of issue dicts
    """
    issues = []
    value_map = getattr(palette, 'VALUE_TO_VARIABLE', {})
    tolerances = getattr(palette, 'TOLERANCES', {})
    brand_colors = getattr(palette, 'BRAND_COLORS', {})
    
    for element in page_data.get('elements', []):
        # Extract colors from element's computed styles
        styles = element.get('computed_styles', {})
        
        for prop in ['color', 'background-color', 'border-color', 'fill', 'stroke']:
            value = styles.get(prop)
            if not value:
                continue
            
            # Skip if it's already a CSS variable
            if 'var(--' in value:
                continue
            
            # Check if this is a hard-coded value that should be a variable
            candidate = find_variable_candidate(value, value_map, tolerances)
            
            if candidate:
                source_context = detect_source_context(element)
                
                issues.append({
                    'type': 'color',
                    'page_url': page_data.get('url', ''),
                    'element': element.get('tag', 'unknown'),
                    'selector': element.get('selector', ''),
                    'property': prop,
                    'found_value': value,
                    'expected_value': candidate['variable_name'],
                    'variable_candidate': candidate['variable_name'],
                    'match_type': candidate['match_type'],
                    'source_context': source_context,
                    'severity': 'high' if candidate['match_type'] == 'exact' else 'medium',
                    'notes': f"Hard-coded value should use variable: {candidate['variable_name']}"
                })
                
                if verbose:
                    print(f"  [COLOR] {element.get('selector')}: {value} → {candidate['variable_name']}")
    
    return issues


def audit_fonts(page_data, palette, verbose=False):
    """
    Audit a page for typography violations.
    
    Args:
        page_data: Dict containing scraped page data
        palette: Loaded palette module with TYPOGRAPHY
        verbose: Enable verbose logging
    
    Returns:
        List of issue dicts
    """
    issues = []
    value_map = getattr(palette, 'VALUE_TO_VARIABLE', {})
    tolerances = getattr(palette, 'TOLERANCES', {})
    
    for element in page_data.get('elements', []):
        styles = element.get('computed_styles', {})
        
        # Check font-size
        font_size = styles.get('font-size')
        if font_size and 'var(--' not in font_size:
            candidate = find_variable_candidate(font_size, value_map, tolerances)
            
            if candidate:
                source_context = detect_source_context(element)
                
                issues.append({
                    'type': 'font',
                    'page_url': page_data.get('url', ''),
                    'element': element.get('tag', 'unknown'),
                    'selector': element.get('selector', ''),
                    'property': 'font-size',
                    'found_value': font_size,
                    'expected_value': candidate['variable_name'],
                    'variable_candidate': candidate['variable_name'],
                    'font_size': font_size,
                    'font_weight': styles.get('font-weight', ''),
                    'line_height': styles.get('line-height', ''),
                    'source_context': source_context,
                    'severity': 'medium',
                    'notes': f"Font size should use variable: {candidate['variable_name']}"
                })
                
                if verbose:
                    print(f"  [FONT] {element.get('selector')}: {font_size} → {candidate['variable_name']}")
    
    return issues


def audit_spacing(page_data, palette, verbose=False):
    """
    Audit a page for spacing violations.
    
    Args:
        page_data: Dict containing scraped page data
        palette: Loaded palette module with SPACING
        verbose: Enable verbose logging
    
    Returns:
        List of issue dicts
    """
    issues = []
    value_map = getattr(palette, 'VALUE_TO_VARIABLE', {})
    tolerances = getattr(palette, 'TOLERANCES', {})
    
    spacing_props = [
        'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
        'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
        'gap', 'row-gap', 'column-gap'
    ]
    
    for element in page_data.get('elements', []):
        styles = element.get('computed_styles', {})
        
        for prop in spacing_props:
            value = styles.get(prop)
            if not value or value == '0px' or 'var(--' in value:
                continue
            
            candidate = find_variable_candidate(value, value_map, tolerances)
            
            if candidate:
                source_context = detect_source_context(element)
                
                issues.append({
                    'type': 'spacing',
                    'page_url': page_data.get('url', ''),
                    'element': element.get('tag', 'unknown'),
                    'selector': element.get('selector', ''),
                    'property': prop,
                    'found_value': value,
                    'expected_value': candidate['variable_name'],
                    'variable_candidate': candidate['variable_name'],
                    'source_context': source_context,
                    'severity': 'low',
                    'notes': f"Spacing should use variable: {candidate['variable_name']}"
                })
                
                if verbose:
                    print(f"  [SPACING] {element.get('selector')}: {prop}={value} → {candidate['variable_name']}")
    
    return issues


def audit_images(page_data, palette, verbose=False):
    """
    Audit a page for image issues (alt text, sizing, format).
    
    Args:
        page_data: Dict containing scraped page data
        palette: Loaded palette module (not heavily used for images)
        verbose: Enable verbose logging
    
    Returns:
        List of issue dicts
    """
    issues = []
    
    for image in page_data.get('images', []):
        # Check for missing alt text
        if not image.get('alt'):
            issues.append({
                'type': 'image',
                'page_url': page_data.get('url', ''),
                'image_url': image.get('src', ''),
                'alt_text': '',
                'issue_subtype': 'missing_alt',
                'current_size': image.get('file_size', ''),
                'recommended_size': '',
                'dimensions': f"{image.get('width', '?')}x{image.get('height', '?')}",
                'format': image.get('format', ''),
                'severity': 'high',
                'notes': 'Image missing alt text (accessibility issue)'
            })
        
        # Check for oversized images
        file_size_kb = image.get('file_size_kb', 0)
        if file_size_kb > 500:
            issues.append({
                'type': 'image',
                'page_url': page_data.get('url', ''),
                'image_url': image.get('src', ''),
                'alt_text': image.get('alt', ''),
                'issue_subtype': 'oversized',
                'current_size': f"{file_size_kb}KB",
                'recommended_size': '< 500KB',
                'dimensions': f"{image.get('width', '?')}x{image.get('height', '?')}",
                'format': image.get('format', ''),
                'severity': 'medium',
                'notes': f'Image is {file_size_kb}KB, consider optimizing'
            })
        
        if verbose and issues:
            print(f"  [IMAGE] {image.get('src', 'unknown')}: {len(issues)} issue(s)")
    
    return issues


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def run_audit(url, palette, audit_types, verbose=False, site_config=None):
    """
    Main entry point for running design audits.
    
    Args:
        url: The site URL to audit
        palette: Loaded palette module
        audit_types: List of audit types to run ('colors', 'fonts', 'spacing', 'images')
        verbose: Enable verbose output
        site_config: Optional site configuration dict
    
    Returns:
        Dict containing all audit results
    """
    site_config = site_config or {}
    
    results = {
        'url': url,
        'timestamp': datetime.now().isoformat(),
        'audit_types': audit_types,
        'issues': [],
        'summary': {
            'total_issues': 0,
            'by_type': {},
            'by_severity': {'high': 0, 'medium': 0, 'low': 0},
            'by_source_context': {}
        }
    }
    
    # Import the scraper (would be implemented separately)
    try:
        from core.page_scraper import scrape_site
        pages_data = scrape_site(url, site_config)
    except ImportError:
        if verbose:
            print("Note: page_scraper not available, using placeholder data")
        # Placeholder for testing without scraper
        pages_data = [{'url': url, 'elements': [], 'images': []}]
    
    # Run requested audits on each page
    for page_data in pages_data:
        if verbose:
            print(f"\nAuditing: {page_data.get('url', url)}")
        
        if 'colors' in audit_types:
            results['issues'].extend(audit_colors(page_data, palette, verbose))
        
        if 'fonts' in audit_types:
            results['issues'].extend(audit_fonts(page_data, palette, verbose))
        
        if 'spacing' in audit_types:
            results['issues'].extend(audit_spacing(page_data, palette, verbose))
        
        if 'images' in audit_types:
            results['issues'].extend(audit_images(page_data, palette, verbose))
    
    # Build summary
    for issue in results['issues']:
        issue_type = issue.get('type', 'unknown')
        severity = issue.get('severity', 'medium')
        source = issue.get('source_context', 'Unknown')
        
        results['summary']['by_type'][issue_type] = results['summary']['by_type'].get(issue_type, 0) + 1
        results['summary']['by_severity'][severity] = results['summary']['by_severity'].get(severity, 0) + 1
        results['summary']['by_source_context'][source] = results['summary']['by_source_context'].get(source, 0) + 1
    
    results['summary']['total_issues'] = len(results['issues'])
    
    return results
