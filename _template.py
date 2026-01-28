#!/usr/bin/env python3
"""
Site Palette Template
Copy this file to your site directory and rename to palette.py

Location: ~/sites/{your-site.com}/palette.py

This template includes:
- Brand color definitions
- Typography specifications
- Spacing scale
- VALUE_TO_VARIABLE reverse mapping for Design System Linting
"""

# =============================================================================
# SITE METADATA
# =============================================================================

SITE_NAME = "Your Site Name"
SITE_URL = "https://your-site.com"
WEBFLOW_SITE_ID = ""  # Optional: for MCP integration


# =============================================================================
# BRAND COLORS
# =============================================================================

BRAND_COLORS = {
    # Primary palette
    "primary": "#000000",
    "secondary": "#333333",
    "accent": "#0066cc",
    
    # Neutrals
    "surface-light": "#ffffff",
    "surface-dark": "#f4f4f4",
    "border": "#e0e0e0",
    
    # Text colors
    "text-primary": "#1a1a1a",
    "text-secondary": "#666666",
    "text-muted": "#999999",
    
    # Semantic colors
    "success": "#28a745",
    "warning": "#ffc107",
    "error": "#dc3545",
}


# =============================================================================
# TYPOGRAPHY
# =============================================================================

TYPOGRAPHY = {
    "font-family-heading": "Inter, sans-serif",
    "font-family-body": "Inter, sans-serif",
    
    # Heading sizes
    "heading-xl": "64px",
    "heading-lg": "48px",
    "heading-md": "36px",
    "heading-sm": "24px",
    
    # Body sizes
    "body-lg": "20px",
    "body-md": "16px",
    "body-sm": "14px",
    "body-xs": "12px",
    
    # Font weights
    "weight-regular": "400",
    "weight-medium": "500",
    "weight-semibold": "600",
    "weight-bold": "700",
    
    # Line heights
    "line-height-tight": "1.2",
    "line-height-normal": "1.5",
    "line-height-relaxed": "1.75",
}


# =============================================================================
# SPACING SCALE
# =============================================================================

SPACING = {
    "space-xs": "4px",
    "space-sm": "8px",
    "space-md": "16px",
    "space-lg": "24px",
    "space-xl": "32px",
    "space-2xl": "48px",
    "space-3xl": "64px",
    "space-4xl": "96px",
    
    # Semantic spacing
    "gutter": "24px",
    "section-padding": "80px",
    "container-max-width": "1200px",
}


# =============================================================================
# TEXTURES & EFFECTS (Optional)
# =============================================================================

TEXTURES = {
    # Example texture definitions
    # "linen-grain": {
    #     "asset_url": "https://cdn.example.com/textures/linen.avif",
    #     "default_opacity": 15,
    #     "blend_mode": "overlay",
    # },
}


# =============================================================================
# VALUE_TO_VARIABLE MAPPING
# Design System Linter uses this to identify hard-coded values
# that should be replaced with CSS variables
# =============================================================================

def build_value_to_variable_map():
    """
    Automatically builds the reverse mapping from the definitions above.
    Returns a dict: { "raw_value": "var(--variable-name)" }
    """
    mapping = {}
    
    # Map colors
    for name, value in BRAND_COLORS.items():
        css_var = f"var(--color-{name})"
        # Store both lowercase and original case for matching
        mapping[value.lower()] = css_var
        mapping[value.upper()] = css_var
    
    # Map typography values
    for name, value in TYPOGRAPHY.items():
        css_var = f"var(--{name})"
        mapping[value] = css_var
    
    # Map spacing values
    for name, value in SPACING.items():
        css_var = f"var(--{name})"
        mapping[value] = css_var
    
    return mapping


# Pre-built mapping for import
VALUE_TO_VARIABLE = build_value_to_variable_map()


# =============================================================================
# CUSTOM OVERRIDES (Optional)
# Add manual mappings for edge cases the auto-builder doesn't catch
# =============================================================================

CUSTOM_MAPPINGS = {
    # Example: map common variations
    # "rgb(26, 43, 60)": "var(--color-primary)",
    # "1.5em": "var(--line-height-normal)",
}

# Merge custom mappings
VALUE_TO_VARIABLE.update(CUSTOM_MAPPINGS)


# =============================================================================
# TOLERANCE SETTINGS
# How much variance is allowed before flagging as an issue
# =============================================================================

TOLERANCES = {
    "color_delta_e": 3.0,      # CIE Delta E color difference threshold
    "spacing_px": 2,           # Pixel tolerance for spacing values
    "font_size_px": 1,         # Pixel tolerance for font sizes
}


# =============================================================================
# AUDIT CONFIGURATION
# =============================================================================

AUDIT_CONFIG = {
    # Elements to skip during audit
    "ignore_selectors": [
        ".w-webflow-badge",
        ".w-nav-overlay",
        "#wf-form-*",
    ],
    
    # Pages to exclude from audit
    "ignore_pages": [
        "/404",
        "/password-protected",
    ],
    
    # Severity overrides for specific issues
    "severity_overrides": {
        # "color_mismatch": "high",
        # "missing_alt_text": "high",
    },
}
