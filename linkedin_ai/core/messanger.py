
""" Handle Linkedin Messaging """

from linkedin_ai.sessions.session_manager import SessionManager
from linkedin_ai.utils import *
from linkedin_ai import settings
from linkedin_ai.logging_config import logger
from urllib.parse import quote
from linkedin_ai.openai.chatbot import ChatBot


class Messanger(SessionManager):

    def get_recipientUrn(self, response):
        try:
            logger.info(" [+] Getting pre-requisites")
            for item in response.json().get("included"):
                if item.get("profileStatefulProfileActions"):
                    for i in item.get("profileStatefulProfileActions").get("overflowActions"):
                        if i.get("report"):
                            report = i.get("report")
                            return f'urn:li:fsd_profile:{report.get("authorProfileId")}'
        except Exception as e:
            logger.error(e)


    def get_trackingID(self, recipientUrn, username):
        try:
            logger.info(" [+] Getting trackingId")
            url = f"https://www.linkedin.com:443/voyager/api/graphql?includeWebMetadata=true&variables=(vieweeId:{recipientUrn.split('fsd_profile:')[-1]})&&queryId=voyagerLearningDashLearningRecommendations.7e671a8405bfd461031db616dd3ccf64"
            response = send_request(self.session, "GET", url, headers=build_headers(self.csrf_token, keyword=username))
            trackingId = response.json().get("data").get("data").get("learningDashLearningRecommendationsByProfile").get("metadata").get("trackingId")
            return trackingId
        except Exception as e:
            logger.error(e)


    def process_urls(self, urls):
        try:
            for url in urls:
                username = url.split('in/')[-1].replace('/','')
                logger.info(f" [+] Scraping {username}")
                modified_url = f"https://www.linkedin.com:443/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity={username}&decorationId=com.linkedin.voyager.dash.deco.identity.profile.TopCardSupplementary-120"
                response = send_request(self.session, 'GET', modified_url, headers=build_headers(self.csrf_token))
                recipientUrn = self.get_recipientUrn(response)
                trackingId = self.get_trackingID(recipientUrn, username)
                self.make_sale(recipientUrn, trackingId, username)
        except Exception as e:
            logger.error(e)


    def make_sale(self, recipientUrn, trackingId, recipient):
        bot = ChatBot()
        while True:
            chat_history = self.read_inbox(recipient=recipient)
            if not chat_history:
                # mean we already have a chat
                parsed_history = self.parse_chat(chat_history)
                if parsed_history:
                    recent_msg = sorted(parsed_history.get("all"), key=lambda x: x['timestamp'], reverse=True)[0]
                    if recipientUrn.lower() in recent_msg.get("sender").lower():
                        logger.info(f" [+] got reply from {recipient}")
                        prompt = bot.construct_prompt(parsed_history)
                        response = bot.call_gpt(prompt)
                        gpt_reply = bot.parse(response)
                        self.send_msg(gpt_reply, recipient, recipientUrn, trackingId)
                        continue
            else:
                inital_msg = bot.generate_msg(recipient)
                self.send_msg(inital_msg, recipient, recipientUrn, trackingId)


    def parse_chat(self, chat):
        try:
            logger.info(" [+] parsing chat history")
            history = {'bot': [], 'person': [], 'all': []}
            for message in chat.get("included"):
                sender = message.get("*sender")
                if sender is not None:
                    schema = {
                        "body": message.get("body").get("text"),
                        "timestamp": message.get("deliveredAt"),
                        "sender": message.get("*sender")
                    }
                    if self.own_urn.lower() in sender.lower():
                        history['bot'].append(schema)
                    else:
                        history['person'].append(schema)
                    history['all'].append(schema)
            return history
        except Exception as e:
            logger.error(e)


    @staticmethod
    def get_own_urn():
        try:
            logger.info(" [+] Getting own urn")
            with open("data/user_data.json", 'r') as f:
                urn = json.load(f).get('user_urn').strip('"')
            return urn
        except Exception as e:
            logger.error(e)


    @staticmethod
    def get_conversation_urn(response):
        try:
            return response.json().get("included")[0].get("conversationUrn")
        except Exception as e:
            logger.error(e)


    def dump_conversation_urn(self, recipient, response):
        try:
            logger.info(f" [+] Dumping conversation urn for {recipient}")
            conversation_urn = self.get_conversation_urn(response)
            if self.db.contains(self.msg.recipient == recipient):
                logger.info(" [+] conversation urn already exists")
                return
            self.db.insert({"recipient": recipient, "conversation_urn": conversation_urn})
            logger.info(f" [+] conversation urn added")
        except Exception as e:
            logger.error(e)


    def load_conversations(self):
        try:
            return self.db.all()
        except Exception as e:
            logger.error(e)


    def send_msg(self, message, recipient, recipientUrn, trackingId):
        try:
            logger.info(f" [+] Sending message to {recipient}")
            url = 'https://www.linkedin.com/voyager/api/voyagerMessagingDashMessengerMessages?action=createMessage'
            headers = build_headers(self.csrf_token, keyword=recipient)
            del headers['X-Li-Pem-Metadata']
            data = deepcopy(settings.MSG_PAYLOAD)
            data['message']['body']['text'] = message
            data['message']['originToken'] = generate_token()
            data['mailboxUrn'] = self.own_urn
            data['trackingId'] = trackingId
            data['hostRecipientUrns'] = [recipientUrn]
            response = send_request(self.session ,"POST", url, headers=headers, data=data)
            if response.status_code == 200:
                self.dump_conversation_urn(recipient, response)
                logger.info(f" [+] Message sent to {recipient}")
        except Exception as e:
            logger.error(e)


    def read_inbox(self, recipient):
        try:
            record = self.db.search(self.msg.recipient == recipient)
            if record:
                logger.info(f" [+] Reading inbox for {recipient}")
                conversation_urn = quote(record[0].get("conversation_urn"))
                url = f"https://www.linkedin.com/voyager/api/voyagerMessagingGraphQL/graphql?queryId=messengerMessages.8d15783c080e392b337ba57fc576ad21&variables=(conversationUrn:{conversation_urn})"
                response = send_request(self.session, "GET", url, headers=build_headers(self.csrf_token, keyword=recipient))
                if response.status_code == 200:
                    logger.info(f" [+] Inbox read for {recipient}")
                    return response.json()
        except Exception as e:
            logger.error(e)


    def run(self):
        if not self.load_cookies():
            logger.info(" [+] Cookies not found")
            self.login()
        if self.logged_in:
            logger.info(" [+] Starting crawler")
            self.db, self.msg = init_db()
            self.session = create_session(self.cookies)
            self.csrf_token = get_csrf_token(self.cookies)
            self.own_urn = self.get_own_urn()
            urls = load_urls()
            self.process_urls(urls)



