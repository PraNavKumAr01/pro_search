from .pro_search import ProSearch

searcher = ProSearch(
    api_key="api-key"
)
query = "Your Query"

res = searcher.run(query)
print(res)