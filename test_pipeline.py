from graph.workflow import app

result = app.invoke({
    "query": "Agentic AI systems",
    "iteration": 0,
    "max_iterations": 2
})

print(result["report"])
print(result["critique"])
print("iterations:", result["iteration"])