# ProSearch

A powerful web search and content synthesis tool that leverages GROQ AI to provide comprehensive, context-rich answers to your queries.

## Features

Advanced web searching with filtering of sponsored content
Intelligent query refinement
Content scraping and summarization
Multi-source context synthesis

## Installation

```bash
pip install pro-search
```

## Usage
Basic usage example:

```python
from pro_search import ProSearch

# Initialize with your GROQ API key
searcher = ProSearch(api_key="your_groq_api_key")

# Run a search query
query = "What are the latest developments in quantum computing?"
result = searcher.run(query)

print(result)
```

## Configuration

The ProSearch class accepts the following parameters:
`api_key`: Your GROQ API key (required)
`num_results`: Number of search results to process (default: 5)
`num_retries`: Number of retry attempts for failed searches (default: 5)