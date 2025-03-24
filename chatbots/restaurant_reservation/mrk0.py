#!/home/akugyo/Programs/Python/chatbots/bin/python

import os
import random
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langchain_openai import AzureChatOpenAI
from typing_extensions import TypedDict
from langchain_core.prompts import PromptTemplate



model = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)



class State(TypedDict):

    query: str
    message: str
    next_node: str



def greeting(state: State):

    print("Hi. I am a assistant designed to schedule or modify existing restaturant reservation.")
    return state



def initial(state: State):

    prompt = """You are an assistant that classifies user input into
    either "new" or "modify" or "undefined".
    Your response should be limited to either "new" or "modify" or
    "undefined".

    Example:
    User: I would like to make a reservation.
    AI: new

    User: I would like to change my reservation that I made earlier.
    AI: modify

    User: Hello did you have breakfast.
    AI: undefined

    User: {user_input}
    AI:
    """

    prompt_template = PromptTemplate.from_template(prompt)

    for _ in range(3):

        response = model.invoke(prompt_template.invoke({"user_input": state["query"]}))
        if response.content in ["new", "modify"]:
            break

        reg = "I am an assistant designed to schedule or modify existing restaurant reservations"
        print(reg)
        state["query"] = input(">>> ")

    else:

        print("Stop WASTING computation resources")
        exit()

    return {"next_node": response.content}



def reserve(state: State):

    prompt = """
    You are a responsible AI assistant who is specialized in creating a
    reservation for a user based on their location, cuisine preference,
    name, number of guests and availablity. Ask relevant questions for the purpose.
    Your output should be of format:
    {
    "name": name,
    "location": location,
    "cuisine": cuisine,
    "number_of_guests": number of guests,
    }
    """

    response = model.invoke(prompt)
    print(response)
    return {"message": "les see reserve"}



def modify(state: State):

    print(state)
    return {"message": "les see modify"}



workflow = StateGraph(State)

workflow.add_node("greeting", greeting)
workflow.add_node("initial", initial)
workflow.add_node("new", reserve)
workflow.add_node("modify", modify)

workflow.add_edge(START, "greeting")
workflow.add_edge("greeting", "initial")
workflow.add_conditional_edges("initial", lambda state: state["next_node"],
    ["new", "modify", END])

workflow.add_edge("new", END)
workflow.add_edge("modify", END)

graph = workflow.compile()

response = graph.invoke({"query": "hello, i would like to do a reservation"})
print(response["message"])
response = graph.invoke({"query": "hello, i would like to change my reservation"})
print(response["message"])
