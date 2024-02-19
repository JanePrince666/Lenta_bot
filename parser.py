import datetime
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
        return post_text

    # @time_of_function
    def get_url(self):
        return self.url


class TelegramChannel:

    def __init__(self, url, start_post=50):
        # if self.check_channel_doc(url):
        #     self.channel_url, self.stub, self.last_post = self.connection2ParsingChannels.select_channel_data(url)[0]
        # else:
        self.channel_url = url
        self.last_post = start_post
        self.stub = TelegramPost(url, 1).post_text
        self.connection2ParsingChannels.create_new_channel(self.channel_url, self.stub, self.last_post)

    # @staticmethod
    def check_channel_doc(self, url):
        return len(self.connection2ParsingChannels.select_channel_data(url)) > 0

    # @time_of_function
    def check_new_posts(self, first_launch):
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
                    # self.connection2ParsingChannels.change_channel_last_post(self.channel_url, self.last_post)
                    if not first_launch:
                        PostingList(*DATA_FOR_DATABASE).add_to_posting_list(post, post_text)
                        # self.connection2PostingList.add_to_posting_list(post, post_text)
        # print(f"процесс проверки канала {self.channel_url} закончен в {datetime.datetime.now()}")

# что-нибудь
