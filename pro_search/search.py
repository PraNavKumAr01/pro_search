import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import os
import random
import time
import sqlite3
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from readability import Document

class AdvancedWebSearch:
    def __init__(self, 
                 proxies: Optional[List[str]] = None, 
                 cache_db_path: str = 'web_search_cache.db',
                 rate_limit: int = 0):
        """
        Initialize advanced web search with enhanced capabilities
        
        Args:
            proxies (list, optional): List of proxy servers to rotate
            cache_db_path (str): Path to SQLite cache database
            rate_limit (int): Minimum seconds between requests
        """
        self.headers = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            },
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.95 Safari/537.11',
                'Accept-Language': 'en-US,en;q=0.5',
            }
        ]
        
        self.proxies = proxies or []
        self.rate_limit = rate_limit
        
        # Setup cache database
        cache_db_path = str(os.getcwd() + cache_db_path)
        self._setup_cache_database(cache_db_path)
        
    def _setup_cache_database(self, db_path: str):
        """
        Create SQLite database for caching search results and web content
        """
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Create tables for caching
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_cache (
                query TEXT PRIMARY KEY,
                results TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_cache (
                url TEXT PRIMARY KEY,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def _get_cached_search_results(self, query: str, max_age_hours: int = 24) -> Optional[List[Dict]]:
        """
        Retrieve cached search results if they exist and are not too old
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT results FROM search_cache 
            WHERE query = ? AND 
            timestamp > datetime('now', ?)
        ''', (query, f'-{max_age_hours} hours'))
        
        result = cursor.fetchone()
        return eval(result[0]) if result else None
    
    def _cache_search_results(self, query: str, results: List[Dict]):
        """
        Cache search results in SQLite database
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO search_cache (query, results) 
            VALUES (?, ?)
        ''', (query, str(results)))
        self.conn.commit()
    
    def _select_proxy(self) -> Optional[Dict]:
        """
        Select a random proxy from the list
        """
        if not self.proxies:
            return None
        
        return {
            'http': random.choice(self.proxies),
            'https': random.choice(self.proxies)
        }
    
    def _wait_rate_limit(self):
        """
        Enforce rate limiting between requests
        """
        time.sleep(self.rate_limit)

    def _is_sponsored_link(self, container):
        """
        Detect sponsored links using specific Google HTML structure
        """
        try:
            taw_div = container.find_parents('div', class_='taw')
            if taw_div:
                tvcap_div = container.find_parents('div', class_='tvcap')
                if tvcap_div:
                    ggjvb_div = container.find_parents('div', class_='gGXjvb')
                    if ggjvb_div:
                        ads_header = container.find('h1', string='Ads')
                        if ads_header:
                            return True
            
            sponsored_indicators = [
                'ad', 'sponsored', 'advertisment', 'promoted'
            ]
            return any(
                indicator in str(container.get('class', '')).lower() or
                indicator in container.get_text(strip=True).lower()
                for indicator in sponsored_indicators
            )
        except Exception:
            return False

    def scrape_main_content(self, url: str, max_length: int = 2000) -> str:
        """
        Enhanced webpage content scraping with multiple strategies
        
        Args:
            url (str): The URL of the webpage to scrape
            max_length (int, optional): Maximum length of the returned content
            use_fallback (bool): Whether to use Selenium if initial scraping fails
        
        Returns:
            str: Extracted main content, cleaned and truncated
        """
        def clean_text(text: str) -> str:
            """Internal helper to clean extracted text"""
            # Remove extra whitespaces
            text = re.sub(r'\s+', ' ', text).strip()
            # Remove non-printable characters
            text = re.sub(r'[^\x20-\x7E\n]+', '', text)
            return text[:max_length]

        try:
            # Select random headers and proxies
            headers = random.choice(self.headers)
            proxies = self._select_proxy()

            # Attempt to get cached content first
            cursor = self.conn.cursor()
            cursor.execute('SELECT content FROM content_cache WHERE url = ?', (url,))
            cached_content = cursor.fetchone()
            if cached_content:
                return clean_text(cached_content[0])

            # Standard requests-based scraping
            response = requests.get(
                url, 
                headers=headers, 
                proxies=proxies,
                timeout=10
            )
            response.raise_for_status()

            # Use readability library for better content extraction
            doc = Document(response.text)
            text = doc.summary()
            soup = BeautifulSoup(text, 'html.parser')
            
            # Remove unnecessary tags
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                tag.decompose()

            # Extract text
            main_text = soup.get_text(separator=' ', strip=True)
            cleaned_text = clean_text(main_text)

            # Cache the content
            cursor.execute(
                'INSERT OR REPLACE INTO content_cache (url, content) VALUES (?, ?)', 
                (url, cleaned_text)
            )
            self.conn.commit()

            return cleaned_text

        except Exception as e:
            return f"Scraping failed. Errors: {str(e)}"
    
    def search(self, query: str, num_results: int = 5, use_cache: bool = True) -> List[Dict]:
        """
        Enhanced search method with caching, proxy support, and robustness
        """
        # Check cache first
        if use_cache:
            cached_results = self._get_cached_search_results(query)
            if cached_results:
                return cached_results
        
        try:
            # Rotate headers and proxies
            headers = random.choice(self.headers)
            proxies = self._select_proxy()
            
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            # Rate limiting
            self._wait_rate_limit()
            
            response = requests.get(
                search_url, 
                headers=headers, 
                proxies=proxies,
                timeout=10
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            result_containers = soup.find_all('div', class_=re.compile(r'(yuRUbf|g)'))
            
            results = []
            for container in result_containers:
                # Skip sponsored links
                if self._is_sponsored_link(container):
                    continue
                
                # Extract link details
                title_elem = container.find(['h3', 'h2'])
                link_elem = container.find('a')
                
                if not (title_elem and link_elem):
                    continue
                
                title = title_elem.get_text(strip=True)
                link = link_elem.get('href', '')

                pattern = r"https://.*?\.html|https://.*?(?=&ved)"
                match = re.search(pattern, link)
                if match:
                    link = match.group()

                # Find description
                desc_elem = container.find_next_sibling('div')
                if not desc_elem:
                    desc_elem = container.find_next('div', class_=re.compile(r'VwiC3b'))
                
                description = desc_elem.get_text(strip=True) if desc_elem else ''
                
                if title and link:
                    results.append({
                        'title': title,
                        'link': link,
                        'description': description
                    })
                
                if len(results) >= num_results:
                    break
            
            # Cache results
            if use_cache:
                self._cache_search_results(query, results)
            
            return results
            
        except Exception as e:
            print(f"Search attempt failed: {e}")
        
        return []
    
    def batch_scrape(self, urls: List[str], max_workers: int = 5) -> Dict[str, str]:
        """
        Batch scrape multiple URLs concurrently
        
        Args:
            urls (list): List of URLs to scrape
            max_workers (int): Maximum concurrent threads
        
        Returns:
            list: list of scraped content
        """
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(self.scrape_main_content, url): url 
                for url in urls
            }
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    content = future.result()
                    results.append(content)
                except Exception as e:
                    print(f"Scraping error: {str(e)}")
        
        return results
    
    def __del__(self):
        """
        Clean up resources
        """
        if hasattr(self, 'conn'):
            self.conn.close()