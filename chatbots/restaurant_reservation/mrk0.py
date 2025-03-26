#!/home/akugyo/Programs/Python/chatbots/bin/python

import os
from langgraph.graph import StateGraph, START, END
from langchain_openai import AzureChatOpenAI
from typing_extensions import TypedDict
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field


class State(TypedDict):

    query: str
    message: str
    next_node: str
    data: dict


class Output(BaseModel):

    name: str = Field(description="The name under which reservation is done")
    location: str = Field(description="The preferred location")
    number_of_guests: str = Field(description="The number of guests")
    cuisine: str = Field(description="Preferred cuisine")
    occation: str = Field(description="Occation of the event")
    date: int = Field(description="date of month of the reservation")
    time: str = Field(description="requested time frame for 1 hour only")


class Mody(BaseModel):

    name: str = Field(description="The name under which reservation is done")
    number_of_guests: str = Field(description="The number of guests")
    restaurant: str = Field(description="Restaurant name")
    date: int = Field(description="day of the month of reservation")


class Resto(BaseModel):

    name: str = Field(description="The name of restaurant")


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

    history = []
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

    tool = TavilySearch(
        max_results=1,
        topic="general",
    )

    search = f"give me 1 {data['cuisine']} restaturant name in {data['location']} for {data['occation']} occation. Do not include any links."
    agent = create_react_agent(model, [tool])

    for step in agent.stream(
        {"messages": search},
        stream_mode="values",
    ):
        response = step["messages"][-1]

    model_with_tools = model.bind_tools([Resto])
    data["restaurant"] = model_with_tools.invoke(response.content).tool_calls[0]["args"]["name"]

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

    state["message"] = response.content
    state["data"] = data
    return {"message": response.content, "data": data}


def modify(state: State):

    data = {}
    history = []

    prompt = """
    You are a responsible AI assistant who is specialized in changing a
    reservation for a user based on their restaurant name, date, time,
    name for reservation, number of guests. Ask relevant questions for the purpose.
    Also ask the time that it has to be changed it to.
    After collecting all the info also confirm the information with the user.
    Once the conversation is completed you output should be "<<DONE>>".
    Do not mention anything related to the status of reservation.
    Try NOT to sound like a robot.
    Your final output once the conversation is completed should be of format:

    <<DONE>>
    "name": name,
    "restaurant": restaurant,
    "number_of_guests": number of guests,
    "date": date,
    "time": time,
    """

    prompt_template = ChatPromptTemplate([
        ("system", prompt),
        MessagesPlaceholder("message")
    ])

    prompt = prompt_template.invoke({"message": history})

    response = model.invoke(prompt)
    history.append(AIMessage(response.content))
    print(response.content)

    while "<<DONE>>" not in response.content:

        user = input(">>> ")

        history.append(HumanMessage(user))
        prompt = prompt_template.invoke({"message": history})
        response = model.invoke(prompt)
        history.append(AIMessage(response.content))

        if "<<DONE>>" not in response.content:
            print(response.content)

        else:
            model_with_tools = model.bind_tools([Mody])
            data = model_with_tools.invoke(response.content).tool_calls[0]["args"]

    pro = """
    You are a helpful AI assistant that is specialized in modifying
    restaurant reservation. The reservation can be confirmed only
    when the time requested by user {current_timeframe} is "Available" else "Reservation
    is not available for the selected time" and give {current_timeframe}
    so that the user can select from that. If the reservation is
    available then inform them regarding it. Else inform otherwise

    For example:
    Let me say the time to schedule is 12 pm, when i cross reference
    the time to {current_timeframe} and it says "Booked" so i cannot accept
    the reservation.
    I will give the output of {current_timeframe} whose value is
    "Available", then ask the user to select a time from the given time.
    """

    prompt_template = ChatPromptTemplate([
        ("system", pro),
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
            model.invoke("Thank user for using your service")
            break

        date = input(">>> ")
        history.append(HumanMessage(content=date))

    state["message"] = response.content
    state["data"] = data

    return state



if __name__ == "__main__":

    model = AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
        openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    )

    workflow = StateGraph(State)

    current_timeframe = {'12AM': 'Booked', '1PM': 'Booked', '2PM': 'Available', '3PM': 'Available', '7PM': 'Available', '8PM': 'Available', '9PM': 'Available', '10PM': 'Available'}

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

    # response = graph.invoke({"query": "hello, i would like to do a reservation"})
    # print(response)
    response = graph.invoke({"query": "hello, i would like to change my reservation"})
    print(response)
