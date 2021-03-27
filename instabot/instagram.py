import requests
import json
from datetime import datetime
import requests_html


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
    token: str
        a string that contains the csrf token if present in advance
    url: str
        a string that contains the endpoint to post the comment to

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
    def __init__(self, tag_list: list, authentication_token=None):
        """
        Initializes the Instagram object
        :param tag_list: a list that contains the usernames to
            include in the comments
        :param authentication_token: a string containing a pre-existing
            instagram csrf token.
        """
        self.cookies = None
        self.session = None
        self.tags = tag_list
        self.token = authentication_token
        self.url = None

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

            return self.session
        session.close()
        raise Exception(login_response.text)


if __name__ == "__main__":
    insta = Instagram()
    res = insta.login("username", "password")
