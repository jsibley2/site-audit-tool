"""
================================================================================
ENGINE.PY - Core Crawler Engine
================================================================================
The heart of the unified audit tool. Handles URL discovery, normalization,
rate limiting, and orchestrates the crawling process.

This engine is designed to be plugin-agnostic - it discovers URLs and passes
them to whatever audit callback is provided.

Key Features:
- Automatic URL normalization (trailing slashes, fragments, query params)
- Domain restriction (stays within the target site)
- Rate limiting to avoid overwhelming servers
- Duplicate detection
- Error handling with graceful degradation

Author: Built with Claude in BoodleBox
Date: January 2026
================================================================================
"""

import time
import re
from urllib.parse import urlparse, urljoin, urlunparse
from collections import deque
from typing import Callable, List, Dict, Any, Set, Optional

import requests
from bs4 import BeautifulSoup


class AuditEngine:
    """
    Core crawler engine that discovers URLs and runs audit plugins against them.
    
    The engine handles all the "plumbing" of web crawling:
    - Finding links on pages
    - Normalizing URLs to avoid duplicates
    - Respecting rate limits
    - Staying within the target domain
    
    Plugins handle the actual audit logic (colors, SEO, content, etc.)
    """
    
    def __init__(
        self,
        base_url: str,
        max_pages: int = 50,
        excluded_patterns: Optional[List[str]] = None,
        rate_limit: float = 0.5,
        verbose: bool = False
    ):
        """
        Initialize the audit engine.
        
        Args:
            base_url: The starting URL for the crawl (e.g., "https://lastingchange.co")
            max_pages: Maximum number of pages to crawl (prevents runaway crawls)
            excluded_patterns: List of regex patterns for URLs to skip
            rate_limit: Seconds to wait between requests (be nice to servers!)
            verbose: If True, print detailed progress information
        """
        self.base_url = self._normalize_url(base_url)
        self.max_pages = max_pages
        self.excluded_patterns = excluded_patterns or []
        self.rate_limit = rate_limit
        self.verbose = verbose
        
        # Parse the base URL to extract the domain for restriction
        parsed = urlparse(self.base_url)
        self.allowed_domain = parsed.netloc
        self.scheme = parsed.scheme
        
        # Track visited URLs to avoid duplicates
        self.visited_urls: Set[str] = set()
        
        # Queue of URLs to visit (breadth-first crawling)
        self.url_queue: deque = deque()
        
        # Store results from all audited pages
        self.results: List[Dict[str, Any]] = []
        
        # Session for connection pooling (more efficient than individual requests)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "UnifiedAuditTool/1.0 (Web Design Audit; Contact: jonathan@lastingchange.co)"
        })
    
    def _normalize_url(self, url: str) -> str:
        """
        Normalize a URL to prevent duplicate crawling of the same page.
        
        Normalization rules:
        - Remove trailing slashes (except for root)
        - Remove URL fragments (#section)
        - Remove common tracking parameters
        - Lowercase the domain
        
        Args:
            url: The URL to normalize
            
        Returns:
            Normalized URL string
        """
        parsed = urlparse(url)
        
        # Lowercase the domain
        netloc = parsed.netloc.lower()
        
        # Remove fragment (e.g., #section-id)
        # Fragments don't change the page content, just scroll position
        fragment = ""
        
        # Clean up the path
        path = parsed.path
        
        # Remove trailing slash (except for root path "/")
        if path != "/" and path.endswith("/"):
            path = path.rstrip("/")
        
        # If path is empty, make it "/"
        if not path:
            path = "/"
        
        # Remove common tracking query parameters
        # These don't affect page content but create duplicate URLs
        query = parsed.query
        if query:
            # List of tracking params to remove
            tracking_params = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "fbclid", "gclid"]
            params = query.split("&")
            filtered_params = [p for p in params if not any(p.startswith(tp + "=") for tp in tracking_params)]
            query = "&".join(filtered_params)
        
        # Reconstruct the normalized URL
        normalized = urlunparse((
            parsed.scheme,
            netloc,
            path,
            parsed.params,
            query,
            fragment
        ))
        
        return normalized
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Check if a URL should be crawled.
        
        Validation rules:
        - Must be HTTP or HTTPS
        - Must be on the allowed domain
        - Must not match any excluded patterns
        - Must not be a file download (PDF, image, etc.)
        
        Args:
            url: The URL to validate
            
        Returns:
            True if the URL should be crawled, False otherwise
        """
        try:
            parsed = urlparse(url)
            
            # Must be HTTP or HTTPS
            if parsed.scheme not in ("http", "https"):
                return False
            
            # Must be on the allowed domain
            if parsed.netloc.lower() != self.allowed_domain:
                return False
            
            # Check excluded patterns
            for pattern in self.excluded_patterns:
                if re.search(pattern, url):
                    if self.verbose:
                        print(f"  [SKIP] Excluded by pattern: {url}")
                    return False
            
            # Skip common non-HTML resources
            # These won't have links to follow or styles to audit
            skip_extensions = [
                ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".avif",
                ".mp4", ".mp3", ".wav", ".zip", ".rar", ".exe", ".dmg",
                ".css", ".js", ".json", ".xml", ".txt", ".ico"
            ]
            path_lower = parsed.path.lower()
            for ext in skip_extensions:
                if path_lower.endswith(ext):
                    if self.verbose:
                        print(f"  [SKIP] Non-HTML resource: {url}")
                    return False
            
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"  [ERROR] URL validation failed for {url}: {e}")
            return False
    
    def _extract_links(self, html: str, current_url: str) -> List[str]:
        """
        Extract all links from an HTML page.
        
        Finds all <a href="..."> tags and converts relative URLs to absolute.
        
        Args:
            html: The HTML content of the page
            current_url: The URL of the current page (for resolving relative links)
            
        Returns:
            List of absolute URLs found on the page
        """
        links = []
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            # Find all anchor tags with href attributes
            for anchor in soup.find_all("a", href=True):
                href = anchor["href"]
                
                # Skip empty hrefs, javascript:, mailto:, tel:, etc.
                if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                    continue
                
                # Convert relative URLs to absolute
                absolute_url = urljoin(current_url, href)
                
                # Normalize the URL
                normalized_url = self._normalize_url(absolute_url)
                
                links.append(normalized_url)
                
        except Exception as e:
            if self.verbose:
                print(f"  [ERROR] Link extraction failed: {e}")
        
        return links
    
    def _fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch the HTML content of a page.
        
        Handles errors gracefully and respects rate limiting.
        
        Args:
            url: The URL to fetch
            
        Returns:
            HTML content as string, or None if fetch failed
        """
        try:
            response = self.session.get(url, timeout=30)
            
            # Check for successful response
            if response.status_code != 200:
                if self.verbose:
                    print(f"  [WARN] HTTP {response.status_code} for {url}")
                return None
            
            # Check content type - we only want HTML
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                if self.verbose:
                    print(f"  [SKIP] Non-HTML content type: {content_type}")
                return None
            
            return response.text
            
        except requests.exceptions.Timeout:
            if self.verbose:
                print(f"  [ERROR] Timeout fetching {url}")
            return None
            
        except requests.exceptions.RequestException as e:
            if self.verbose:
                print(f"  [ERROR] Request failed for {url}: {e}")
            return None
    
    def run(self, audit_callback: Callable[[str, str], Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run the crawler with the provided audit callback.
        
        This is the main entry point for running an audit. The engine will:
        1. Start at the base URL
        2. Fetch each page
        3. Call the audit_callback with the URL and HTML
        4. Extract links and add new URLs to the queue
        5. Continue until max_pages is reached or no more URLs
        
        Args:
            audit_callback: A function that takes (url, html) and returns audit results.
                           This is provided by the audit plugins (design, SEO, content).
                           
        Returns:
            List of audit results from all crawled pages
        """
        # Initialize the queue with the base URL
        self.url_queue.append(self.base_url)
        self.results = []
        pages_crawled = 0
        
        print(f"Starting crawl from: {self.base_url}")
        print(f"Max pages: {self.max_pages}")
        print("-" * 50)
        
        while self.url_queue and pages_crawled < self.max_pages:
            # Get the next URL from the queue
            current_url = self.url_queue.popleft()
            
            # Skip if already visited
            if current_url in self.visited_urls:
                continue
            
            # Mark as visited
            self.visited_urls.add(current_url)
            
            # Validate the URL
            if not self._is_valid_url(current_url):
                continue
            
            # Progress indicator
            pages_crawled += 1
            print(f"[{pages_crawled}/{self.max_pages}] Auditing: {current_url}")
            
            # Fetch the page
            html = self._fetch_page(current_url)
            
            if html is None:
                continue
            
            # Run the audit callback
            try:
                audit_result = audit_callback(current_url, html)
                
                # Add the URL to the result for reference
                if isinstance(audit_result, dict):
                    audit_result["url"] = current_url
                    self.results.append(audit_result)
                elif isinstance(audit_result, list):
                    # Some audits return multiple results per page
                    for result in audit_result:
                        result["url"] = current_url
                        self.results.append(result)
                        
            except Exception as e:
                print(f"  [ERROR] Audit callback failed: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()
            
            # Extract links for further crawling
            links = self._extract_links(html, current_url)
            
            # Add new links to the queue
            for link in links:
                if link not in self.visited_urls and link not in self.url_queue:
                    self.url_queue.append(link)
            
            # Rate limiting - be nice to the server
            if self.rate_limit > 0:
                time.sleep(self.rate_limit)
        
        print("-" * 50)
        print(f"Crawl complete. Pages audited: {pages_crawled}")
        print(f"Total results collected: {len(self.results)}")
        
        return self.results
    
    def get_all_urls(self) -> List[str]:
        """
        Get all URLs that were visited during the crawl.
        
        Useful for generating a sitemap or understanding site structure.
        
        Returns:
            List of all visited URLs
        """
        return list(self.visited_urls)
