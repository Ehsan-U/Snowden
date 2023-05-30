
""" OpenAI chatbot """

import openai
import configparser
from linkedin_ai.logging_config import logger


class ChatBot():

    def __init__(self, max_tokens=100):
        config = configparser.ConfigParser()
        config.read("config.ini")
        openai.api_key = config.get("OpenAI", "key")
        self.max_tokens = max_tokens
        logger.info(" [+] API key Loaded")


    def construct_prompt(self, chat_history):
        try:
            pass
        except Exception as e:
            logger.error(e)


    def call_gpt(self, prompt):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=prompt,
                max_tokens=self.max_tokens
            )
            return response
        except Exception as e:
            logger.error(e)


    def parse(self, response):
        try:
            pass
        except Exception as e:
            logger.error(e)


    def generate_msg(self, recipient):
        try:
            prompt = [
                {"role": "system", "content": "you are a helpful assistant"},
                {"role": "user", "content": f"write an initial personalized message to {recipient} in context of linkedin."}
            ]
            response = self.call_gpt(prompt)
            gpt_reply = self.parse(response)
            return gpt_reply
        except Exception as e:
            logger.error(e)

