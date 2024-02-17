import requests
# noinspection PyPep8Naming
from bs4 import BeautifulSoup as bs
from db_management_OOP import connection


class TelegramPost:
    def __init__(self, channel_url, post_number):
        self.url = channel_url + f"/{post_number}"

    def get_text(self):
        r = requests.get(self.url)
        soup = bs(r.text, "html.parser")
        post_text = str(soup.find_all(property="og:description"))[16:-30]
        return post_text

    def get_url(self):
        return self.url


def check_new_posts(channel_url, last_post):
    stub = connection.get_channel_stub(channel_url)
    is_post = False
    counter = last_post + 1
    for i in range(10):
        post = TelegramPost(channel_url, counter)
        post_text = post.get_text()
        if post_text != stub and len(post_text) > 0:
            last_post = counter
            is_post = True
            connection.change_channel_last_post(channel_url, last_post)
            yield post
            counter += 1
        else:
            counter += 1
    if is_post:
        check_new_posts(channel_url, last_post)
