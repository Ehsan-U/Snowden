
""" Handle Linkedin Messaging """

from linkedin_ai.sessions.session_manager import SessionManager
from linkedin_ai.utils import *
from linkedin_ai import settings
from linkedin_ai.logging_config import logger
from urllib.parse import quote
from linkedin_ai.openai.chatbot import ChatBot


class Messanger(SessionManager):

    def get_name(self, response):
        try:
            logger.debug("Getting name")
            for item in response.json().get("included"):
                if item.get("publicIdentifier"):
                    return item.get("firstName")
        except Exception as e:
            logger.error(e)


    def get_headline(self, response):
        try:
            logger.debug("Getting headline")
            for item in response.json().get("included"):
                if item.get("headline"):
                    return item.get("headline")
        except Exception as e:
            logger.error(e)


    def get_recipientUrn(self, response):
        try:
            logger.debug("Getting pre-requisites")
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
            logger.debug("Getting trackingId")
            url = f"https://www.linkedin.com:443/voyager/api/graphql?includeWebMetadata=true&variables=(vieweeId:{recipientUrn.split('fsd_profile:')[-1]})&&queryId=voyagerLearningDashLearningRecommendations.7e671a8405bfd461031db616dd3ccf64"
            response = send_request(self.session, "GET", url, headers=build_headers(self.csrf_token, keyword=username))
            trackingId = response.json().get("data").get("data").get("learningDashLearningRecommendationsByProfile").get("metadata").get("trackingId")
            return trackingId
        except Exception as e:
            logger.error(e)


    def get_user_metadata(self, response, username):
        recipient_name = self.get_name(response)
        recipient_headline = self.get_headline(response)
        recipient_urn = self.get_recipientUrn(response)
        tracking_id = self.get_trackingID(recipient_urn, username)
        return {
            "recipient_name": recipient_name,
            "recipient_headline": recipient_headline,
            "recipient_urn": recipient_urn,
            "tracking_id": tracking_id,
            "recipient_username": username
        }


    def process_urls(self, urls):
        try:
            for url in urls:
                username = url.split('in/')[-1].replace('/','')
                logger.info(f"Scraping {username}")
                modified_url = f"https://www.linkedin.com:443/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity={username}&decorationId=com.linkedin.voyager.dash.deco.identity.profile.TopCardSupplementary-120"
                response = send_request(self.session, 'GET', modified_url, headers=build_headers(self.csrf_token))
                metadata = self.get_user_metadata(response, username)
                self.make_sale(**metadata)
        except Exception as e:
            logger.error(e)


    def make_sale(self, recipient_name, recipient_headline, recipient_urn, tracking_id, recipient_username):
        bot = ChatBot()
        inital_timer = time.time()
        while True:
            chat_history = self.read_inbox(recipient=recipient_username)
            if chat_history:
                if self.reached_user_limit(recipient_username):
                    logger.debug(f"Reached user messages limit")
                    break
                # mean we already have a chat
                parsed_history = self.parse_chat(chat_history, recipient_name)
                if parsed_history:
                    recent_msg = sorted(parsed_history.get("all"), key=lambda x: x['timestamp'], reverse=True)[0]
                    if recipient_urn.lower() in recent_msg.get("sender").lower():
                        inital_timer = time.time()
                        logger.info(f"got reply from {recipient_name}")
                        prompt = bot.construct_prompt(recent_msg)
                        if prompt:
                            response = bot.call_gpt(prompt)
                            response = bot.parse(response)
                            if response:
                                message = response.get("gpt_reply")
                                is_sale_made = response.get("is_user_agree_to_buy")
                                is_decline = response.get("is_user_decline_to_buy")
                                is_reply_required = response.get('is_reply_required')
                                if not is_sale_made and is_reply_required and not is_decline:
                                    self.send_msg(message, recipient_username, recipient_urn, tracking_id)
                                    self.update_message_count(recipient_username)
                                elif is_decline:
                                    # user decline to buy
                                    logger.info(f"User decline to buy: {recipient_name}")
                                    break
                                else:
                                    # sale made
                                    logger.info(f"Sale made: {recipient_name}")
                                    break
                        continue
                    else:
                        if time.time() - inital_timer > settings.wait_time:
                            logger.info(f"Timeout for user: {recipient_name}")
                            break
            else:
                inital_msg = bot.generate_msg(recipient_name, recipient_headline)
                self.send_msg(inital_msg, recipient_username, recipient_urn, tracking_id)


    def parse_chat(self, chat, recipient_name):
        try:
            logger.debug("parsing chat history")
            history = {'me': [], recipient_name: [], "all": []}
            for message in chat.get("included"):
                sender = message.get("*sender")
                if sender is not None:
                    schema = {
                        "body": message.get("body").get("text"),
                        "timestamp": message.get("deliveredAt"),
                        "sender": message.get("*sender")
                    }
                    if self.own_urn.lower() in sender.lower():
                        history['me'].append(schema)
                    else:
                        history[recipient_name].append(schema)
                    history["all"].append(schema)
            return history
        except Exception as e:
            logger.error(e)


    @staticmethod
    def get_own_urn():
        try:
            logger.debug("Getting own urn")
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
            logger.debug(f"Dumping conversation urn for {recipient}")
            conversation_urn = self.get_conversation_urn(response)
            if self.db.contains(self.USER.recipient == recipient):
                logger.debug("conversation urn already exists")
                return
            self.db.insert({"recipient": recipient, "conversation_urn": conversation_urn})
            logger.debug(f"conversation urn added")
        except Exception as e:
            logger.error(e)


    def load_conversations(self):
        try:
            return self.db.all()
        except Exception as e:
            logger.error(e)


    def update_message_count(self, recipient):
        try:
            logger.debug(f"Updating message count for {recipient}")
            record = self.db.get(self.USER.recipient == recipient)
            message_count = record.get("message_count")
            if not message_count:
                # first time, count will not exist
                self.db.update({"message_count": 1}, self.USER.recipient == recipient)
                return
            self.db.update({"message_count": message_count + 1}, self.USER.recipient == recipient)
            logger.debug("Message count updated")
        except Exception as e:
            logger.error(e)


    def reached_user_limit(self, recipient):
        try:
            logger.debug("Checking user limit")
            record = self.db.get(self.USER.recipient == recipient)
            message_count = record.get("message_count")
            if not message_count:
                # first time, count will not exist
                return False
            if message_count >= settings.per_user_limit:
                return True
        except Exception as e:
            logger.error(e)


    def send_msg(self, message, recipient, recipientUrn, trackingId):
        try:
            logger.info(f"Sending message to {recipient}")
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
                logger.info(f"Message sent to {recipient}")
        except Exception as e:
            logger.error(e)


    def read_inbox(self, recipient):
        try:
            record = self.db.search(self.USER.recipient == recipient)
            if record:
                logger.info(f"Reading inbox for {recipient}")
                conversation_urn = quote(record[0].get("conversation_urn"))
                url = f"https://www.linkedin.com/voyager/api/voyagerMessagingGraphQL/graphql?queryId=messengerMessages.8d15783c080e392b337ba57fc576ad21&variables=(conversationUrn:{conversation_urn})"
                response = send_request(self.session, "GET", url, headers=build_headers(self.csrf_token, keyword=recipient))
                if response.status_code == 200:
                    logger.debug(f"Inbox read for {recipient}")
                    return response.json()
        except Exception as e:
            logger.error(e)


    def run(self):
        if not self.load_cookies():
            logger.debug("Cookies not found")
            self.login()
        if self.logged_in:
            logger.info("Starting crawler")
            self.db, self.USER = init_db()
            self.session = create_session(self.cookies)
            self.csrf_token = get_csrf_token(self.cookies)
            self.own_urn = self.get_own_urn()
            urls = load_urls()
            self.process_urls(urls)



