from langgraph.graph import StateGraph, END

from graph.state import ResearchState
from graph.planner_node import planner_node
from graph.research_node import research_node
from graph.writer_node import writer_node
from graph.critic_node import critic_node

workflow = StateGraph(ResearchState)

workflow.add_node("planner", planner_node)
workflow.add_node("research", research_node)
workflow.add_node("writer", writer_node)
workflow.add_node("critic", critic_node)

workflow.set_entry_point("planner")

workflow.add_edge("planner", "research")
workflow.add_edge("research", "writer")
workflow.add_edge("writer", "critic")
workflow.add_edge("critic", END)

app = workflow.compile()