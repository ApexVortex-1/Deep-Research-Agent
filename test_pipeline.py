from graph.workflow import app

result = app.invoke({
    "query": "Agentic AI systems and their applications"
})

print("\n===== PLAN =====\n")
print(result["plan"])

print("\n===== RESEARCH =====\n")
print(result["research"])

print("\n===== REPORT =====\n")
print(result["report"])

print("\n===== CRITIQUE =====\n")
print(result["critique"])