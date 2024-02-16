import requests
from bs4 import BeautifulSoup as bs
from db_management_OOP import connection


class TelegramPost:
    def __init__(self, url):
        self.url = url

    def get_text(self):
        r = requests.get(self.url)
        soup = bs(r.text, "html.parser")
        post_text = str(soup.find_all(property="og:description"))[16:-30]
        return post_text

    def get_url(self):
        return self.url


class TelegramChannel:
    def __init__(self, url, start_post=50):
        if self.check_channel_doc(url):
            self.channel_url, self.stub, self.last_post = connection.select_channel_data(url)[0]
        else:
            self.channel_url = url
            self.stub = TelegramPost(url + "/1").get_text()
            self.last_post = start_post
            connection.create_new_channel(self.channel_url, self.stub, self.last_post)

    @staticmethod
    def check_channel_doc(url):
        return len(connection.select_channel_data(url)) > 0

    def check_new_posts(self):
        post_list = []
        counter = self.last_post + 1
        for i in range(10):
            post_url = self.channel_url + f"/{counter}"
            post_text = TelegramPost(post_url).get_text()
            if post_text != self.stub and len(post_text) > 0:
                self.last_post = counter
                post_list.append(True)
                connection.change_channel_last_post(self.channel_url, self.last_post)
                yield post_url
                counter += 1
            else:
                post_list.append(None)
                counter += 1
        if any((i is not None for i in post_list)):
            self.check_new_posts()
