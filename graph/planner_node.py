from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

def planner_node(state):

    query = state["query"]

    prompt = f"""
You are a senior research planner.

Break this topic into structured research plan:

{query}

Return structured sections and questions.
"""

    response = llm.invoke(prompt)

    return {
        "plan": response.content
    }