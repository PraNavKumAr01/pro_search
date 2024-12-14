from .search import AdvancedWebSearch
from .agents import GroqClient

class ProSearch:
    def __init__(self, api_key):
        self.query = None
        self.searcher = AdvancedWebSearch()
        self.agent = GroqClient(api_key = api_key)
        self.search_query = None
        self.search_links = []
        self.search_results = []
        self.content = []
        self.context = None

    def run(self, query, num_results = 5, num_retries = 5):
        self.query = query
        print("Generating Search Query...")
        self.search_query = self.agent.generate_search_query(query)
        print(f"Browsing for Query {self.search_query}...")
        self.search_links = self.searcher.search(self.search_query, num_results)
        for _ in range(num_retries):
            print(f"Retrying search {_ + 1}/{num_results}")
            if len(self.search_links) < num_results:
                self.search_links = self.searcher.search(self.search_query, num_results)
            else:
                break
        print(f"Scraping content from {len(self.search_links)} sources...")
        for link in self.search_links:
            search_result = self.searcher.scrape_main_content(link)
            self.search_results.append(search_result)
        print("Generating Content Summary...")
        for result in self.search_results:
            content = self.agent.generate_content_summary(self.query, result)
            self.content.append(content)

        print("Generating Final Context...")
        self.context = self.agent.generate_context(self.query, self.content)

        return self.context