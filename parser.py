import requests
import asyncio
from bs4 import BeautifulSoup as bs
from db_management_OOP import connection
from profiler import time_of_function


# async def get_text(url):
#     r = requests.get(url)
#     soup = bs(r.text, "html.parser")
#     post_text = str(soup.find_all(property="og:description"))[16:-30]
#     return post_text


class TelegramPost:
    def __init__(self, channel_url, post_number):
        self.post_text = None
        self.url = channel_url + f"/{post_number}"
        # self.post_text = None

    # @time_of_function
    async def get_text(self):
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
            self.stub = None

    async def get_stub(self):
        self.stub = await TelegramPost(self.channel_url, 1).get_text()
        return self.stub

    @staticmethod
    def check_channel_doc(url):
        return len(connection.select_channel_data(url)) > 0

    # @time_of_function
    async def check_new_posts(self):
        is_post = True
        counter = self.last_post + 1
        while is_post:
            is_post = False
            for i in range(10):
                post = TelegramPost(self.channel_url, counter)
                post_text = await post.get_text()
                if post_text != self.stub and len(post_text) > 0:
                    self.last_post = counter
                    is_post = True
                    connection.change_channel_last_post(self.channel_url, self.last_post)
                    connection.add_to_posting_list(post, post_text)
                    counter += 1
                else:
                    counter += 1


# print(asyncio.run(get_text("https://t.me/Ateobreaking/111948")))
# a = TelegramChannel("https://t.me/komcitynews", 46748).get_stub()
# print(a.stub)
