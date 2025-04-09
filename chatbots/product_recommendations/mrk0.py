#!/home/akugyo/Programs/Python/chatbots/bin/python

import os
from langgraph.graph import StateGraph, START, END
from langchain_openai import AzureChatOpenAI
from typing_extensions import TypedDict
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai.chat_models.azure import AzureChatOpenAI
from pydantic import BaseModel, Field
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent



class State(TypedDict):

    query: str
    message: str
    next_node: str
    data: dict
    model: AzureChatOpenAI
    history: list


class Product(BaseModel):

    product: str = Field(description="The name of the product that they are interested in")


def greeting(state: State):

    prompt = """
    You are a responsible AI assistant that is specialized in suggesting products
    for the user. Your task is to greet the user.

    For example:
    Chatbot: Hello! I'm a chatbot specialized with product suggestions. How can I help
    you today?
    """

    response = state["model"].invoke(prompt)
    state["query"] = response.content
    state["history"].append(AIMessage(content=response.content))
    print(response.content)

    return state


def product(state: State):

    human_input = input(">>> ")
    state["message"] = human_input
    state["history"].append(HumanMessage(content=human_input))

    prompt = """
    You are a chatbot specialized in classifying the user intput into "decided" or
    "undecided". Your output can only be either one of "decided" or "undecided".
    Your output is "decided" when human specifies a product that he/she is
    interested in. Your output is "undecided" when human does not specify a
    product that they would like recommendations.

    For example:
    Human: hi, how are you doing today?
    Chatbot: undecided

    Human: hi, i would like to buy headphones.
    Chatbot: decided
    """

    prompt_template = ChatPromptTemplate([
        ("system", prompt),
        MessagesPlaceholder("history")
    ])
   
    while True:

        prompt = prompt_template.invoke({"history": state["history"]})
        response = state["model"].invoke(prompt)

        if "undecided" in response.content.lower():

            sub_prompt = """
            You are a chatbot specialized in giving product recommendations.
            if the user is greeting you, then greet and ask what products
            they would need recommendations for. So that they stick with the task
            at hand.
            """

            sub_prompt_template = ChatPromptTemplate([
                ("system", sub_prompt),
                MessagesPlaceholder("history")
            ])

            sprompt = sub_prompt_template.invoke({"history": state["history"]})
            response = state["model"].invoke(sprompt)
            print(response.content)
            state["query"] = response.content
            state["history"].append(AIMessage(content=response.content))

            human_input = input(">>> ")
            state["message"] = human_input
            state["history"].append(HumanMessage(content=human_input))

        else:

            model_with_tools = state["model"].bind_tools([Product])
            product = model_with_tools.invoke(human_input).tool_calls[0]["args"]
            state["data"] = product

            break

    return state


def questions_for_product(state: State):

    prompt = """
    You are a responsible AI assistant that is specialized in giving product
    recommendations to user. Your task is to ask user questions based on the
    product, in order to find the most optimal option available for the user.
    Once you are done with all the questions then your final output must be
    "<<DONE>>" followed by all the i will search. Ask only 1 question at a time.
    Do not mention any product name or options as that is not your task.

    Always ask the user if they have any specific requirements else Ask more than 5 questions.
    Always ask the budget of the product.
    """

    prompt_template = ChatPromptTemplate([
        ("system", prompt),
        MessagesPlaceholder("history")
    ])

    while True:

        prompt = prompt_template.invoke({"history": state["history"]})
        response = state["model"].invoke(prompt)
        print(response.content)
        state["history"].append(AIMessage(content=response.content))
        state["query"] = response.content

        if "<<DONE>>" in response.content:

            prompt = """
            Based on the responses provided by the user, create a search query
            in order to search the web for 5 such products. Just give the query
            alone.
            """

            prompt_template = ChatPromptTemplate([
                ("system", prompt),
                MessagesPlaceholder("history")
            ])

            prompt = prompt_template.invoke({"history": state["history"]})

            response = state["model"].invoke(prompt)
            print(response.content)
            state["query"] = response.content
            break

        else:

            human_input = input(">>> ")
            state["message"] = human_input
            state["history"].append(HumanMessage(content=human_input))

    return state


def search(state: State):

    tool = TavilySearch(
        max_results=1,
        topic="general",
    )

    search = f"give me a list of 5 {state['query']}. Only give 5 product names" 
    agent = create_react_agent(state["model"], [tool])

    for step in agent.stream(
        {"messages": search},
        stream_mode="values",
    ):
        response = step["messages"][-1]

    print(response.content)

    return state


def chatbot():

    model = AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
        openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    )

    workflow = StateGraph(State)

    workflow.add_node("greeting", greeting)
    workflow.add_node("product", product)
    workflow.add_node("question", questions_for_product)
    workflow.add_node("search", search)

    workflow.add_edge(START, "greeting")
    workflow.add_edge("greeting", "product")
    workflow.add_edge("product", "question")
    workflow.add_edge("question", "search")
    workflow.add_edge("search", END)

    graph = workflow.compile()

    response = graph.invoke({"model": model, "history": [], "data": {}})

    return response


if __name__ == "__main__":

    chatbot()
