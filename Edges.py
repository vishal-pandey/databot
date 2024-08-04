from State import State

def should_continue(state: State):
    """Return the next node to execute."""
    last_message = state["messages"][-1]
    print(last_message, "VISHAL CHECK \n\n\n\n")
    # If there is no function call, then we finish
    # if not last_message.tool_calls:
    #     return "__end__"
    # Otherwise if there is, we continue
    return "call_model"