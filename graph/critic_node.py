from langchain_groq import ChatGroq
from dotenv import load_dotenv
import logging

load_dotenv()

llm = ChatGroq(
    model = "llama-3.1-8b-instant",
    temperature = 0
)

def critic_node(state):
    
    logging.info("Critic node started.")    

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
    
    
    logging.info(f"Critic node decision: {decision}")

    return {
        "critique": decision
    }