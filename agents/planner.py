from langchain_groq import ChatGroq
from dotenv import load_dotenv


load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)


def planner_agent(query: str):

    prompt = f"""
You are a senior research planner.

Break the following topic into a structured research plan:

Topic: {query}

Return:
1. Main sections
2. Subsections
3. Key questions to research
"""
    response = llm.invoke(prompt)
    return response.content