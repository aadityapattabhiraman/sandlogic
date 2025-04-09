#!/home/akugyo/Programs/Python/chatbots/bin/python

import os
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from langchain_openai.chat_models.azure import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage


class State(TypedDict):

    """
    A class to store the state of a graph
    """

    prompt: str
    message: str
    next_node: str
    data: dict
    model: AzureChatOpenAI
    current_timeframe: dict



def everything(state: State):

    history = []

    while True:

        prompt_template = ChatPromptTemplate([
            ("system", state["prompt"]),
            MessagesPlaceholder("message")
        ])
        prompt = prompt_template.invoke({"message": history})
        response = state["model"].invoke(prompt)
        print(response.content)

        if "<<DONE>>" in response.content:
            break

        history.append(AIMessage(content=response.content))
        message = input(">>> ")
        history.append(HumanMessage(content=message))



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
