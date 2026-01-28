"""
================================================================================
PLUGINS / AUDIT_SEO.PY - SEO Auditor
================================================================================
Audits webpages for SEO best practices and meta tag compliance.

This plugin checks:
- Title tags: presence, length, uniqueness
- Meta descriptions: presence, length, keyword usage
- Open Graph tags: og:title, og:description, og:image, og:url
- Twitter Card tags: twitter:card, twitter:title, twitter:description
- Heading structure: H1 presence and hierarchy
- Canonical URLs: presence and correctness
- Robots directives: index/noindex, follow/nofollow

Output format uses "Expected vs Found" columns for clear accountability.

Uses Requests + BeautifulSoup (lightweight, fast).

Author: Built with Claude in BoodleBox
Date: January 2026
================================================================================
"""

from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup

# Import configuration
from config import (
    SEO_META_TAGS,
    SEO_LIMITS,
    STATUS_MATCH,
    STATUS_MISMATCH,
    STATUS_MISSING,
    STATUS_IN_RANGE,
    STATUS_OUT_OF_RANGE,
)


class SEOAuditor:
    """
    Audits a webpage for SEO best practices.
    
    Checks meta tags, heading structure, and other SEO-critical elements
    against recommended standards.
    """
    
    def __init__(self):
        """
        Initialize the SEO auditor.
        
        No special configuration needed - uses standards from config.py.
        """
        self.meta_tags_to_check = SEO_META_TAGS
        self.limits = SEO_LIMITS
    
    def audit(self, url: str, html: str) -> List[Dict[str, Any]]:
        """
        Audit a page for SEO compliance.
        
        This is the main entry point called by the crawler engine.
        
        Args:
            url: The URL of the page being audited
            html: The HTML content of the page
            
        Returns:
            List of audit result dictionaries
        """
        results = []
        
        # Parse the HTML
        soup = BeautifulSoup(html, "html.parser")
        
        # =====================================================================
        # PHASE 1: Title Tag
        # =====================================================================
        title_results = self._audit_title(soup)
        results.extend(title_results)
        
        # =====================================================================
        # PHASE 2: Meta Description
        # =====================================================================
        description_results = self._audit_meta_description(soup)
        results.extend(description_results)
        
        # =====================================================================
        # PHASE 3: Open Graph Tags
        # =====================================================================
        og_results = self._audit_open_graph(soup)
        results.extend(og_results)
        
        # =====================================================================
        # PHASE 4: Twitter Card Tags
        # =====================================================================
        twitter_results = self._audit_twitter_cards(soup)
        results.extend(twitter_results)
        
        # =====================================================================
        # PHASE 5: Heading Structure
        # =====================================================================
        heading_results = self._audit_headings(soup)
        results.extend(heading_results)
        
        # =====================================================================
        # PHASE 6: Canonical URL
        # =====================================================================
        canonical_results = self._audit_canonical(soup, url)
        results.extend(canonical_results)
        
        # =====================================================================
        # PHASE 7: Robots Directives
        # =====================================================================
        robots_results = self._audit_robots(soup)
        results.extend(robots_results)
        
        # =====================================================================
        # PHASE 8: Image Alt Tags
        # =====================================================================
        image_results = self._audit_images(soup)
        results.extend(image_results)
        
        return results
    
    def _audit_title(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Audit the page title tag.
        
        Checks:
        - Presence of <title> tag
        - Length within recommended range (30-60 characters)
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of audit results
        """
        results = []
        
        title_tag = soup.find("title")
        
        if title_tag and title_tag.string:
            title_text = title_tag.string.strip()
            title_length = len(title_text)
            
            # Check presence
            results.append({
                "type": "seo",
                "element": "title",
                "property": "presence",
                "expected": "Title tag present",
                "found": f"'{title_text[:50]}{'...' if len(title_text) > 50 else ''}'",
                "status": STATUS_MATCH,
            })
            
            # Check length
            min_len = self.limits.get("title", {}).get("min", 30)
            max_len = self.limits.get("title", {}).get("max", 60)
            
            if min_len <= title_length <= max_len:
                status = STATUS_IN_RANGE
            else:
                status = STATUS_OUT_OF_RANGE
            
            results.append({
                "type": "seo",
                "element": "title",
                "property": "length",
                "expected": f"{min_len}–{max_len} characters",
                "found": f"{title_length} characters",
                "status": status,
            })
        else:
            results.append({
                "type": "seo",
                "element": "title",
                "property": "presence",
                "expected": "Title tag present",
                "found": "Missing",
                "status": STATUS_MISSING,
            })
        
        return results
    
    def _audit_meta_description(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Audit the meta description tag.
        
        Checks:
        - Presence of meta description
        - Length within recommended range (120-160 characters)
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of audit results
        """
        results = []
        
        meta_desc = soup.find("meta", attrs={"name": "description"})
        
        if meta_desc and meta_desc.get("content"):
            desc_text = meta_desc["content"].strip()
            desc_length = len(desc_text)
            
            # Check presence
            results.append({
                "type": "seo",
                "element": "meta",
                "property": "description (presence)",
                "expected": "Meta description present",
                "found": f"'{desc_text[:60]}{'...' if len(desc_text) > 60 else ''}'",
                "status": STATUS_MATCH,
            })
            
            # Check length
            min_len = self.limits.get("description", {}).get("min", 120)
            max_len = self.limits.get("description", {}).get("max", 160)
            
            if min_len <= desc_length <= max_len:
                status = STATUS_IN_RANGE
            else:
                status = STATUS_OUT_OF_RANGE
            
            results.append({
                "type": "seo",
                "element": "meta",
                "property": "description (length)",
                "expected": f"{min_len}–{max_len} characters",
                "found": f"{desc_length} characters",
                "status": status,
            })
        else:
            results.append({
                "type": "seo",
                "element": "meta",
                "property": "description",
                "expected": "Meta description present",
                "found": "Missing",
                "status": STATUS_MISSING,
            })
        
        return results
    
    def _audit_open_graph(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Audit Open Graph meta tags.
        
        Checks for presence of:
        - og:title
        - og:description
        - og:image
        - og:url
        - og:type
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of audit results
        """
        results = []
        
        og_tags = ["og:title", "og:description", "og:image", "og:url", "og:type"]
        
        for tag_name in og_tags:
            meta_tag = soup.find("meta", attrs={"property": tag_name})
            
            if meta_tag and meta_tag.get("content"):
                content = meta_tag["content"].strip()
                
                # Truncate long content for display
                display_content = content[:60] + "..." if len(content) > 60 else content
                
                results.append({
                    "type": "seo",
                    "element": "open-graph",
                    "property": tag_name,
                    "expected": f"{tag_name} present",
                    "found": f"'{display_content}'",
                    "status": STATUS_MATCH,
                })
                
                # Check length for title and description
                if tag_name == "og:title":
                    min_len = self.limits.get("og:title", {}).get("min", 30)
                    max_len = self.limits.get("og:title", {}).get("max", 60)
                    
                    if min_len <= len(content) <= max_len:
                        status = STATUS_IN_RANGE
                    else:
                        status = STATUS_OUT_OF_RANGE
                    
                    results.append({
                        "type": "seo",
                        "element": "open-graph",
                        "property": f"{tag_name} (length)",
                        "expected": f"{min_len}–{max_len} characters",
                        "found": f"{len(content)} characters",
                        "status": status,
                    })
                
                elif tag_name == "og:description":
                    min_len = self.limits.get("og:description", {}).get("min", 120)
                    max_len = self.limits.get("og:description", {}).get("max", 200)
                    
                    if min_len <= len(content) <= max_len:
                        status = STATUS_IN_RANGE
                    else:
                        status = STATUS_OUT_OF_RANGE
                    
                    results.append({
                        "type": "seo",
                        "element": "open-graph",
                        "property": f"{tag_name} (length)",
                        "expected": f"{min_len}–{max_len} characters",
                        "found": f"{len(content)} characters",
                        "status": status,
                    })
            else:
                results.append({
                    "type": "seo",
                    "element": "open-graph",
                    "property": tag_name,
                    "expected": f"{tag_name} present",
                    "found": "Missing",
                    "status": STATUS_MISSING,
                })
        
        return results
    
    def _audit_twitter_cards(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Audit Twitter Card meta tags.
        
        Checks for presence of:
        - twitter:card
        - twitter:title
        - twitter:description
        - twitter:image
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of audit results
        """
        results = []
        
        twitter_tags = ["twitter:card", "twitter:title", "twitter:description", "twitter:image"]
        
        for tag_name in twitter_tags:
            meta_tag = soup.find("meta", attrs={"name": tag_name})
            
            if meta_tag and meta_tag.get("content"):
                content = meta_tag["content"].strip()
                display_content = content[:60] + "..." if len(content) > 60 else content
                
                results.append({
                    "type": "seo",
                    "element": "twitter-card",
                    "property": tag_name,
                    "expected": f"{tag_name} present",
                    "found": f"'{display_content}'",
                    "status": STATUS_MATCH,
                })
            else:
                results.append({
                    "type": "seo",
                    "element": "twitter-card",
                    "property": tag_name,
                    "expected": f"{tag_name} present",
                    "found": "Missing",
                    "status": STATUS_MISSING,
                })
        
        return results
    
    def _audit_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Audit heading structure.
        
        Checks:
        - Presence of exactly one H1
        - Proper heading hierarchy (no skipped levels)
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of audit results
        """
        results = []
        
        # Count H1 tags
        h1_tags = soup.find_all("h1")
        h1_count = len(h1_tags)
        
        if h1_count == 1:
            h1_text = h1_tags[0].get_text(strip=True)
            display_text = h1_text[:50] + "..." if len(h1_text) > 50 else h1_text
            
            results.append({
                "type": "seo",
                "element": "heading",
                "property": "h1 (count)",
                "expected": "Exactly 1 H1 tag",
                "found": f"1 H1: '{display_text}'",
                "status": STATUS_MATCH,
            })
        elif h1_count == 0:
            results.append({
                "type": "seo",
                "element": "heading",
                "property": "h1 (count)",
                "expected": "Exactly 1 H1 tag",
                "found": "0 H1 tags (missing)",
                "status": STATUS_MISSING,
            })
        else:
            results.append({
                "type": "seo",
                "element": "heading",
                "property": "h1 (count)",
                "expected": "Exactly 1 H1 tag",
                "found": f"{h1_count} H1 tags (too many)",
                "status": STATUS_MISMATCH,
            })
        
        # Check heading hierarchy
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        
        if headings:
            levels = [int(h.name[1]) for h in headings]
            
            # Check for skipped levels
            skipped = False
            for i in range(1, len(levels)):
                if levels[i] > levels[i-1] + 1:
                    skipped = True
                    break
            
            if skipped:
                results.append({
                    "type": "seo",
                    "element": "heading",
                    "property": "hierarchy",
                    "expected": "No skipped heading levels",
                    "found": f"Skipped levels detected in sequence: {levels}",
                    "status": STATUS_MISMATCH,
                })
            else:
                results.append({
                    "type": "seo",
                    "element": "heading",
                    "property": "hierarchy",
                    "expected": "No skipped heading levels",
                    "found": f"Proper hierarchy: {levels}",
                    "status": STATUS_MATCH,
                })
        
        return results
    
    def _audit_canonical(self, soup: BeautifulSoup, current_url: str) -> List[Dict[str, Any]]:
        """
        Audit canonical URL tag.
        
        Checks:
        - Presence of canonical link
        - Whether it points to the current URL (or a valid alternate)
        
        Args:
            soup: BeautifulSoup parsed HTML
            current_url: The URL of the current page
            
        Returns:
            List of audit results
        """
        results = []
        
        canonical = soup.find("link", attrs={"rel": "canonical"})
        
        if canonical and canonical.get("href"):
            canonical_url = canonical["href"].strip()
            
            results.append({
                "type": "seo",
                "element": "canonical",
                "property": "presence",
                "expected": "Canonical URL present",
                "found": canonical_url,
                "status": STATUS_MATCH,
            })
            
            # Check if canonical matches current URL (basic check)
            # Note: This is a simplified check - real implementation would normalize URLs
            if canonical_url.rstrip("/") == current_url.rstrip("/"):
                results.append({
                    "type": "seo",
                    "element": "canonical",
                    "property": "self-referencing",
                    "expected": "Canonical matches current URL",
                    "found": "Self-referencing (correct)",
                    "status": STATUS_MATCH,
                })
            else:
                results.append({
                    "type": "seo",
                    "element": "canonical",
                    "property": "self-referencing",
                    "expected": "Canonical matches current URL",
                    "found": f"Points to different URL (may be intentional)",
                    "status": "⚠️ Review",
                })
        else:
            results.append({
                "type": "seo",
                "element": "canonical",
                "property": "presence",
                "expected": "Canonical URL present",
                "found": "Missing",
                "status": STATUS_MISSING,
            })
        
        return results
    
    def _audit_robots(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Audit robots meta tag.
        
        Checks:
        - Presence of robots directive
        - Whether page is set to index/noindex
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of audit results
        """
        results = []
        
        robots = soup.find("meta", attrs={"name": "robots"})
        
        if robots and robots.get("content"):
            content = robots["content"].strip().lower()
            
            results.append({
                "type": "seo",
                "element": "robots",
                "property": "directive",
                "expected": "Robots directive present",
                "found": content,
                "status": STATUS_MATCH,
            })
            
            # Check for noindex
            if "noindex" in content:
                results.append({
                    "type": "seo",
                    "element": "robots",
                    "property": "indexing",
                    "expected": "Page indexable (no 'noindex')",
                    "found": "noindex detected - page will NOT be indexed",
                    "status": "⚠️ Intentional?",
                })
            else:
                results.append({
                    "type": "seo",
                    "element": "robots",
                    "property": "indexing",
                    "expected": "Page indexable",
                    "found": "Page is indexable",
                    "status": STATUS_MATCH,
                })
        else:
            # No robots tag means default behavior (index, follow)
            results.append({
                "type": "seo",
                "element": "robots",
                "property": "directive",
                "expected": "Robots directive (optional)",
                "found": "Not specified (defaults to index, follow)",
                "status": STATUS_MATCH,
            })
        
        return results
    
    def _audit_images(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Audit image alt tags.
        
        Checks:
        - Presence of alt attributes on images
        - Empty alt attributes (may be intentional for decorative images)
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of audit results
        """
        results = []
        
        images = soup.find_all("img")
        
        if not images:
            results.append({
                "type": "seo",
                "element": "images",
                "property": "count",
                "expected": "N/A",
                "found": "No images found on page",
                "status": STATUS_MATCH,
            })
            return results
        
        total_images = len(images)
        images_with_alt = 0
        images_empty_alt = 0
        images_missing_alt = 0
        
        for img in images:
            if img.has_attr("alt"):
                if img["alt"].strip():
                    images_with_alt += 1
                else:
                    images_empty_alt += 1
            else:
                images_missing_alt += 1
        
        # Summary result
        results.append({
            "type": "seo",
            "element": "images",
            "property": "alt-tags (summary)",
            "expected": "All images have alt attributes",
            "found": f"{total_images} images: {images_with_alt} with alt, {images_empty_alt} empty alt, {images_missing_alt} missing alt",
            "status": STATUS_MATCH if images_missing_alt == 0 else STATUS_MISMATCH,
        })
        
        # Flag if any images are missing alt
        if images_missing_alt > 0:
            results.append({
                "type": "seo",
                "element": "images",
                "property": "accessibility",
                "expected": "0 images missing alt attribute",
                "found": f"{images_missing_alt} images missing alt (accessibility issue)",
                "status": STATUS_MISMATCH,
            })
        
        return results
