import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

class AdvancedWebSearch:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }

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
        
    def scrape_main_content(self, url, max_length=2000):
        """
        Scrape the main content from a webpage and return it truncated to max_length.
        
        Args:
            url (str): The URL of the webpage to scrape
            max_length (int, optional): Maximum length of the returned content. Defaults to 1000.
        
        Returns:
            str: Extracted main content, cleaned and truncated
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status() 
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            main_content = soup.find(['main', 'article', 'div#content', 'div.content'])
            
            if not main_content:
                main_content = soup.body
            
            text = main_content.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text[:max_length]
        
        except requests.RequestException as e:
            return f"Error fetching webpage: {str(e)}"
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def search(self, query, num_results = 5):
        """
        Perform a web search and return high-quality results
        """

        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        
        try:
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            result_containers = soup.find_all('div', class_=re.compile(r'(yuRUbf|g)'))
            
            results = []
            
            for container in result_containers:
                if self._is_sponsored_link(container):
                    continue
                
                title_elem = container.find(['h3', 'h2'])
                link_elem = container.find('a')
                
                desc_elem = container.find_next_sibling('div')
                if not desc_elem:
                    desc_elem = container.find_next('div', class_=re.compile(r'VwiC3b'))
                
                if not (title_elem and link_elem):
                    continue
                
                title = title_elem.get_text(strip=True)
                link = link_elem.get('href', '')
                description = desc_elem.get_text(strip=True) if desc_elem else ''
                
                if title and link:
                    results.append({
                        'title': title,
                        'link': link,
                        'description': description
                    })
                
                if len(results) >= num_results:
                    break
            
            return results
        
        except requests.RequestException as e:
            print(f"Search request failed: {e}")
            return []

if __name__ == "__main__":
    searcher = AdvancedWebSearch()
    results = searcher.search("python web scraping")
    
    for result in results:
        print(f"Title: {result['title']}")
        print(f"Link: {result['link']}")
        print(f"Description: {result['description']}")
        print("---")