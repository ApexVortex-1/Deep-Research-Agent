from langchain_groq import ChatGroq
from dotenv import load_dotenv
import logging

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2
)


def writer_node(state):
    
    logging.info("Writer node started.")

    query = state["query"]
    plan = state["plan"]
    research = state["research"]

    iteration = state.get("iteration", 0)

    prompt = f"""
You are a professional research writer.

TOPIC:
{query}

PLAN:
{plan}

RESEARCH:
{research}

Write a detailed structured report.
"""

    response = llm.invoke(prompt)
    logging.info("Writer node completed.")

    return {
        "report": response.content,
        "iteration": iteration + 1
    }