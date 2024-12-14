from .pro_search import ProSearch

searcher = ProSearch(
    api_key="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"
)
query = "Who took the decisive catch that won india the t20 cricket world cup?"

res = searcher.run(query)
print(res)