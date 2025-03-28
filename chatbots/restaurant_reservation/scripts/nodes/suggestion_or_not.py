#!/usr/bin/env python3

from classes import State
from langchain_core.prompts import PromptTemplate



def suggestion_or_not(state: State):

    prompt = """
    You are a helpful AI assistant who is specialized in asking the user
    whether the person has a restaurant name in mind or whether they
    would like some suggestions.
    """
    print(state["model"].invoke(prompt).content)

    prompt = """You are an assistant that classifies user input into
    either "suggestion" or "no_suggestion".
    Your response should be limited to either "suggestion" or "no_suggestion".

    User: Barbeque nation.
    AI: no_suggestion

    User: McDonalds
    AI: no_suggestion

    User: I would like you to suggest.
    AI: suggestion

    User: {user_input}
    AI:
    """

    prompt_template = PromptTemplate.from_template(prompt)

    for _ in range(3):

        user_input = input(">>> ")
        response = state["model"].invoke(prompt_template.invoke({"user_input": user_input}))
        if response.content in ["suggestion", "no_suggestion"]:
            break

        reg = "I am an assistant designed to schedule restaurant reservations"
        print(reg)
        state["query"] = input(">>> ")

    else:

        print("Stop WASTING computation resources")
        exit()

    return {"next_node": response.content, "message": user_input}
