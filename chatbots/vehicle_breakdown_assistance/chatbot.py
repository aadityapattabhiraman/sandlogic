#!/home/akugyo/Programs/Python/chatbots/bin/python

import os
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, START, END
from classes import State
from nodes.everything import everything


def chatbot():

    model = AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
        openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    )

    with open("prompt.txt") as f:
        prompt = f.read()

    workflow = StateGraph(State)
    workflow.add_node("everything", everything)

    workflow.add_edge(START, "everything")
    workflow.add_edge("everything", END)

    graph = workflow.compile()

    graph.invoke({"model": model, "prompt": prompt})

if __name__ == "__main__":

    chatbot()
