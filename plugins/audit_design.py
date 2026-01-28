"""
================================================================================
PLUGINS / AUDIT_DESIGN.PY - Enhanced Design Consistency Auditor
================================================================================
Audits colors and textures against the approved brand palette with enhanced
context fields for tracking down issues in Webflow.

Enhanced Context Fields:
- full_selector: Complete CSS path (e.g., .hero-section > .container > h2.heading-xl)
- parent_context: Immediate parent element for disambiguation
- source_context: Where the style originates (Inline, Class, Embed, External CSS)

This plugin checks:
- Colors: Are all colors in the approved palette? Any near-misses or rogues?
- Textures: Are approved texture files being used with correct blend modes/opacity?
- Section Rules: Does each section match its expected design specifications?

Output format uses "Expected vs Found" columns for clear accountability.

Author: Built with Claude in BoodleBox
Date: January 2026
================================================================================
"""

import re
import math
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag
import requests

# Try to import configuration with fallbacks
try:
    from config import (
        COLOR_PROPERTIES,
        TEXTURE_PROPERTIES,
        COLOR_NEAR_MISS_THRESHOLD,
        STATUS_MATCH,
        STATUS_NEAR_MISS,
        STATUS_MISMATCH,
        STATUS_MISSING,
        STATUS_ROGUE,
        STATUS_IN_RANGE,
        STATUS_OUT_OF_RANGE,
    )
except ImportError:
    # Fallback defaults
    COLOR_PROPERTIES = [
        "color", "background-color", "background", "border-color",
        "border-top-color", "border-right-color", "border-bottom-color",
        "border-left-color", "outline-color", "fill", "stroke",
        "box-shadow", "text-shadow"
    ]
    TEXTURE_PROPERTIES = ["background-image", "background"]
    COLOR_NEAR_MISS_THRESHOLD = 25
    STATUS_MATCH = "✅ Match"
    STATUS_NEAR_MISS = "⚠️ Near-miss"
    STATUS_MISMATCH = "❌ Mismatch"
    STATUS_MISSING = "❌ Missing"
    STATUS_ROGUE = "❌ Rogue"
    STATUS_IN_RANGE = "✅ In range"
    STATUS_OUT_OF_RANGE = "❌ Out of range"


class DesignAuditor:
    """
    Audits a webpage for design consistency against an approved palette.
    
    Enhanced to provide detailed context for tracking down issues:
    - full_selector: Complete CSS selector path
    - parent_context: Parent element hierarchy
    - source_context: Where the style originates
    """
    
    def __init__(self, palette_name: str = "lasting_change", palette_module=None):
        """
        Initialize the design auditor with a specific palette.

        Args:
            palette_name: Name of the palette module to load from palettes/
            palette_module: Optional pre-loaded palette module (takes precedence)
        """
        self.palette_name = palette_name

        # Use provided module or load by name
        if palette_module is not None:
            self.palette = self._extract_palette_from_module(palette_module)
        else:
            self.palette = self._load_palette(palette_name)

        # Ensure we always have a valid palette structure
        if self.palette is None:
            self.palette = self._get_empty_palette()
            self.palette_loaded = False
        else:
            self.palette_loaded = True

        # Pre-compute approved colors for fast lookup
        self.approved_colors = set()
        for hex_code in self.palette.get("BRAND_COLORS", {}).keys():
            if hex_code != "transparent":
                self.approved_colors.add(hex_code.lower())

        # Cache for external stylesheets
        self._stylesheet_cache = {}

    def _get_empty_palette(self) -> Dict:
        """Return an empty palette structure with sensible defaults."""
        return {
            "BRAND_COLORS": {},
            "BRAND_GRADIENTS": {},
            "APPROVED_TEXTURES": {},
            "APPROVED_BLEND_MODES": [],
            "TEXTURE_OPACITY_RANGE": (0.05, 0.20),
            "SECTION_RULES": {},
            "get_color_name": lambda x: "Unknown",
            "get_section_rules": lambda x: None,
        }

    def _extract_palette_from_module(self, palette_module) -> Optional[Dict]:
        """
        Extract palette data from a pre-loaded module.

        Args:
            palette_module: A loaded Python module with palette attributes

        Returns:
            Dict with palette data or None
        """
        try:
            return {
                "BRAND_COLORS": getattr(palette_module, "BRAND_COLORS", {}),
                "BRAND_GRADIENTS": getattr(palette_module, "BRAND_GRADIENTS", {}),
                "APPROVED_TEXTURES": getattr(palette_module, "APPROVED_TEXTURES", {}),
                "APPROVED_BLEND_MODES": getattr(palette_module, "APPROVED_BLEND_MODES", []),
                "TEXTURE_OPACITY_RANGE": getattr(palette_module, "TEXTURE_OPACITY_RANGE", (0.05, 0.20)),
                "SECTION_RULES": getattr(palette_module, "SECTION_RULES", {}),
                "get_color_name": getattr(palette_module, "get_color_name", lambda x: "Unknown"),
                "get_section_rules": getattr(palette_module, "get_section_rules", lambda x: None),
            }
        except Exception as e:
            print(f"⚠️ Could not extract palette from module: {e}")
            return None
    
    def _load_palette(self, palette_name: str) -> Optional[Dict]:
        """
        Dynamically load a palette module.
        """
        try:
            palette_module = __import__(f"palettes.{palette_name}", fromlist=[palette_name])
            
            return {
                "BRAND_COLORS": getattr(palette_module, "BRAND_COLORS", {}),
                "BRAND_GRADIENTS": getattr(palette_module, "BRAND_GRADIENTS", {}),
                "APPROVED_TEXTURES": getattr(palette_module, "APPROVED_TEXTURES", {}),
                "APPROVED_BLEND_MODES": getattr(palette_module, "APPROVED_BLEND_MODES", []),
                "TEXTURE_OPACITY_RANGE": getattr(palette_module, "TEXTURE_OPACITY_RANGE", (0.05, 0.20)),
                "SECTION_RULES": getattr(palette_module, "SECTION_RULES", {}),
                "get_color_name": getattr(palette_module, "get_color_name", lambda x: "Unknown"),
                "get_section_rules": getattr(palette_module, "get_section_rules", lambda x: None),
            }
        except ImportError as e:
            print(f"⚠️ Could not load palette '{palette_name}': {e}")
            print("Using empty palette - all colors will be flagged as 'Unknown'")
            return None
    
    # ==========================================================================
    # CONTEXT EXTRACTION HELPERS
    # ==========================================================================
    
    def _get_full_selector(self, element: Tag) -> str:
        """
        Build the full CSS selector path for an element.
        
        Example output: ".hero-section > .container > h2.heading-xl.is-white"
        
        Args:
            element: BeautifulSoup Tag element
            
        Returns:
            Full CSS selector string
        """
        parts = []
        current = element
        
        # Walk up the tree (limit to 5 levels to avoid overly long selectors)
        depth = 0
        while current and current.name and depth < 5:
            # Build selector for this element
            selector = current.name
            
            # Add classes
            classes = current.get("class", [])
            if classes:
                selector += "." + ".".join(classes)
            
            # Add ID if present (but not Webflow's auto-generated IDs)
            element_id = current.get("id", "")
            if element_id and not element_id.startswith("w-"):
                selector = f"#{element_id}"
            
            parts.insert(0, selector)
            current = current.parent
            depth += 1
        
        return " > ".join(parts)
    
    def _get_parent_context(self, element: Tag) -> str:
        """
        Get the immediate parent context for disambiguation.
        
        Example output: ".hero-section > .content-wrapper"
        
        Args:
            element: BeautifulSoup Tag element
            
        Returns:
            Parent context string
        """
        parents = []
        current = element.parent
        
        # Get up to 2 parent levels
        depth = 0
        while current and current.name and depth < 2:
            selector = current.name
            classes = current.get("class", [])
            if classes:
                selector += "." + ".".join(classes)
            parents.insert(0, selector)
            current = current.parent
            depth += 1
        
        return " > ".join(parents) if parents else "root"
    
    def _determine_source_context(self, element: Tag, property_name: str, 
                                   found_in: str = "inline") -> str:
        """
        Determine where a style originates from.
        
        Args:
            element: The element being audited
            property_name: The CSS property being checked
            found_in: Where the style was found ("inline", "embedded", URL, etc.)
            
        Returns:
            Human-readable source context string
        """
        if found_in == "inline":
            return "Inline Style"
        elif found_in == "embedded":
            return "Custom Code Embed"
        elif found_in.startswith("http"):
            # External stylesheet
            parsed = urlparse(found_in)
            filename = parsed.path.split("/")[-1]
            if "webflow" in filename.lower():
                return f"Class Style ({filename})"
            return f"External CSS ({filename})"
        elif found_in == "global":
            return "Global Style"
        else:
            return f"Class Style ({found_in})"
    
    def _get_text_snippet(self, element: Tag, max_length: int = 50) -> str:
        """
        Extract a text snippet from an element for identification.
        
        Args:
            element: BeautifulSoup Tag element
            max_length: Maximum length of snippet
            
        Returns:
            Text snippet string
        """
        text = element.get_text(strip=True)
        if len(text) > max_length:
            return text[:max_length - 3] + "..."
        return text
    
    # ==========================================================================
    # MAIN AUDIT ENTRY POINT
    # ==========================================================================
    
    def audit(self, url: str, html: str) -> List[Dict[str, Any]]:
        """
        Audit a page for design consistency.
        
        This is the main entry point called by the crawler engine.
        
        Args:
            url: The URL of the page being audited
            html: The HTML content of the page
            
        Returns:
            List of audit result dictionaries with enhanced context
        """
        results = []
        
        # Parse the HTML
        soup = BeautifulSoup(html, "html.parser")
        
        # Phase 1: Extract colors from inline styles
        inline_results = self._extract_inline_colors(soup, url)
        results.extend(inline_results)
        
        # Phase 2: Extract colors from <style> tags (Custom Code Embeds)
        embedded_results = self._extract_embedded_colors(soup, url)
        results.extend(embedded_results)
        
        # Phase 3: Extract colors from external stylesheets
        external_results = self._extract_external_colors(soup, url)
        results.extend(external_results)
        
        # Phase 4: Extract and validate textures
        texture_results = self._extract_textures(soup, url)
        results.extend(texture_results)
        
        # Phase 5: Section-specific validation
        if self.palette and self.palette.get("SECTION_RULES"):
            section_results = self._validate_sections(soup, url)
            results.extend(section_results)
        
        return results
    
    # ==========================================================================
    # COLOR EXTRACTION - INLINE STYLES
    # ==========================================================================
    
    def _extract_inline_colors(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """
        Extract colors from inline style attributes.
        """
        results = []
        
        for element in soup.find_all(style=True):
            style = element.get("style", "")
            colors = self._parse_colors_from_style(style)
            
            for prop, color in colors:
                result = self._evaluate_color(
                    color=color,
                    element=element,
                    property_name=prop,
                    source="inline",
                    url=url
                )
                results.append(result)
        
        return results
    
    # ==========================================================================
    # COLOR EXTRACTION - EMBEDDED STYLES (<style> tags)
    # ==========================================================================
    
    def _extract_embedded_colors(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """
        Extract colors from <style> tags (Custom Code Embeds in Webflow).
        """
        results = []
        
        for style_tag in soup.find_all("style"):
            css_content = style_tag.string or ""
            css_results = self._parse_css_for_colors(css_content, soup, "embedded", url)
            results.extend(css_results)
        
        return results
    
    # ==========================================================================
    # COLOR EXTRACTION - EXTERNAL STYLESHEETS
    # ==========================================================================
    
    def _extract_external_colors(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """
        Extract colors from linked stylesheets.
        """
        results = []
        
        for link in soup.find_all("link", rel="stylesheet"):
            href = link.get("href")
            if href:
                stylesheet_url = urljoin(url, href)
                
                # Check cache first
                if stylesheet_url in self._stylesheet_cache:
                    css_content = self._stylesheet_cache[stylesheet_url]
                else:
                    try:
                        response = requests.get(stylesheet_url, timeout=10)
                        if response.status_code == 200:
                            css_content = response.text
                            self._stylesheet_cache[stylesheet_url] = css_content
                        else:
                            continue
                    except Exception as e:
                        print(f"  ⚠️ Could not fetch stylesheet {stylesheet_url}: {e}")
                        continue
                
                css_results = self._parse_css_for_colors(css_content, soup, stylesheet_url, url)
                results.extend(css_results)
        
        return results
    
    # ==========================================================================
    # CSS PARSING
    # ==========================================================================
    
    def _parse_css_for_colors(self, css: str, soup: BeautifulSoup, 
                               source: str, url: str) -> List[Dict[str, Any]]:
        """
        Parse CSS content and extract all color values with context.
        """
        results = []
        
        # Regex to match CSS rules: selector { properties }
        rule_pattern = r'([^{]+)\{([^}]+)\}'
        
        for match in re.finditer(rule_pattern, css):
            selector = match.group(1).strip()
            properties = match.group(2)
            
            # Try to find matching elements in the DOM for context
            matching_elements = []
            try:
                # Clean up selector for BeautifulSoup (remove pseudo-elements)
                clean_selector = re.sub(r'::?[a-z-]+', '', selector)
                clean_selector = re.sub(r'\[.*?\]', '', clean_selector)
                if clean_selector.strip():
                    matching_elements = soup.select(clean_selector.strip())
            except (ValueError, SyntaxError, NotImplementedError) as e:
                # Invalid CSS selectors are expected for some edge cases
                pass
            
            # Extract colors from properties
            colors = self._parse_colors_from_style(properties)
            
            for prop, color in colors:
                # Use first matching element for context, or create synthetic context
                if matching_elements:
                    element = matching_elements[0]
                    full_selector = self._get_full_selector(element)
                    parent_context = self._get_parent_context(element)
                    text_snippet = self._get_text_snippet(element)
                else:
                    full_selector = selector
                    parent_context = "CSS Rule (no DOM match)"
                    text_snippet = ""
                
                result = {
                    "url": url,
                    "type": "color",
                    "element": selector.split()[-1] if selector else "unknown",
                    "full_selector": full_selector,
                    "parent_context": parent_context,
                    "property": prop,
                    "source_context": self._determine_source_context(None, prop, source),
                    "text_snippet": text_snippet,
                }
                
                # Evaluate the color
                evaluation = self._evaluate_color_value(color)
                result.update(evaluation)
                
                results.append(result)
        
        return results
    
    def _parse_colors_from_style(self, style: str) -> List[Tuple[str, str]]:
        """
        Extract color values from a CSS style string.
        
        Handles hex, RGB/RGBA, HSL/HSLA, and named colors.
        """
        colors = []
        
        for prop in COLOR_PROPERTIES:
            pattern = rf'{prop}\s*:\s*([^;]+)'
            match = re.search(pattern, style, re.IGNORECASE)
            
            if match:
                value = match.group(1).strip()
                
                # Extract hex colors
                hex_matches = re.findall(r'#[0-9a-fA-F]{3,8}', value)
                for hex_color in hex_matches:
                    colors.append((prop, self._normalize_hex(hex_color)))
                
                # Extract rgb/rgba colors
                rgb_matches = re.findall(r'rgba?\([^)]+\)', value)
                for rgb_color in rgb_matches:
                    hex_equiv = self._rgb_to_hex(rgb_color)
                    if hex_equiv:
                        colors.append((prop, hex_equiv))
                
                # Extract hsl/hsla colors
                hsl_matches = re.findall(r'hsla?\([^)]+\)', value)
                for hsl_color in hsl_matches:
                    hex_equiv = self._hsl_to_hex(hsl_color)
                    if hex_equiv:
                        colors.append((prop, hex_equiv))
                
                # Check for 'transparent' keyword
                if 'transparent' in value.lower():
                    colors.append((prop, 'transparent'))
        
        return colors
    
    # ==========================================================================
    # COLOR EVALUATION
    # ==========================================================================
    
    def _evaluate_color(self, color: str, element: Tag, property_name: str,
                        source: str, url: str) -> Dict[str, Any]:
        """
        Evaluate a color against the approved palette with full context.
        """
        result = {
            "url": url,
            "type": "color",
            "element": element.name,
            "full_selector": self._get_full_selector(element),
            "parent_context": self._get_parent_context(element),
            "property": property_name,
            "source_context": self._determine_source_context(element, property_name, source),
            "text_snippet": self._get_text_snippet(element),
        }
        
        evaluation = self._evaluate_color_value(color)
        result.update(evaluation)
        
        return result
    
    def _evaluate_color_value(self, color: str) -> Dict[str, Any]:
        """
        Evaluate a color value and return expected/found/status.
        """
        color_lower = color.lower()
        
        # Handle transparent
        if color_lower == "transparent":
            return {
                "expected": "Any approved color or transparent",
                "found": "transparent",
                "status": STATUS_MATCH,
            }
        
        # Check if color is in approved palette
        if color_lower in self.approved_colors:
            color_name = self.palette["get_color_name"](color_lower) if self.palette else "Unknown"
            return {
                "expected": f"{color_name} ({color_lower})",
                "found": color_lower,
                "status": STATUS_MATCH,
            }
        
        # Check for near-miss (typo or eyeballed value)
        nearest, distance = self._find_nearest_color(color_lower)
        if nearest and distance <= COLOR_NEAR_MISS_THRESHOLD:
            nearest_name = self.palette["get_color_name"](nearest) if self.palette else "Unknown"
            return {
                "expected": f"{nearest_name} ({nearest})",
                "found": color_lower,
                "status": f"{STATUS_NEAR_MISS} (Δ{distance:.0f})",
            }
        
        # Rogue color - not in palette
        return {
            "expected": "Any approved palette color",
            "found": color_lower,
            "status": STATUS_ROGUE,
        }
    
    # ==========================================================================
    # TEXTURE EXTRACTION AND VALIDATION
    # ==========================================================================
    
    def _extract_textures(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """
        Extract and validate texture usage with full context.
        """
        results = []
        
        if not self.palette:
            return results
        
        approved_textures = self.palette.get("APPROVED_TEXTURES", {})
        approved_blend_modes = self.palette.get("APPROVED_BLEND_MODES", [])
        opacity_range = self.palette.get("TEXTURE_OPACITY_RANGE", (0.05, 0.20))
        
        # Find elements with background-image styles
        for element in soup.find_all(style=True):
            style = element.get("style", "")
            
            # Check for background-image
            bg_match = re.search(r'background-image\s*:\s*url\(["\']?([^"\')\s]+)["\']?\)', style)
            if bg_match:
                texture_url = bg_match.group(1)
                texture_filename = texture_url.split('/')[-1].split('?')[0]
                
                base_result = {
                    "url": url,
                    "type": "texture",
                    "element": element.name,
                    "full_selector": self._get_full_selector(element),
                    "parent_context": self._get_parent_context(element),
                    "source_context": "Inline Style",
                    "text_snippet": self._get_text_snippet(element),
                }
                
                # Validate texture file
                if texture_filename.lower() in [t.lower() for t in approved_textures.keys()]:
                    results.append({
                        **base_result,
                        "property": "texture-file",
                        "expected": f"Approved: {', '.join(approved_textures.keys())}",
                        "found": texture_filename,
                        "status": STATUS_MATCH,
                    })
                else:
                    results.append({
                        **base_result,
                        "property": "texture-file",
                        "expected": f"Approved: {', '.join(approved_textures.keys())}",
                        "found": texture_filename,
                        "status": f"{STATUS_MISMATCH} (unapproved file)",
                    })
            
            # Check for blend mode
            blend_match = re.search(r'(?:mix-blend-mode|background-blend-mode)\s*:\s*([^;]+)', style)
            if blend_match:
                blend_mode = blend_match.group(1).strip().lower()
                
                base_result = {
                    "url": url,
                    "type": "texture",
                    "element": element.name,
                    "full_selector": self._get_full_selector(element),
                    "parent_context": self._get_parent_context(element),
                    "source_context": "Inline Style",
                    "text_snippet": "",
                }
                
                if blend_mode in [m.lower() for m in approved_blend_modes]:
                    results.append({
                        **base_result,
                        "property": "blend-mode",
                        "expected": f"Approved: {', '.join(approved_blend_modes)}",
                        "found": blend_mode,
                        "status": STATUS_MATCH,
                    })
                else:
                    results.append({
                        **base_result,
                        "property": "blend-mode",
                        "expected": f"Approved: {', '.join(approved_blend_modes)}",
                        "found": blend_mode,
                        "status": STATUS_MISMATCH,
                    })
            
            # Check for opacity
            opacity_match = re.search(r'opacity\s*:\s*([\d.]+)', style)
            if opacity_match:
                opacity = float(opacity_match.group(1))
                min_opacity, max_opacity = opacity_range
                
                base_result = {
                    "url": url,
                    "type": "texture",
                    "element": element.name,
                    "full_selector": self._get_full_selector(element),
                    "parent_context": self._get_parent_context(element),
                    "source_context": "Inline Style",
                    "text_snippet": "",
                }
                
                if min_opacity <= opacity <= max_opacity:
                    results.append({
                        **base_result,
                        "property": "opacity",
                        "expected": f"{min_opacity*100:.0f}–{max_opacity*100:.0f}%",
                        "found": f"{opacity*100:.0f}%",
                        "status": STATUS_IN_RANGE,
                    })
                else:
                    results.append({
                        **base_result,
                        "property": "opacity",
                        "expected": f"{min_opacity*100:.0f}–{max_opacity*100:.0f}%",
                        "found": f"{opacity*100:.0f}%",
                        "status": STATUS_OUT_OF_RANGE,
                    })
        
        return results
    
    # ==========================================================================
    # SECTION VALIDATION
    # ==========================================================================
    
    def _validate_sections(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """
        Validate section-specific design rules with full context.
        """
        results = []
        section_rules = self.palette.get("SECTION_RULES", {})
        get_section_rules = self.palette.get("get_section_rules", lambda x: None)
        
        for element in soup.find_all(['div', 'section', 'footer', 'header']):
            classes = element.get("class", [])
            if not classes:
                continue
            
            class_string = " ".join(classes)
            rules = get_section_rules(class_string)
            
            if rules:
                style = element.get("style", "")
                
                base_result = {
                    "url": url,
                    "type": "section",
                    "element": element.name,
                    "full_selector": self._get_full_selector(element),
                    "parent_context": self._get_parent_context(element),
                    "source_context": "Section Rules",
                    "text_snippet": self._get_text_snippet(element),
                }
                
                # Validate background color
                if rules.get("background_color"):
                    expected_color = rules["background_color"]
                    
                    bg_match = re.search(r'background(?:-color)?\s*:\s*([^;]+)', style)
                    found_color = bg_match.group(1).strip() if bg_match else "not found in inline style"
                    
                    if found_color.startswith('#'):
                        found_color = self._normalize_hex(found_color)
                    
                    status = STATUS_MATCH if found_color.lower() == expected_color.lower() else STATUS_MISMATCH
                    
                    results.append({
                        **base_result,
                        "property": "background-color",
                        "expected": expected_color,
                        "found": found_color,
                        "status": status,
                    })
                
                # Validate blend mode
                if rules.get("blend_mode"):
                    expected_blend = rules["blend_mode"]
                    
                    blend_match = re.search(r'(?:mix-blend-mode|background-blend-mode)\s*:\s*([^;]+)', style)
                    found_blend = blend_match.group(1).strip() if blend_match else "not found"
                    
                    status = STATUS_MATCH if found_blend.lower() == expected_blend.lower() else STATUS_MISMATCH
                    
                    results.append({
                        **base_result,
                        "property": "blend-mode",
                        "expected": expected_blend,
                        "found": found_blend,
                        "status": status,
                    })
                
                # Validate opacity range
                if rules.get("opacity_range"):
                    min_op, max_op = rules["opacity_range"]
                    expected_opacity = f"{min_op*100:.0f}–{max_op*100:.0f}%"
                    
                    opacity_match = re.search(r'opacity\s*:\s*([\d.]+)', style)
                    if opacity_match:
                        found_opacity = float(opacity_match.group(1))
                        found_str = f"{found_opacity*100:.0f}%"
                        status = STATUS_IN_RANGE if min_op <= found_opacity <= max_op else STATUS_OUT_OF_RANGE
                    else:
                        found_str = "not found"
                        status = STATUS_MISSING
                    
                    results.append({
                        **base_result,
                        "property": "opacity",
                        "expected": expected_opacity,
                        "found": found_str,
                        "status": status,
                    })
        
        return results
    
    # ==========================================================================
    # COLOR CONVERSION UTILITIES
    # ==========================================================================
    
    def _normalize_hex(self, hex_color: str) -> str:
        """Normalize a hex color to lowercase 6-digit format."""
        hex_color = hex_color.lower().strip()
        hex_value = hex_color.lstrip('#')
        
        if len(hex_value) == 3:
            hex_value = ''.join([c * 2 for c in hex_value])
        
        if len(hex_value) == 8:
            hex_value = hex_value[:6]
        
        return f"#{hex_value}"
    
    def _rgb_to_hex(self, rgb_string: str) -> Optional[str]:
        """Convert rgb() or rgba() to hex."""
        try:
            numbers = re.findall(r'[\d.]+', rgb_string)
            if len(numbers) >= 3:
                r = int(float(numbers[0]))
                g = int(float(numbers[1]))
                b = int(float(numbers[2]))
                return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            pass
        return None
    
    def _hsl_to_hex(self, hsl_string: str) -> Optional[str]:
        """Convert hsl() or hsla() to hex."""
        try:
            numbers = re.findall(r'[\d.]+', hsl_string)
            if len(numbers) >= 3:
                h = float(numbers[0]) / 360
                s = float(numbers[1]) / 100
                l = float(numbers[2]) / 100
                
                if s == 0:
                    r = g = b = l
                else:
                    def hue_to_rgb(p, q, t):
                        if t < 0: t += 1
                        if t > 1: t -= 1
                        if t < 1/6: return p + (q - p) * 6 * t
                        if t < 1/2: return q
                        if t < 2/3: return p + (q - p) * (2/3 - t) * 6
                        return p
                    
                    q = l * (1 + s) if l < 0.5 else l + s - l * s
                    p = 2 * l - q
                    r = hue_to_rgb(p, q, h + 1/3)
                    g = hue_to_rgb(p, q, h)
                    b = hue_to_rgb(p, q, h - 1/3)
                
                return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        except (ValueError, IndexError):
            pass
        return None
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_value = hex_color.lstrip('#')
        if len(hex_value) == 3:
            hex_value = ''.join([c * 2 for c in hex_value])
        
        return (
            int(hex_value[0:2], 16),
            int(hex_value[2:4], 16),
            int(hex_value[4:6], 16),
        )
    
    def _find_nearest_color(self, hex_color: str) -> Tuple[Optional[str], float]:
        """Find the nearest approved color using RGB distance."""
        if not self.approved_colors:
            return None, float('inf')
        
        try:
            r1, g1, b1 = self._hex_to_rgb(hex_color)
        except ValueError:
            return None, float('inf')
        
        nearest = None
        min_distance = float('inf')
        
        for approved in self.approved_colors:
            try:
                r2, g2, b2 = self._hex_to_rgb(approved)
                distance = math.sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest = approved
            except ValueError:
                continue
        
        return nearest, min_distance
