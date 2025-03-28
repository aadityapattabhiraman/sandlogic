#!/usr/bin/env python3

from classes import State



def greeting(state: State):

    """
    A node that greets the user
    """

    print(state["model"].invoke("""
    You are a helpful AI assistant who is specialized in creating and
    modifying the user restaurant reservation. Greet the user and ask
    them what they would like to do.
    """).content)

    return state
