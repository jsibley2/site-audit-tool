"""
================================================================================
CONFIG.PY - Shared Configuration & Constants
================================================================================
Central configuration file for the unified audit tool. All settings, constants,
and shared values live here to ensure consistency across all modules.

Modify these values to customize the tool's behavior without touching
the core logic in other files.

Author: Built with Claude in BoodleBox
Date: January 2026
================================================================================
"""

# =============================================================================
# CRAWLER SETTINGS
# =============================================================================

# Maximum number of pages to crawl by default
# This prevents runaway crawls on large sites
# Override with --max-pages CLI argument
DEFAULT_MAX_PAGES = 50

# Seconds to wait between requests
# Be respectful to servers - don't hammer them
DEFAULT_RATE_LIMIT = 0.5

# Request timeout in seconds
REQUEST_TIMEOUT = 30

# =============================================================================
# URL EXCLUSION PATTERNS
# =============================================================================
# Regex patterns for URLs to skip during crawling
# Add patterns here to exclude specific paths, file types, or URL structures

EXCLUDED_PATTERNS = [
    # Admin and system paths
    r"/admin",
    r"/wp-admin",
    r"/wp-login",
    r"/login",
    r"/logout",
    r"/cart",
    r"/checkout",
    
    # Webflow-specific paths to skip
    r"/editor",
    r"\.webflow\.io/editor",
    
    # Pagination that might create infinite loops
    r"\?page=\d+$",
    r"/page/\d+",
    
    # Search results (dynamic content)
    r"\?s=",
    r"/search",
    
    # Calendar/date archives (can be infinite)
    r"/\d{4}/\d{2}/\d{2}",  # /2024/01/15 style dates
    
    # Common CMS paths
    r"/tag/",
    r"/category/",
    r"/author/",
    
    # API endpoints
    r"/api/",
    r"/graphql",
    r"\.json$",
    r"\.xml$",
]

# =============================================================================
# COLOR ANALYSIS SETTINGS
# =============================================================================

# How close (in RGB distance) a color must be to be considered a "near-miss"
# RGB distance is calculated as: sqrt((r1-r2)² + (g1-g2)² + (b1-b2)²)
# A value of 10 catches colors like #003153 vs #003155 (typos/eyeballing)
COLOR_NEAR_MISS_THRESHOLD = 10

# CSS properties to check for color values
COLOR_PROPERTIES = [
    "color",
    "background-color",
    "background",
    "border-color",
    "border-top-color",
    "border-right-color",
    "border-bottom-color",
    "border-left-color",
    "outline-color",
    "box-shadow",
    "text-shadow",
    "fill",
    "stroke",
]

# =============================================================================
# TEXTURE ANALYSIS SETTINGS
# =============================================================================

# CSS properties to check for texture/background-image values
TEXTURE_PROPERTIES = [
    "background-image",
    "background",
]

# Properties related to texture rendering
TEXTURE_BLEND_PROPERTIES = [
    "mix-blend-mode",
    "background-blend-mode",
]

# =============================================================================
# SEO ANALYSIS SETTINGS
# =============================================================================

# Meta tags to check during SEO audits
SEO_META_TAGS = [
    "title",
    "description",
    "keywords",
    "robots",
    "canonical",
    "og:title",
    "og:description",
    "og:image",
    "og:url",
    "og:type",
    "twitter:card",
    "twitter:title",
    "twitter:description",
    "twitter:image",
]

# Recommended character limits for SEO elements
SEO_LIMITS = {
    "title": {"min": 30, "max": 60},
    "description": {"min": 120, "max": 160},
    "og:title": {"min": 30, "max": 60},
    "og:description": {"min": 120, "max": 200},
}

# =============================================================================
# CONTENT ANALYSIS SETTINGS
# =============================================================================

# HTML tags to extract text content from
CONTENT_TAGS = [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p",
    "li",
    "blockquote",
    "figcaption",
]

# Tags to ignore when extracting content
CONTENT_IGNORE_TAGS = [
    "script",
    "style",
    "nav",
    "footer",
    "header",
    "aside",
    "noscript",
]

# =============================================================================
# OUTPUT SETTINGS
# =============================================================================

# CSV export settings
CSV_ENCODING = "utf-8"
CSV_DELIMITER = ","

# Status labels for audit results
STATUS_MATCH = "✅ Match"
STATUS_NEAR_MISS = "⚠️ Near-miss"
STATUS_MISMATCH = "❌ Mismatch"
STATUS_MISSING = "❌ Missing"
STATUS_ROGUE = "❌ Rogue (not in palette)"
STATUS_IN_RANGE = "✅ In range"
STATUS_OUT_OF_RANGE = "❌ Out of range"

# =============================================================================
# USER AGENT
# =============================================================================

# Identify the crawler politely
# Include contact info so site owners can reach out if needed
USER_AGENT = "UnifiedAuditTool/1.0 (Web Design Audit; https://github.com/your-repo)"
