from tools.search_tool import search_web

def research_node(state):

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

    return {
        "research": context
    }