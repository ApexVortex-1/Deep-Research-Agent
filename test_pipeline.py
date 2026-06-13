from graph.workflow import app

result = app.invoke({
    "query": "Agentic AI"
})

print(result["plan"])
print("\n" + "="*50 + "\n")
print(result["research"])