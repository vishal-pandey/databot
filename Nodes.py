from langchain_core.runnables import RunnableConfig
from State import State
from langchain_core.tools import tool

from langchain_openai import ChatOpenAI

def generateRandomName(state: State, config: RunnableConfig) -> State:
    print(state)
    return { "name": "Vishal", "age": 27}



def actionNode(state: State) -> State:
    print(state)
    return state


@tool
def search(query: str):
    """Call to surf the web"""
    return ["The answer to your question lies within"]



tools = [search]

# tool_node = ToolNode(tools)


model = ChatOpenAI(temperature=0, streaming=True)

bound_model = model.bind_tools(tools)


# Define the function that calls the model
def call_model(state: State):
    response = model.invoke(state["messages"])
    # We return a list, because this will get added to the existing list
    return {"messages": response}