from Graph import Graph
from config import config
from State import State
from langchain_core.messages import HumanMessage, SystemMessage
import chainlit as cl
import random
from SystemPrompt import SystemPrompt

inputs:State = {
            "messages": [SystemMessage(content=SystemPrompt)]
        }

@cl.on_chat_start
async def main():
    config["configurable"]["thread_id"] = str(int(random.random()*10000))
    # config["configurable"]["thread_id"] = "123"

@cl.on_message
async def main(message: cl.Message):

    final_answer = await cl.Message(content="").send()

    # inputs:State = {
    #         "question": message.content
    #     }
    print(inputs, "BEFORE \n")
    inputs["question"] = message.content
    inputs["messages"].append(HumanMessage(content=message.content))
    print(inputs, "AFTER \n")

    async for event in Graph.astream_events(inputs, config, stream_mode="values", version="v1"):
        if event["event"] == "on_chat_model_stream" and event["name"] == "ChatOpenAI" :
        # if event["event"] == "on_chat_model_stream" and event["name"] == "ChatOpenAI" and event["metadata"]["langgraph_node"] != "generate_question_node" and event["metadata"]["langgraph_node"] != "tools":
            # print(event)
            content = event["data"]["chunk"].content or ""
            await final_answer.stream_token(token=content)
    await final_answer.update()
