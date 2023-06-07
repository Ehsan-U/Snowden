
""" Manage user session """

import os
from playwright.sync_api import sync_playwright
import json
import time
from linkedin_ai.logging_config import logger
import re


class SessionManager():
    login_url = 'https://www.linkedin.com/login'
    logged_in = False


    def init_playwright(self) -> None:
        self.play = sync_playwright().start()
        browser = self.play.firefox.launch_persistent_context(headless=False, user_data_dir="./user_data_dir")
        self.page = browser.pages[0]

    def reshape_cookies(self, cookies: list[dict]) :
        if cookies:
            logger.debug("Reshaping cookies")
            request_cookies = {}
            for cookie in cookies:
                name = cookie['name']
                del cookie['name']
                value = cookie['value']
                del cookie['value']
                cookie[name] = value
                request_cookies.update(cookie)
            request_cookies = {k:str(v) for k,v in request_cookies.items()}
            return request_cookies
        else:
            return None

    def load_cookies(self) -> bool:
        if os.path.exists("data/cookies.json"):
            with open("data/cookies.json", 'r') as f:
                self.cookies = self.reshape_cookies(json.load(f))
                self.logged_in = True
                logger.debug("Cookies loaded!")
                return True
        else:
            return False

    def save_cookies(self, cookies: list[dict], user_id: str, user_urn: str) -> None:
        with open("data/cookies.json", 'w') as f:
            json.dump(cookies, f)
            logger.debug("Cookies saved")
        with open('data/user_data.json', 'w') as f:
            json.dump({"user": user_id.split('/')[-2], "user_urn": user_urn}, f)


    def login(self) -> None:
        try:
            self.init_playwright()
            self.page.goto(self.login_url)
            input("Compelete login and press enter:")
        except Exception as e:
            logger.error(e)
        else:
            cookies = self.page.context.cookies()
            time.sleep(1)
            user_id = self.page.locator("//a[contains(@href, '/in/') and @class='ember-view block']").get_attribute('href')
            user_urn = re.search('urn\:li\:fsd_profile.*?\"', self.page.content()).group()
            self.save_cookies(cookies, user_id, user_urn)
            self.play.stop()

