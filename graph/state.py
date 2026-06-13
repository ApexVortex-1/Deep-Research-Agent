from typing import TypedDict, List, Optional



class ResearchState(TypedDict):
    query: str
    plan: str
    research : str
    report : str
    critique : str
    iteration: int
    max_iterations: int