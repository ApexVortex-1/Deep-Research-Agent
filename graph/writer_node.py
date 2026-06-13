from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2
)


def writer_node(state):
    query = state['query']
    plan = state['plan']
    research = state['research']
    
    prompt = f"""
You are a professional research writer.

Write a detailed report based on:

TOPIC:
{query}

PLAN:
{plan}

RESEARCH DATA:
{research}

Structure the report clearly with headings and explanations.
"""
    response = llm.invoke(prompt)
    return {
        "report": response.content
    }