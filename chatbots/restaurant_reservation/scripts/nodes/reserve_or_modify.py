#!/usr/bin/env python3

import sys
sys.path.insert(0, '../')
from langchain_core.prompts import PromptTemplate
from classes import State



def new_or_modify(state: State):

    """
    A node which uses conditional edge to send user to create new reservation
    or modify existing reservation
    """

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

        state["query"] = input(">>> ")

        response = state["model"].invoke(prompt_template.invoke(
            {"user_input": state["query"]}
        ))

        if response.content in ["new", "modify"]:
            break

        reg = "I am an assistant designed to schedule or modify "\
            "existing restaurant reservations"
        print(reg)

    else:

        print("Stop WASTING computation resources")
        exit()

    return {"next_node": response.content}
