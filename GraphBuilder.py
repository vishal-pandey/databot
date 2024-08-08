from langgraph.graph import StateGraph, START, END
from Nodes import call_db_model, generate_question_node, tool_node
from edges.route import route_tools
from State import State

GraphBuilder = StateGraph(State)

# GraphBuilder.add_node("call_model", call_model)
GraphBuilder.add_node("call_db_model", call_db_model)
GraphBuilder.add_node("tools", tool_node)
# GraphBuilder.add_node("generate_question_node", generate_question_node)


GraphBuilder.add_edge(START, "call_db_model")
# GraphBuilder.add_edge("generate_question_node", "call_db_model")
# GraphBuilder.add_edge("call_model", "call_db_model")

GraphBuilder.add_edge("tools", "call_db_model")

GraphBuilder.add_conditional_edges(
    "call_db_model",
    route_tools
)

