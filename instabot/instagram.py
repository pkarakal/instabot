import logging
from http.cookiejar import CookieJar
from datetime import datetime, timedelta
from time import sleep
from instabot.SpamDetectedException import SpamDetectedException
import requests
import json
import sys
import traceback
import secrets
import re


class Instagram:
    """
    A class used to represent an Instagram Web client

    ...
    Attributes
    ----------
    cookies: CookieJar
        a CookieJar object containing the cookies received
        and generated from instagram. Most notable cookie is
        csrf token used to identify the user, and session_id
    session: dict
        a dictionary containing the csrf token and session id
        in human readable form, after proper json decoding and
        obtaining keys from the cookies object
    tags: list
        a list containing the usernames to include in the comments
    emojis: list
        a list containing the usernames to include in the comments
    token: str
        a string that contains the csrf token if present in advance
    url: str
        a string that contains the endpoint to post the comment to
    logger: logger
        a logger object used to log activities to file

    Methods
    -------
    load(session)
        Loads a ready session in place of the existing one
    login(username, password)
        Uses the Instagram Web API to login the user and returns
        a tuple containing the session and the cookies.
    post_comment(post_id, comment, token, cookie_jar=None)
        Given a comment, post it to the correct endpoint using
        the Instagram Web API
    """

    def __init__(self, tag_list: list, emojis: list, number_of_tags: int, number_of_emojis:int,
                 authentication_token=None, logger: logging.Logger = None):
        """
        Initializes the Instagram object
        :param tag_list: a list that contains the usernames to
            include in the comments
        :param emojis: a list that contains the usernames to
            include in the comments
        :param number_of_tags: a number that indicates the
            the number of people to tag in a post
        :param number_of_emojis: a number that indicates the
            the number of emojis to put in a comment
        :param authentication_token: a string containing a pre-existing
            instagram csrf token.
        :param logger: a logger object
        """
        self.cookies = None
        self.session = None
        self.tags = tag_list
        self.emojis = emojis
        self.number_of_tags = number_of_tags
        self.number_of_emojis = number_of_emojis
        self.token = authentication_token
        self.url = None
        self.logger = logger

    def load(self, existing_session):
        self.session = existing_session

    def login(self, username: str, password: str) -> tuple:
        """
        This uses the Instagram Web API to login to instagram
        It makes a get request to the base instagram url to get
        an initial csrf token, so that is can proceed to the login.
        Note that `ig_cb` cookie is in place to make sure that cookies
        are accepted in the 'browser'. Then it encrypts the password
        in the same way it is encrypted on the web app. Finally, it posts
        to Instagram backend to get authenticated and updates the csrf
        token and the session id of the current session. It returns a dict
        containing the session and the cookies
        :param username: a string that contains the user's ig handle
        :param password: a string that contains the user's ig password
        :return: tuple containing a dict with csrf token and session id and
            the response cookies.
        """
        base_url = 'https://www.instagram.com/'
        url = base_url + 'accounts/login/'
        login_url = url + 'ajax/'
        USER_AGENT = 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0'

        time = int(datetime.now().timestamp())

        session = requests.Session()
        session.cookies.set("ig_cb", "2")
        session.headers = {'user-agent': USER_AGENT}
        session.headers.update({'Referer': base_url})

        response = session.get(base_url)
        csrftoken = None

        for key in response.cookies.keys():
            if key == 'csrftoken':
                csrftoken = session.cookies['csrftoken']
        session.headers.update({'X-CSRFToken': csrftoken})
        payload = {
            'username': username,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:{password}',
            'queryParams': {},
            'optIntoOneTap': 'false'
        }

        login_response = session.post(login_url, data=payload, allow_redirects=True)
        session.headers.update({'X-CSRFToken': login_response.cookies['csrftoken']})
        json_data = json.loads(login_response.text)

        if json_data["authenticated"]:
            self.cookies = login_response.cookies
            cookie_jar = self.cookies.get_dict()

            self.session = {
                "csrf_token": cookie_jar['csrftoken'],
                "session_id": cookie_jar['sessionid']
            }

            session.close()
            if self.logger is not None:
                self.logger.debug("Log in was successful and token was obtained")
            else:
                print("Log in was successful and token was obtained")

            return self.session, self.cookies.get_dict()
        session.close()
        raise Exception(login_response.text)

    def post_comment(self, post_id, comment, token, run_until: datetime = None,
                     comments_per_day: int = 500, cookie_jar: CookieJar = None):
        """
        This uses the Instagram Web API to post a comment to an IG Media.
        It constructs the correct url to post the data to, by setting the
        correct ig media id to a string. It then constructs the HTTP request
        headers and the data object. It finally uses requests to post the
        comment to Instagram. This runs until the datetime specified and posts
        a specified number of comments per day. When an error is raised it
        outputs the stack trace to the standard output.
        :param post_id: an int that contains the ig media id
        :param comment: a str that contains the comment to post
        :param token: a str containing the csrf token
        :param run_until: a datetime object that specifies the datetime to stop execution
        :param comments_per_day: an integer that indicates the number of comments to post per day
        :param cookie_jar: a CookieJar object. If None, it uses session.cookies
        :return: None
        """
        self.url = f"https://www.instagram.com/web/comments/{post_id}/add/"
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'X-CSRFToken': f'{token}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.instagram.com',
            'Connection': 'keep-alive',
        }
        data = f"comment_text={comment}"
        try:
            if run_until is not None:
                while (run_until - datetime.now()).total_seconds() >= 0:
                    response = requests.request("POST", self.url, data=data.encode('utf-8'), headers=headers,
                                                cookies=cookie_jar if cookie_jar is not None else self.cookies)
                    self.log(str(response.status_code) + " " + response.text)
                    # create a regex to find dates in YYYY-MM-DD format in the response.
                    # if found and the day difference is less than 7 days, sleep until then.
                    # else throw SpamDetected Exception. This can happen even when status code is 200.
                    regex_date = re.compile(r"\d{4}-(0?[1-9]|1[012])-(0?[1-9]|[12][0-9]|3[01])")
                    matches_date = regex_date.search(response.text)
                    if matches_date is not None:
                        date = datetime.fromisoformat(matches_date.group(0)) + timedelta(days=1)
                        diff = date - datetime.now()
                        if diff.days < 7:
                            self.log("Spam Detected. Sleeping for " + str(diff.total_seconds()))
                            sleep(diff.total_seconds())
                        else:
                            spam = SpamDetectedException(matches_date.group(0))
                            self.critical("Spam Detected Exception. Exiting", spam)
                            raise spam
                    # usually when a heavy activity is detected and spam is not detected, the response
                    # code is 429 and response message is the one in the regex below. If found, sleep
                    # for 5 minutes and continue program execution.
                    if response.status_code != 200:
                        regex = re.compile(r"^Please wait a few minutes before you try again.$")
                        matches = regex.search(response.text)
                        if matches is not None:
                            self.log("Sleeping for 300s")
                            sleep(300)
                    # to reach the specified number of comments per day, divide that number by seconds in a day
                    self.log("Sleeping for " + str(comments_per_day / (24 * 60)) + "s")
                    sleep(comments_per_day / (24 * 60))
                    new_comment = (" ".join(self.randomizeTags(self.number_of_tags)))
                    data = f"comment_text={new_comment}"
            else:
                requests.request("POST", self.url, data=data, headers=headers,
                                 cookies=cookie_jar if cookie_jar is not None else self.cookies)
        except Exception as e:
            self.critical("Critical exception thrown", e)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)

    def randomizeTags(self, number_of_tags: int = 3):
        """
        Given a int select random items from self.tags list
        using system randomness.
        :param number_of_tags:
        :return:
        """
        if self.tags is not None and number_of_tags < len(self.tags):
            sys_rand = secrets.SystemRandom()
            return sys_rand.sample(self.tags, number_of_tags)
        return None

    def randomizeEmojis(self, number_of_emojis: int = 2):
        """
            Given a int select random items from self.tags list
            using system randomness.
            :param number_of_emojis:
            :return:
        """
        if self.emojis is not None and number_of_emojis < len(self.tags):
            sys_rand = secrets.SystemRandom()
            return sys_rand.sample(self.emojis, number_of_emojis)
        return None

    def log(self, message: str):
        if self.logger is not None:
            self.logger.debug(message)
        else:
            print(message)

    def error(self, message: str, error: Exception):
        if self.logger is not None:
            self.logger.error(message, error)
        else:
            print(message, error)

    def critical(self, message: str, error: Exception):
        if self.logger is not None:
            self.logger.critical(message, error)
        else:
            print(message, error)


if __name__ == "__main__":
    insta = Instagram(tag_list=['@lorem', '@ipsum', '@dolor', '@sit', '@emet'])
    _comment = " ".join(insta.randomizeTags(2)).join(insta.randomizeEmojis(2))
    _session, cookie = insta.login("username", "password")
    insta.post_comment(post_id=1234, comment=_comment, token=_session.get('csrf_token'))
