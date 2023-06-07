
""" OpenAI chatbot """

import openai
import configparser
from linkedin_ai.logging_config import logger


class ChatBot():

    def __init__(self, max_tokens=100):
        config = configparser.ConfigParser()
        config.read("config.ini")
        openai.api_key = config.get("OpenAI", "key")
        self.max_tokens = int(config.get("OpenAI", "maxtoken")) if config.get("OpenAI", "maxtoken") else max_tokens
        self.system_prompt = {"role": "system", "content": "you are a helpful assistant"}
        logger.info("API key Loaded")

    def build_gpt3_prompt(self, recent_msg):
        try:
            logger.debug("Building prompt")
            prompt = [self.system_prompt]
            prompt.append({"role": 'user', "content": recent_msg['body']})
            return prompt
        except Exception as e:
            logger.error(e)


    def construct_prompt(self, recent_msg):
        prompt = self.build_gpt3_prompt(recent_msg)
        return prompt


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
            content = response.get("choices")[0].get("message").get("content")
            return content
        except Exception as e:
            logger.error(e)


    def generate_msg(self, recipient, recipientHeadline):
        try:
            prompt = [
                self.system_prompt,
                {"role": "user", "content": f"write a short personalized message to {recipient} in context of linkedin (do not add regards). This is the profile headline of {recipient}: {recipientHeadline}"}
            ]
            response = self.call_gpt(prompt)
            gpt_reply = self.parse(response)
            return gpt_reply
        except Exception as e:
            logger.error(e)


