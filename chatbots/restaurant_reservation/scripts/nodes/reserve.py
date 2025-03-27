#!/usr/bin/env python3

from ..classes import State, Output, Resto
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_tavily import TavilySearch
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent



def get_user_data():

    history = []
    data = {}

    prompt = """
    You are a responsible AI assistant who is specialized in creating a
    reservation for a user based on their location, cuisine preference,
    name, number of guests, date, occation(optional), time and availablity.
    Ask relevant questions for the purpose. After collecting all the
    info also confirm the information with the user. Once the
    conversation is completed you output should be "<<DONE>>". Do not
    mention anything related to the status of reservation. Try not to
    sound like a robot. Your final output once the conversation is
    completed should be of format:

    <<DONE>>
    "name": name,
    "location": location,
    "cuisine": cuisine,
    "number_of_guests": number of guests,
    "occation": occation,
    "date": date,
    "time": time,
    """

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

    return data


def tavily_search(data: dict):

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


def get_resto_name(response, data):

    model_with_tools = model.bind_tools([Resto])
    data["restaurant"] = model_with_tools.invoke(response.content).tool_calls[0]["args"]["name"]

    return data


def try_hotel_or_not(data: dict):

    new = []
    pro = f"""
    You are a helpful assistant that is specialized in a restaurant suggestion
    Ask the user whether the user would like to try the {data["restaurant"]} restaurant or not.
    If yes then respond only with "yes" else "no".
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


def reservation(current_timeframe: dict):
    
    pro = """
    You are a helpful AI assistant that is specialized in scheduling
    restaurant reservation. The reservation has been confirmed only
    if the time {current_timeframe} is "Available" else "Reservation
    is not available for the selected time" and give {current_timeframe}
    so that the user can select from that. If the reservation is
    available then inform them regarding it. Else inform otherwise

    For example:
    Let me say the time to schedule is 12 pm, when you cross reference
    the time to {current_timeframe} it says "Booked" so i cannot accept
    the reservation.
    I will give the output of {current_timeframe} whose value is
    "Available", then ask the user to select a time from the given time.
    """

    prompt_template = ChatPromptTemplate([
        ("system", pro),
        MessagesPlaceholder("message")
    ])

    new = []
    while True:

        prompt = prompt_template.invoke({"message": new, "current_timeframe": current_timeframe})
        breaking = model.invoke(prompt).content
        print(breaking)
        new.append(AIMessage(content=breaking))

        breaker = model.invoke(f"""
        You are a responsible AI assistant that classifies user input as
        "yes" or "no". Your output can only be "yes" or "no". It is "yes"
        when the reservation is confirmed else it is "no"

        User: {breaking}
        """).content

        if breaker.lower() == "yes":
            break

        new_inp = input(">>> ")
        new.append(HumanMessage(content=new_inp))

    return breaking



def reserve(state: State):

    data = get_user_data()
    response = tavily_search(data)
    data = get_resto_name(response, data)
    resto_response = try_hotel_or_not(data)
    message = reservation(current_timeframe)
    state["message"] = message
    state["data"] = data

    return state
