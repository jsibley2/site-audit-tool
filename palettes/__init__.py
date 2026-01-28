"""
Brand palette definitions.

Each palette file defines approved colors, textures, and section-specific rules
for a particular website or brand.

Available palettes:
    - lasting_change: LASTING CHANGE executive coaching website
"""

# Import the default palette for convenience
try:
    from palettes.lasting_change import (
        BRAND_COLORS,
        BRAND_GRADIENTS,
        APPROVED_TEXTURES,
        APPROVED_BLEND_MODES,
        TEXTURE_OPACITY_RANGE,
        SECTION_RULES,
        get_color_name,
        get_section_rules,
        is_approved_color,
        is_approved_texture,
        get_all_approved_hex_codes,
    )
except ImportError:
    # Palette file not yet created
    pass

__all__ = [
    "BRAND_COLORS",
    "BRAND_GRADIENTS", 
    "APPROVED_TEXTURES",
    "APPROVED_BLEND_MODES",
    "TEXTURE_OPACITY_RANGE",
    "SECTION_RULES",
    "get_color_name",
    "get_section_rules",
    "is_approved_color",
    "is_approved_texture",
    "get_all_approved_hex_codes",
]
