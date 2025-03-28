#!/usr/bin/env python3

from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langchain_openai.chat_models.azure import AzureChatOpenAI



class State(TypedDict):

    """
    A class to store the state of a graph
    """

    prompt: str
    message: str
    next_node: str
    data: dict
    model: AzureChatOpenAI
    current_timeframe: dict
