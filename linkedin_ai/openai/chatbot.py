
""" OpenAI chatbot """
import json
from json.decoder import JSONDecodeError
import openai
from linkedin_ai.logging_config import logger
import linkedin_ai.settings as settings


class ChatBot():

    def __init__(self):
        openai.api_key = settings.key
        self.max_tokens = settings.max_tokens
        self.system_prompt = {"role": "system", "content": """you are a sales assistant who sells web development services to a person and always respond in JSON format: {
            "user_response": "original query",
            "is_reply_required": bool decide based on user_response whether reply required to user_response or not,
            "gpt_reply": "reply to person message if reply required"
            "is_user_agree_to_buy": bool decide based on user_response whether user want to buy service or not
        }"""}
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
                model="gpt-4",
                messages=prompt,
                max_tokens=self.max_tokens
            )
            return response
        except Exception as e:
            logger.error(e)


    def parse(self, response):
        try:
            content = response.get("choices")[0].get("message").get("content")
            data = json.loads(content)
            return data
        except JSONDecodeError as e:
            return content
        except Exception as e:
            logger.error(e)


    def generate_msg(self, recipient, recipientHeadline):
        try:
            prompt = [
                {"role": "system", "content": "you are a sales assistant who sell web development services to a person and keep the responses short"},
                {"role": "user", "content": f"This is the profile headline of {recipient}: {recipientHeadline}"}
            ]
            response = self.call_gpt(prompt)
            gpt_reply = self.parse(response)
            return gpt_reply
        except Exception as e:
            logger.error(e)


