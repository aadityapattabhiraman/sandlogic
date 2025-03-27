#!/home/akugyo/Programs/Python/chatbots/bin/python

from pydantic import BaseModel, Field
from typing_extensions import TypedDict



class State(TypedDict):

    """
    A class to store the state of a graph
    """

    query: str
    message: str
    next_node: str
    data: dict



class Output(BaseModel):

    """
    A class to convert llm output to structured output for reservation
    """

    name: str = Field(description="The name under which reservation is done")
    location: str = Field(description="The preferred location")
    number_of_guests: str = Field(description="The number of guests")
    cuisine: str = Field(description="Preferred cuisine")
    occation: str = Field(description="Occation of the event")
    date: int = Field(description="date of month of the reservation")
    time: str = Field(description="requested time frame for 1 hour only")



class Mody(BaseModel):

    """
    A class to convert llm output to structured output for modification
    """

    name: str = Field(description="The name under which reservation is done")
    number_of_guests: str = Field(description="The number of guests")
    restaurant: str = Field(description="Restaurant name")
    date: int = Field(description="day of the month of reservation")



class Resto(BaseModel):

    """
    A class to get restaurant name
    """

    name: str = Field(description="The name of restaurant")



if __name__ == "__main__":

    print("Checking imports")
