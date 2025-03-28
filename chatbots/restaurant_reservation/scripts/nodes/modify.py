#!/usr/bin/env python3

import sys
sys.path.insert(0, '../')
from .reserve import get_user_data, scheduling
from classes import State
from prompts import scheduling_prompt, modify_prompt



def modify(state: State):

    history, data = get_user_data(modify_prompt) 
    message = scheduling(history, scheduling_prompt)
    state["message"] = message
    state["data"] = data

    return state
