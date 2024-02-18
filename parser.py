import time
import requests
from bs4 import BeautifulSoup as bs

from config import DATA_FOR_DATABASE
from db_management_OOP import ParsingChannels, PostingList
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
    connection2ParsingChannels = ParsingChannels(*DATA_FOR_DATABASE)
    connection2PostingList = PostingList(*DATA_FOR_DATABASE)

    def __init__(self, url, start_post=50):
        if self.check_channel_doc(url):
            self.channel_url, self.stub, self.last_post = self.connection2ParsingChannels.select_channel_data(url)[0]
        else:
            self.channel_url = url
            self.last_post = start_post
            self.stub = TelegramPost(url, start_post).post_text
            self.connection2ParsingChannels.create_new_channel(self.channel_url, self.stub, self.last_post)

    # @staticmethod
    def check_channel_doc(self, url):
        return len(self.connection2ParsingChannels.select_channel_data(url)) > 0

    # @time_of_function
    def check_new_posts(self, first_launch=True):
        is_post = True
        counter = self.last_post
        while is_post:
            is_post = False
            for i in range(10):
                counter += 1
                post = TelegramPost(self.channel_url, counter)
                post_text = post.post_text
                if post_text != self.stub and len(post_text) > 0:
                    self.last_post = counter
                    is_post = True
                    ParsingChannels(*DATA_FOR_DATABASE).change_channel_last_post(self.channel_url, self.last_post)
                    if first_launch:
                        PostingList(*DATA_FOR_DATABASE).add_to_posting_list(post, post_text)
