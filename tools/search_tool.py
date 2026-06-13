from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

tavily_client = TavilyClient(
    api_key = os.getenv("TAVILY_API_KEY")
)

def search_web(query: str):
    results = tavily_client.search(
        query=query,
        search_depth="basic"
    )

    return results["results"]