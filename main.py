from Graph import Graph
from config import config
from State import State
from langchain_core.messages import HumanMessage
import chainlit as cl
import random

@cl.on_chat_start
async def main():
    config["configurable"]["thread_id"] = str(int(random.random()*10000))

@cl.on_message
async def main(message: cl.Message):

    final_answer = await cl.Message(content="").send()

    inputs: State = {
        "name": "Random Name",
        "age": 12,
        "messages": [HumanMessage(content=message.content)]
    }

    async for event in Graph.astream_events(inputs, config, stream_mode="values", version="v1"):
        if event["event"] == "on_chat_model_stream" and event["name"] == "ChatOpenAI":
            content = event["data"]["chunk"].content or ""
            await final_answer.stream_token(token=content)
    await final_answer.update()
