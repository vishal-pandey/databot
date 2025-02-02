from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from State import State
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from toolkits.generic_sql.SQLDatabaseToolkit import SQLDatabaseToolkit


from toolkits.generic_sql.SQLDatabaseToolkit import SQLDatabaseToolkit
from models import model
from databases import db
from langchain_core.messages import HumanMessage, SystemMessage
from toolkits.generic_sql.dbragtool import getListOfTables, getRelationshipsForTables




# Node to generate the user generated question and format in a way that it can be answered effectively to the users.
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

template_message = """You are a helpful agent your objective is to generate a question that can be asked to LLM to answer the question of the user.
                                               Rewrite the question in such a way that answer generated by the LLM is like this is a result of the answer to the feature result of <strong>OpenMetadata DataCatalog response.</strong>
                                                Rewrite the question in such a way that answer generated by the LLM is like it is not be in format of database query operation and answer should be like an Data Steward is providing the result to another collegue which require the data.
                                               You should also use the other system message to take into account for generating the question.
                                               Please rewrite the question the original question is below
                                                {question}"""


def generate_question_node(state: State):
    question = state["question"]
    

    msgs = state["messages"]

    messages = []

    for m in msgs:
        messages.append(("system", m.content))
    # msgs.append(SystemMessage(content=template_message))

    messages.append(("user", template_message))
    prompt_template = ChatPromptTemplate.from_messages(messages)

    question_generation_model = prompt_template | model

    response = question_generation_model.invoke({"question": question})
    # print(response.content, "VISHAL IS DEBUGGING \n\n\n\n\n\n")
    return {"question": response, "messages": [HumanMessage(content=response.content)]}





# Node to generate the answer as sql and execute and send the result to the user.
sqltoolkit = SQLDatabaseToolkit(db=db, llm=model)
dbtools = sqltoolkit.get_tools()

model_db = model.bind_tools(dbtools)

def call_db_model(state: State):
    # print(state["messages"][7], "\n\n\n\n\n\n\n\n STATE", state["messages"][0])
    response = model_db.invoke(state["messages"])

    return {"messages": response}



# TOOL Node
import json
from langchain_core.messages import ToolMessage

class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


tool_node = BasicToolNode(tools=dbtools)


# DB INFO NODE



def db_info_node(state: State):
    promptWithSchemaAndRelationToLLM = """Below is the relevent schema of the tables that might solve the problem first use the schema to look if it can be solved then you can use all the list tables available to you. 
        
        
        {schema}


        Below is also relationship between these tables you can also use these to structure the sql query.
        
        {relationships}

        All the entity tables also have json column which contains the metadata of the entity in the json format. You can use this metadata to generate the query. You should query 1 row for each entity table and use the metadata to generate the query.
    """

    question = state["question"]
    print("\n\n\n\n\n\n\n\n\n CHECKING QUESTION", question)
    schema = getListOfTables(question)

    tables = schema["tables"]
    relationships = getRelationshipsForTables(tables)
    schema = str(schema["schemas"])
    promptWithSchemaAndRelationToLLM = promptWithSchemaAndRelationToLLM.format(schema=schema, relationships=relationships)

    state["messages"].append(SystemMessage(content=promptWithSchemaAndRelationToLLM))
    for i in range(len(state["messages"])-1, 0, -1):
        if isinstance(state["messages"][i], HumanMessage):
            del state["messages"][i]

    state["messages"].append(HumanMessage(content=question))

    # Remove the last HumanMessage and add the new one, check if the last message is HumanMessage



    # print("FINAL \n\n\n CHECK \n\n\n", state['messages'][7], type(state['messages'][7]))

    return state

