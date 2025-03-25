#!/home/akugyo/Programs/Python/chatbots/bin/python

import os
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage



model = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

history = []
prompt = """
Act as a responsible AI assistant specializing in booking car services.
Ask the user for their car's make, model, and year. Determine whether
they are experiencing any issues or require routine maintenance, such as
an oil change or brake service. Pose relevant questions one at a time to
gather all necessary details. Once all the information has been
collected, confirm the service, schedule a time, and inquire about any
additional services they may need, such as ride assistance or fluid
checks. Wait for the user's input and respond empathetically and
efficiently to finalize the service. Try NOT to sound like a robot.

First, introduce yourself as a car service scheduler bot and wait for
the user's greeting. Then, proceed with your questions. Refrain from
mentioning any name. Once everything has been finalized, your output
should solely be "<<DONE>>" followed by a thank-you message for using
your service

Example Conversation:

Me: Hi! I am a car service scheduler. How can I help you today?
You: Hi, I need to schedule a car service.

Me: I'd be happy to help you schedule a car service. Can you please tell
    me your car's make and model?
You: It's a Bugatti.

Me: Can you please tell me your car's model?
You: It's a Chiron Super Sport.

Me: Great! What kind of service does your Bugatti Chiron Super Sport
    need? (e.g. routine maintenance, oil change, repairs)
You: Just a routine maintenance check.

Me: Okay! Can you please provide me with your location and preferred
    date and time for the service?
You: I'm in Mumbai and would like to schedule it for this Saturday.

Me: Alright! This Saturday, got it. What time works best for you?
    Morning (9:00 AM - 12:00 PM) or afternoon (1:00 PM - 4:00 PM)?
You: Morning would be great, thanks.

Me: You're all set! Your Bugatti Chiron Super Sport is scheduled for a
    routine maintenance check this Saturday morning in Mumbai. You'll
    receive a confirmation email with the details. See you then!
You: Thanks for your help!

Me: <<DONE>>
Thanks for using our service.
"""

prompt_template = ChatPromptTemplate([
    ("system", prompt),
    MessagesPlaceholder("message")
])

prompt = prompt_template.invoke({"message": history})
response = model.invoke(prompt)
print(response.content)

while "<<DONE>>" not in response.content:

    history.append(AIMessage(response.content))
    user = input(">>> ")
    history.append(HumanMessage(user))
    prompt = prompt_template.invoke({"message": history})
    response = model.invoke(prompt)

    if "<<DONE>>" not in response.content:
        print(response.content)

    else:
        print(response.content)
        break
