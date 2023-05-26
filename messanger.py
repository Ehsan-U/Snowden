
""" Handle Linkedin Messaging """

from session_manager import SessionManager
from utils import *
import settings
from logging_config import logger


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
                response = send_request(self.session, 'POST', modified_url, headers=build_headers(self.csrf_token))
                recipientUrn = self.get_recipientUrn(response)
                trackingId = self.get_trackingID(recipientUrn, username)
                self.send_msg(username, recipientUrn, trackingId)
        except Exception as e:
            logger.error(e)


    def get_own_urn(self):
        try:
            logger.info(" [+] Getting own urn")
            with open("data/user_data.json", 'r') as f:
                urn = json.load(f).get('user_urn')
            return urn
        except Exception as e:
            logger.error(e)


    def send_msg(self, username, recipientUrn, trackingId):
        try:
            logger.info(f" [+] Sending message to {username}")
            url = 'https://www.linkedin.com/voyager/api/voyagerMessagingDashMessengerMessages?action=createMessage'
            headers = build_headers(self.csrf_token, keyword=username)
            del headers['X-Li-Pem-Metadata']
            data = deepcopy(settings.MSG_PAYLOAD)
            data['message']['body']['text'] = settings.MESSAGE
            data['message']['originToken'] = generate_token()
            data['mailboxUrn'] = self.own_urn
            data['trackingId'] = trackingId
            data['hostRecipientUrns'] = [recipientUrn]
            response = send_request(self.session ,"POST", url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                logger.info(f" [+] Message sent to {username}")
        except Exception as e:
            logger.error(e)


    def crawl(self):
        if not self.load_cookies():
            logger.info(" [+] Cookies not found")
            self.login()
        if self.logged_in:
            logger.info(" [+] Starting crawler")
            self.session = create_session(self.cookies)
            self.csrf_token = get_csrf_token(self.cookies)
            self.own_urn = self.get_own_urn()
            urls = load_urls()
            self.process_urls(urls)


scraper = Messanger()
scraper.crawl()


