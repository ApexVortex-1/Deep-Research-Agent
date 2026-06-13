def route_after_critic(state):

    decision = state["critique"]
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 2)

    if iteration >= max_iterations:
        return "end"

    if decision == "REWRITE":
        return "writer"

    return "end"