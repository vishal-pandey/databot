from langgraph.graph import StateGraph, START, END
from Nodes import generateRandomName, actionNode, call_model
from Edges import should_continue
from State import State

GraphBuilder = StateGraph(State)


GraphBuilder.add_node("entry", generateRandomName)
GraphBuilder.add_node("action", actionNode)
GraphBuilder.add_node("call_model", call_model)

GraphBuilder.add_edge(START, "entry")
GraphBuilder.add_edge("entry", "action")
GraphBuilder.add_conditional_edges(
    "action", should_continue
)
GraphBuilder.add_edge("action", END)