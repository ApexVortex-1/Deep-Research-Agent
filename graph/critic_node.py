from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model = "llama-3.1-8b-instant",
    temperature = 0
)

def critic_node(state):

    report = state["report"]

    prompt = f"""
You are a strict AI critic.

Analyze this report:

{report}

Return ONLY one word:
APPROVE or REWRITE
"""

    response = llm.invoke(prompt)

    decision = response.content.strip()

    return {
        "critique": decision
    }