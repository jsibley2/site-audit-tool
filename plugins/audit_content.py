"""
================================================================================
PLUGINS / AUDIT_CONTENT.PY - Content Extractor & Auditor
================================================================================
Extracts and audits page content for migration, analysis, or quality checks.

This plugin:
- Extracts all text content from semantic HTML elements
- Identifies heading structure and hierarchy
- Captures calls-to-action (buttons, links)
- Detects content patterns (bullet lists, quotes, etc.)
- Flags potential content issues (empty sections, placeholder text)

Useful for:
- Content migration between platforms
- Content inventory and auditing
- Identifying thin or missing content
- Extracting copy for review or translation

Output format uses "Expected vs Found" columns for clear accountability.

Uses Requests + BeautifulSoup (lightweight, fast).

Author: Built with Claude in BoodleBox
Date: January 2026
================================================================================
"""

import re
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup, NavigableString

# Import configuration
from config import (
    CONTENT_TAGS,
    CONTENT_IGNORE_TAGS,
    STATUS_MATCH,
    STATUS_MISMATCH,
    STATUS_MISSING,
)


class ContentAuditor:
    """
    Extracts and audits page content for quality and completeness.
    
    Designed for content migration, inventory, and quality assurance.
    """
    
    def __init__(self, min_paragraph_length: int = 50, detect_placeholder: bool = True):
        """
        Initialize the content auditor.
        
        Args:
            min_paragraph_length: Minimum characters for a paragraph to be considered "substantial"
            detect_placeholder: Whether to flag common placeholder text patterns
        """
        self.content_tags = CONTENT_TAGS
        self.ignore_tags = CONTENT_IGNORE_TAGS
        self.min_paragraph_length = min_paragraph_length
        self.detect_placeholder = detect_placeholder
        
        # Common placeholder text patterns to detect
        self.placeholder_patterns = [
            r"lorem ipsum",
            r"dolor sit amet",
            r"placeholder",
            r"coming soon",
            r"under construction",
            r"todo",
            r"tbd",
            r"insert .* here",
            r"your .* here",
            r"\[.*\]",  # [bracketed placeholders]
        ]
    
    def audit(self, url: str, html: str) -> List[Dict[str, Any]]:
        """
        Audit a page for content quality and extract text.
        
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
        
        # Remove ignored tags (scripts, styles, nav, etc.)
        for tag in soup.find_all(self.ignore_tags):
            tag.decompose()
        
        # =====================================================================
        # PHASE 1: Extract and catalog all headings
        # =====================================================================
        heading_results = self._extract_headings(soup)
        results.extend(heading_results)
        
        # =====================================================================
        # PHASE 2: Extract paragraph content
        # =====================================================================
        paragraph_results = self._extract_paragraphs(soup)
        results.extend(paragraph_results)
        
        # =====================================================================
        # PHASE 3: Extract list content
        # =====================================================================
        list_results = self._extract_lists(soup)
        results.extend(list_results)
        
        # =====================================================================
        # PHASE 4: Extract calls-to-action
        # =====================================================================
        cta_results = self._extract_ctas(soup)
        results.extend(cta_results)
        
        # =====================================================================
        # PHASE 5: Detect sections and their content
        # =====================================================================
        section_results = self._analyze_sections(soup)
        results.extend(section_results)
        
        # =====================================================================
        # PHASE 6: Check for placeholder content
        # =====================================================================
        if self.detect_placeholder:
            placeholder_results = self._detect_placeholders(soup)
            results.extend(placeholder_results)
        
        # =====================================================================
        # PHASE 7: Content statistics summary
        # =====================================================================
        stats_results = self._generate_stats(soup)
        results.extend(stats_results)
        
        return results
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract all headings and their hierarchy.
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of heading content results
        """
        results = []
        
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        
        for i, heading in enumerate(headings):
            text = heading.get_text(strip=True)
            level = heading.name
            
            # Get parent section/div class for context
            parent = heading.find_parent(["section", "div", "article"])
            parent_class = ""
            if parent and parent.get("class"):
                parent_class = " ".join(parent.get("class", []))
            
            results.append({
                "type": "content",
                "element": "heading",
                "property": f"{level} ({i+1})",
                "expected": "Meaningful heading text",
                "found": text[:100] + ("..." if len(text) > 100 else ""),
                "status": STATUS_MATCH if len(text) > 0 else STATUS_MISSING,
                "context": parent_class,
                "full_text": text,
            })
        
        return results
    
    def _extract_paragraphs(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract paragraph content and assess quality.
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of paragraph content results
        """
        results = []
        
        paragraphs = soup.find_all("p")
        
        substantial_count = 0
        thin_count = 0
        empty_count = 0
        
        for i, para in enumerate(paragraphs):
            text = para.get_text(strip=True)
            length = len(text)
            
            # Categorize paragraph
            if length == 0:
                empty_count += 1
                status = STATUS_MISSING
                category = "empty"
            elif length < self.min_paragraph_length:
                thin_count += 1
                status = "⚠️ Thin content"
                category = "thin"
            else:
                substantial_count += 1
                status = STATUS_MATCH
                category = "substantial"
            
            # Get parent context
            parent = para.find_parent(["section", "div", "article"])
            parent_class = ""
            if parent and parent.get("class"):
                parent_class = " ".join(parent.get("class", []))
            
            results.append({
                "type": "content",
                "element": "paragraph",
                "property": f"p ({i+1}) - {category}",
                "expected": f"≥{self.min_paragraph_length} characters",
                "found": f"{length} chars: '{text[:80]}{'...' if len(text) > 80 else ''}'",
                "status": status,
                "context": parent_class,
                "full_text": text,
            })
        
        # Summary
        results.append({
            "type": "content",
            "element": "paragraph",
            "property": "summary",
            "expected": "Mostly substantial paragraphs",
            "found": f"{substantial_count} substantial, {thin_count} thin, {empty_count} empty",
            "status": STATUS_MATCH if substantial_count > thin_count + empty_count else "⚠️ Review content",
            "context": "page-level",
        })
        
        return results
    
    def _extract_lists(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract list content (ul, ol).
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of list content results
        """
        results = []
        
        lists = soup.find_all(["ul", "ol"])
        
        for i, lst in enumerate(lists):
            list_type = "ordered" if lst.name == "ol" else "unordered"
            items = lst.find_all("li", recursive=False)
            item_count = len(items)
            
            # Extract item text
            item_texts = [li.get_text(strip=True) for li in items]
            preview = " | ".join(item_texts[:3])
            if len(item_texts) > 3:
                preview += f" | ... (+{len(item_texts) - 3} more)"
            
            # Get parent context
            parent = lst.find_parent(["section", "div", "article"])
            parent_class = ""
            if parent and parent.get("class"):
                parent_class = " ".join(parent.get("class", []))
            
            results.append({
                "type": "content",
                "element": "list",
                "property": f"{list_type} ({i+1})",
                "expected": "List with meaningful items",
                "found": f"{item_count} items: {preview[:100]}",
                "status": STATUS_MATCH if item_count > 0 else STATUS_MISSING,
                "context": parent_class,
                "full_text": "\n".join(item_texts),
            })
        
        return results
    
    def _extract_ctas(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract calls-to-action (buttons and prominent links).
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of CTA content results
        """
        results = []
        
        # Find buttons
        buttons = soup.find_all(["button", "a"], class_=lambda x: x and any(
            kw in str(x).lower() for kw in ["btn", "button", "cta", "action"]
        ))
        
        # Also find links with button-like text
        action_links = soup.find_all("a", string=lambda x: x and any(
            kw in x.lower() for kw in ["contact", "get started", "learn more", "find out", "sign up", "subscribe"]
        ))
        
        all_ctas = list(set(buttons + action_links))
        
        for i, cta in enumerate(all_ctas):
            text = cta.get_text(strip=True)
            href = cta.get("href", "N/A")
            tag = cta.name
            
            # Get parent context
            parent = cta.find_parent(["section", "div", "article"])
            parent_class = ""
            if parent and parent.get("class"):
                parent_class = " ".join(parent.get("class", []))
            
            results.append({
                "type": "content",
                "element": "cta",
                "property": f"{tag} ({i+1})",
                "expected": "Clear call-to-action text",
                "found": f"'{text}' → {href[:50]}{'...' if len(str(href)) > 50 else ''}",
                "status": STATUS_MATCH if text else STATUS_MISSING,
                "context": parent_class,
            })
        
        # Summary
        results.append({
            "type": "content",
            "element": "cta",
            "property": "count",
            "expected": "≥1 CTA per page",
            "found": f"{len(all_ctas)} CTAs found",
            "status": STATUS_MATCH if len(all_ctas) >= 1 else "⚠️ No CTAs detected",
            "context": "page-level",
        })
        
        return results
    
    def _analyze_sections(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Analyze content sections for completeness.
        
        Looks for common section patterns and checks if they have content.
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of section analysis results
        """
        results = []
        
        # Find semantic sections
        sections = soup.find_all(["section", "article", "main"])
        
        # Also find divs with section-like classes
        section_divs = soup.find_all("div", class_=lambda x: x and any(
            kw in str(x).lower() for kw in ["section", "block", "container", "wrapper", "hero", "footer", "header"]
        ))
        
        all_sections = list(set(sections + section_divs))
        
        for i, section in enumerate(all_sections):
            classes = " ".join(section.get("class", []))
            tag = section.name
            
            # Count content elements within section
            headings = len(section.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]))
            paragraphs = len(section.find_all("p"))
            lists = len(section.find_all(["ul", "ol"]))
            images = len(section.find_all("img"))
            
            # Get text content length
            text_content = section.get_text(strip=True)
            text_length = len(text_content)
            
            # Determine if section has substantial content
            has_content = headings > 0 or paragraphs > 0 or text_length > 100
            
            results.append({
                "type": "content",
                "element": "section",
                "property": f"{tag}.{classes[:30]}",
                "expected": "Section with content",
                "found": f"{headings}h, {paragraphs}p, {lists}lists, {images}img ({text_length} chars)",
                "status": STATUS_MATCH if has_content else "⚠️ Empty/thin section",
                "context": classes,
            })
        
        return results
    
    def _detect_placeholders(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Detect placeholder or dummy content.
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of placeholder detection results
        """
        results = []
        
        # Get all text content
        all_text = soup.get_text(separator=" ").lower()
        
        placeholders_found = []
        
        for pattern in self.placeholder_patterns:
            if re.search(pattern, all_text, re.IGNORECASE):
                placeholders_found.append(pattern)
        
        if placeholders_found:
            results.append({
                "type": "content",
                "element": "quality",
                "property": "placeholder-detection",
                "expected": "No placeholder content",
                "found": f"Detected patterns: {', '.join(placeholders_found[:5])}",
                "status": "❌ Placeholder content detected",
                "context": "page-level",
            })
        else:
            results.append({
                "type": "content",
                "element": "quality",
                "property": "placeholder-detection",
                "expected": "No placeholder content",
                "found": "No placeholder patterns detected",
                "status": STATUS_MATCH,
                "context": "page-level",
            })
        
        return results
    
    def _generate_stats(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Generate content statistics summary.
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of statistics results
        """
        results = []
        
        # Word count
        all_text = soup.get_text(separator=" ")
        words = len(all_text.split())
        
        results.append({
            "type": "content",
            "element": "statistics",
            "property": "word-count",
            "expected": "≥300 words for SEO",
            "found": f"{words} words",
            "status": STATUS_MATCH if words >= 300 else "⚠️ Thin content for SEO",
            "context": "page-level",
        })
        
        # Character count
        chars = len(all_text)
        
        results.append({
            "type": "content",
            "element": "statistics",
            "property": "character-count",
            "expected": "N/A (informational)",
            "found": f"{chars:,} characters",
            "status": STATUS_MATCH,
            "context": "page-level",
        })
        
        # Reading time estimate (average 200 words per minute)
        reading_time = max(1, round(words / 200))
        
        results.append({
            "type": "content",
            "element": "statistics",
            "property": "reading-time",
            "expected": "N/A (informational)",
            "found": f"~{reading_time} minute{'s' if reading_time > 1 else ''} read",
            "status": STATUS_MATCH,
            "context": "page-level",
        })
        
        # Image count
        images = len(soup.find_all("img"))
        
        results.append({
            "type": "content",
            "element": "statistics",
            "property": "image-count",
            "expected": "≥1 image per page",
            "found": f"{images} images",
            "status": STATUS_MATCH if images >= 1 else "⚠️ No images",
            "context": "page-level",
        })
        
        # Link count (internal vs external)
        all_links = soup.find_all("a", href=True)
        internal_links = [l for l in all_links if l["href"].startswith("/") or l["href"].startswith("#")]
        external_links = [l for l in all_links if l["href"].startswith("http")]
        
        results.append({
            "type": "content",
            "element": "statistics",
            "property": "link-count",
            "expected": "N/A (informational)",
            "found": f"{len(internal_links)} internal, {len(external_links)} external",
            "status": STATUS_MATCH,
            "context": "page-level",
        })
        
        return results
