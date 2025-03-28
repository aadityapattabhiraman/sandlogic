#!/usr/bin/env python3

import sys
sys.path.insert(0, '../')
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_tavily import TavilySearch
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from classes import State, Output, Resto
from prompts import user_input_new_suggestion, scheduling_prompt



def get_user_data(prompt, model, additional_info=None):

    """
    Gets the user data to make a new reservation
    """

    history = []
    if additional_info != None:
        history.append(HumanMessage(content=additional_info))
    data = {}


    prompt_template = ChatPromptTemplate([
        ("system", prompt),
        MessagesPlaceholder("message")
    ])

    prompt = prompt_template.invoke({"message": history})

    response = model.invoke(prompt)
    print(response.content)

    while "<<DONE>>" not in response.content:

        history.append(AIMessage(response.content))
        user = input(">>> ")

        history.append(HumanMessage(user))
        prompt = prompt_template.invoke({"message": history})
        response = model.invoke(prompt)

        if "<<DONE>>" not in response.content:
            print(response.content)

        else:
            model_with_tools = model.bind_tools([Output])
            data = model_with_tools.invoke(response.content).tool_calls[0]["args"]

    return history, data


def tavily_search(data: dict, model):

    tool = TavilySearch(
        max_results=1,
        topic="general",
    )

    tavily_prompt = f"""
    give me 1 {data['cuisine']} restaturant name in {data['location']}
    for {data['occation']} occation. Do not include any links.
    """

    agent = create_react_agent(model, [tool])

    for step in agent.stream(
            {"messages": tavily_prompt},
            stream_mode="values",
        ):
        response = step["messages"][-1]

    return response


def get_resto_name(response, data, model):

    model_with_tools = model.bind_tools([Resto])
    data["restaurant"] = model_with_tools.invoke(response.content).tool_calls[0]["args"]["name"]

    return data


def try_hotel_or_not(data: dict, model):

    new = []
    pro = f"""
    You are a helpful assistant that is specialized in a restaurant suggestion
    Ask the user whether the user would like to try the {data["restaurant"]} restaurant or not.
    If they are interested to try the restaurant then respond only with "yes" or else "no".
    """

    prompt_template = ChatPromptTemplate([
        ("system", pro),
        MessagesPlaceholder("message")
    ])

    while True:

        prompt = prompt_template.invoke({"message": new})
        response = model.invoke(prompt)
        new.append(AIMessage(content=response.content))

        if response.content.lower() in ["yes", "no"]:
            break

        print(response.content)
        book = input(">>> ")
        new.append(HumanMessage(content=book))

    return response


def scheduling(current_timeframe: dict, history: list, prompt: str, model):
    
    prompt_template = ChatPromptTemplate([
        ("system", prompt),
        MessagesPlaceholder("message")
    ])

    while True:

        prompt = prompt_template.invoke({"message": history, "current_timeframe": current_timeframe})
        breaking = model.invoke(prompt).content
        print(breaking)
        history.append(AIMessage(content=breaking))

        breaker = model.invoke(f"""
        You are a responsible AI assistant that classifies user input as
        "yes" or "no". Your output can only be "yes" or "no". It is "yes"
        when the reservation is confirmed else it is "no"

        User: {breaking}
        """).content

        if breaker.lower() == "yes":
            break

        new_inp = input(">>> ")
        history.append(HumanMessage(content=new_inp))

    return breaking



def reserve(state: State):

    model = state["model"]
    history, data = get_user_data(user_input_new_suggestion, model)
    response = tavily_search(data, model)
    data = get_resto_name(response, data, model)
    resto_response = try_hotel_or_not(data, model)

    message = scheduling(state["current_timeframe"], history, scheduling_prompt, model)
    state["message"] = message
    state["data"] = data

    return state

