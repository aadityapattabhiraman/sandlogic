#!/home/akugyo/Programs/Python/chatbots/bin/python

from openai import OpenAI
import os

class LLM:
    def __init__(self):
        self.client = OpenAI(base_url="http://164.52.209.85:6002", api_key="sandlogic")


    def run(self, prompt):
        chat_response = self.client.chat.completions.create(
            model="sl-llm",
            messages=prompt,
        )

        return chat_response.choices[0].message.content


if __name__ == "__main__":

    print(LLM().run(["I am a helpful ai assistant"]))
