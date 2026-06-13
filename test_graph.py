from graph.workflow import app

result = app.invoke({
    "query": "Deep Research Agents"
})

print(result["plan"])