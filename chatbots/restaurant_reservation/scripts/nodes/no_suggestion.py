#!/usr/bin/env python3

import sys
sys.path.insert(0, '../')
from classes import State
from prompts import user_input_new, scheduling_prompt
from .reserve import get_user_data, scheduling



def no_suggestion(state: State):

    history, data = get_user_data(
        prompt=user_input_new,
        model=state["model"],
        additional_info=state["message"]
    )
    message = scheduling(
        current_timeframe=state["current_timeframe"],
        history=history,
        prompt=scheduling_prompt,
        model=state["model"]
    )

    state["message"] = message 
    state["data"] = data

    return state
