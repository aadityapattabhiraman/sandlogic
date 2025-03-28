#!/usr/bin/env python3

import sys
sys.path.insert(0, '../')
from classes import State
from prompts import user_input_new, modify_prompt
from .reserve import get_user_data, scheduling



def no_suggestion(state: State):

    history, data = get_user_data(user_input_new, state["model"], state["message"]) 
    message = scheduling(state["current_timeframe"], history, modify_prompt, state["model"])

    state["message"] = message 
    state["data"] = data

    return state
