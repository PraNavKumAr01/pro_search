from .search import AdvancedWebSearch
from .agents import GroqClient
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

class ProSearch:
    def __init__(self, api_key):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError(
                "API key not found. Please provide it as an argument or set it in the environment variable 'GROQ_API_KEY'."
            )
        
        self.query = None
        self.searcher = AdvancedWebSearch()
        self.agent = GroqClient(api_key = api_key)
        self.search_query = None
        self.search_content = []
        self.search_links = []
        self.search_results = []
        self.content = []
        self.context = None

    def process_search_results(self):
        print("Generating Content Summaries...")
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(self.agent.generate_content_summary, self.query, result) 
                for result in self.search_results
            ]
            self.content = []
            for future in as_completed(futures):
                try:
                    content = future.result()
                    if content is not None:
                        self.content.append(content)
                except Exception as e:
                    print(f"Error processing future: {e}")

    def run(self, query, num_results = 5, num_retries = 5):
        self.query = query
        print("Generating Search Query...")
        self.search_query = self.agent.generate_search_query(query)
        print(f"Browsing for Query {self.search_query}...")
        self.search_content = self.searcher.search(self.search_query, num_results)
        self.search_links = [content['link'] for content in self.search_content]

        if len(self.search_links) < num_results:
            for _ in range(num_retries):
                print(f"Retrying search {_ + 1}/{num_results}")
                if len(self.search_links) < num_results:
                    self.search_content = self.searcher.search(self.search_query, num_results)
                    self.search_links = [content['link'] for content in self.search_content]
                else:
                    break

        print(self.search_links)
        print(f"Scraping content from {len(self.search_links)} sources...")
        self.search_results = self.searcher.batch_scrape(self.search_links)
        self.process_search_results()
        print("Generating Final Context...")
        self.context = self.agent.generate_context(self.query, self.content)

        return self.context