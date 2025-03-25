#!/home/akugyo/Programs/Python/chatbots/bin/python

import os
import random
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langchain_openai import AzureChatOpenAI
from typing_extensions import TypedDict
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field



model = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)


class State(TypedDict):

    query: str
    message: str
    next_node: str


def product_recommendation():

    pass


def chatbot():

    workflow = StateGraph(State)

    workflow.add_node("product recommendation", product_recommendation)

    workflow.add_edge(START, "")



if __name__ =="__main__":

    chatbot()
