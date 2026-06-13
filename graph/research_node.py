from tools.search_tool import search_web
import logging

def research_node(state):
    
    logging.info("Research node started.")

    query = state["query"]

    results = search_web(query)

    context = ""

    for r in results:
        context += f"""
Title: {r['title']}
Content: {r['content']}
URL: {r['url']}
---
"""
    logging.info("Research node completed.")
    return {
        "research": context
    }