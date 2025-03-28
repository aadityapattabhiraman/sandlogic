#!/home/akugyo/Programs/Python/chatbots/bin/python

import os
import sys
sys.path.insert(0, './scripts/')
from langgraph.graph import StateGraph, START, END
from langchain_openai import AzureChatOpenAI
from classes import State
from nodes.modify import modify
from nodes.greeting import greeting
from nodes.reserve_or_modify import new_or_modify
from nodes.suggestion_or_not import suggestion_or_not
from nodes.reserve import reserve
from nodes.no_suggestion import no_suggestion



def chatbot():

    model = AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
        openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    )

    current_timeframe = {
        '12AM': 'Booked',
        '1PM': 'Booked',
        '2PM': 'Available',
        '3PM': 'Available',
        '7PM': 'Available',
        '8PM': 'Available',
        '9PM': 'Available',
        '10PM': 'Available',
    }

    workflow = StateGraph(State)

    workflow.add_node("greeting", greeting)
    workflow.add_node("initial", new_or_modify)
    workflow.add_node("new", suggestion_or_not)
    workflow.add_node("modify", modify)
    workflow.add_node("suggestion", reserve)
    workflow.add_node("no_suggestion", no_suggestion)

    workflow.add_edge(START, "greeting")
    workflow.add_edge("greeting", "initial")
    workflow.add_conditional_edges("initial", lambda state: state["next_node"],
        ["new", "modify"])

    workflow.add_conditional_edges("new", lambda state: state["next_node"],
                                   ["no_suggestion", "suggestion"])
    workflow.add_edge("no_suggestion", END)
    workflow.add_edge("suggestion", END)

    graph = workflow.compile()
    
    while True:

        response = graph.invoke({"model": model, "current_timeframe": current_timeframe})



if __name__ == "__main__":

    chatbot()
