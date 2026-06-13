from langgraph.graph import StateGraph,END
from graph.state import ResearchState
from graph.planner_node import planner_node
from graph.research_node import research_node


workflow = StateGraph(ResearchState)

workflow.add_node('planner',planner_node)
workflow.set_entry_point("planner")

workflow.add_node('research',research_node)
workflow.add_edge('planner','research')
workflow.add_edge('research',END)


app = workflow.compile()