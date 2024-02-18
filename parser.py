import time
import requests
from bs4 import BeautifulSoup as bs

from config import db_host, db_user_name, db_password
from db_management_OOP import connection, MySQL
from profiler import time_of_function


class TelegramPost:
    def __init__(self, channel_url, post_number):
        self.url = channel_url + f"/{post_number}"
        self.post_text = self.get_text()

    # @time_of_function
    def get_text(self):
        r = requests.get(self.url)
        soup = bs(r.text, "html.parser")
        post_text = str(soup.find_all(property="og:description"))[16:-30]
        self.post_text = post_text
        return self.post_text

    # @time_of_function
    def get_url(self):
        return self.url


class TelegramChannel:
    def __init__(self, url, start_post=50):
        if self.check_channel_doc(url):
            self.channel_url, self.stub, self.last_post = connection.select_channel_data(url)[0]
        else:
            self.channel_url = url
            self.last_post = start_post
            self.stub = TelegramPost(url, start_post)

    @staticmethod
    def check_channel_doc(url):
        return len(connection.select_channel_data(url)) > 0

    # @time_of_function
    def check_new_posts(self):
        is_post = True
        connection1 = MySQL(db_host, db_user_name, db_password, "lenta_db")
        counter = connection1.select_channel_data(self.channel_url)[0][2]
        while is_post:
            is_post = False
            for i in range(10):
                counter += 1
                post = TelegramPost(self.channel_url, counter)
                post_text = post.post_text
                if post_text != self.stub and len(post_text) > 0:
                    self.last_post = counter
                    is_post = True
                    connection1.change_channel_last_post(self.channel_url, self.last_post)
                    connection1.add_to_posting_list(post, post_text)
            time.sleep(1)
