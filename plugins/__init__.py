"""
Audit plugins for the Unified Audit Tool.

Each plugin handles a specific type of audit:
    - DesignAuditor: Colors, textures, blend modes, opacity
    - SEOAuditor: Meta tags, headings, Open Graph, Twitter Cards
    - ContentAuditor: Text extraction, word counts, placeholder detection
"""

try:
    from plugins.audit_design import DesignAuditor
except ImportError:
    DesignAuditor = None

try:
    from plugins.audit_seo import SEOAuditor
except ImportError:
    SEOAuditor = None

try:
    from plugins.audit_content import ContentAuditor
except ImportError:
    ContentAuditor = None

__all__ = [
    "DesignAuditor",
    "SEOAuditor",
    "ContentAuditor",
]

__version__ = "1.0.0"
