import datetime
import random
import time
import requests
from bs4 import BeautifulSoup as bs

from config import DATA_FOR_DATABASE
from db_management_OOP import ParsingChannels, PostingList
from proxies import proxies
from profiler import time_of_function


def pars_page(url):
    proxy = dict([random.choice(proxies)])
    r = requests.get(url, proxies=proxy)
    soup = bs(r.text, "html.parser")
    is_tg_stub = str(soup.find_all(class_="tgme_page_description"))
    return soup, is_tg_stub


class TelegramPost:
    def __init__(self, channel_url, post_number):
        self.url = channel_url + f"/{post_number}"
        self.post_text = self.get_text()

    # @time_of_function
    def get_text(self):
        soup, is_tg_stub = pars_page(self.url)
        attempt_counter = 0
        while "If you have <strong>Telegram</strong>, you can contact" in is_tg_stub:
            soup, is_tg_stub = pars_page(self.url)
            attempt_counter += 1
            if attempt_counter == 5:
                break
        post_text = str(soup.find_all(property="og:description"))[16:-30]
        return post_text

    # @time_of_function
    def get_url(self):
        return self.url


class TelegramChannel:
    connection2ParsingChannels = ParsingChannels(*DATA_FOR_DATABASE)
    connection2PostingList = PostingList(*DATA_FOR_DATABASE)

    def __init__(self, url, stub, start_post=50):
        self.channel_url = url
        self.last_post = start_post
        self.stub = stub

    # @staticmethod
    def check_channel_doc(self, url):
        return len(self.connection2ParsingChannels.select_channel_data(url)) > 0

    # # @time_of_function
    # def check_new_posts(self, first_launch):
    #     is_post = True
    #     counter = self.last_post
    #     while is_post:
    #         is_post = False
    #         for i in range(10):
    #             counter += 1
    #             post = TelegramPost(self.channel_url, counter)
    #             post_text = post.post_text
    #             if post_text != self.stub and len(post_text) > 0:
    #                 self.last_post = counter
    #                 is_post = True
    #                 ParsingChannels(*DATA_FOR_DATABASE).change_channel_last_post(self.channel_url, self.last_post)
    #                 if not first_launch:
    #                     PostingList(*DATA_FOR_DATABASE).add_to_posting_list(post, post_text)
    #     # print(f"процесс проверки канала {self.channel_url} закончен в {datetime.datetime.now()}", file=open('report.txt', 'a'))

    def change_channel_stub(self):
        stub = TelegramPost(self.channel_url, 1).post_text
        ParsingChannels(*DATA_FOR_DATABASE).change_channel_stub(stub)
        self.last_post -= 10
        self.update_parsing_channels_table()

    def update_parsing_channels_table(self):
        ParsingChannels(*DATA_FOR_DATABASE).change_channel_last_post(self.channel_url, self.last_post)

    def check_new_posts(self, first_launch):
        is_post = True
        is_post_number = self.last_post + 1
        retry_counter = 0
        previous_post_text = ""
        for_posting = []
        while is_post:
            is_post = False
            ten_posts = (TelegramPost(self.channel_url, is_post_number + i) for i in range(10))
            for post in ten_posts:
                post_text = post.post_text
                if post_text == self.stub:
                    continue
                elif previous_post_text == post_text and len(post_text) > 0:
                    retry_counter += 1
                    continue
                elif len(post_text) > 0:
                    self.last_post = is_post_number
                    is_post = True
                    for_posting.append([post, post_text])
                previous_post_text = post_text
            if retry_counter > 8:
                self.change_channel_stub()
        self.update_parsing_channels_table()
        if not first_launch:
            for post, post_text in for_posting:
                PostingList(*DATA_FOR_DATABASE).add_to_posting_list(post, post_text)
        print(f"процесс проверки канала {self.channel_url} закончен в {datetime.datetime.now()}", file=open('report.txt', 'a'))
