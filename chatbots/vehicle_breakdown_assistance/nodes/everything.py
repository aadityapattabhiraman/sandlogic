#!/usr/bin/env python3

from classes import State
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage



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

        history.append(AIMessage(content=response.content))
        message = input(">>> ")
        history.append(HumanMessage(content=message))
