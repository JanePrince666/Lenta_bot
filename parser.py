import requests
from bs4 import BeautifulSoup as bs
import os.path
from channel_list import channel_list


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
    def __init__(self, url, start_post):
        if self.check_channel_doc(url):
            with open("channels/" + url[13:] + ".txt", "r") as f:
                self.channel_url, self.stub, self.last_post, self.posts_list = (i[:-1] for i in f.readlines())
                f.close()
                self.stub = self.stub
                self.posts_list = self.posts_list[:-1].split(", ")
                self.last_post = int(self.last_post)
        else:
            self.channel_url = url
            self.posts_list = []
            self.stub = TelegramPost(url + "/1").get_text()
            self.last_post = start_post
            with open("channels/" + url[13:] + ".txt", "w") as f:
                f.close()
            self.update_posts_list()

    @staticmethod
    def check_channel_doc(url):
        channel_name = url[13:]
        doc_name = "channels" + f"/{channel_name}" + ".txt"
        if os.path.exists(doc_name):
            return True
        else:
            return False

    def save_changes2doc(self):
        doc = "channels/" + self.channel_url[13:] + ".txt"

        if os.path.exists(doc):
            with open(doc, "w") as f:
                f.writelines(f"{self.channel_url}\n")
                f.writelines(f"{self.stub}\n")
                f.writelines(f"{self.last_post}\n")
                for i in self.posts_list:
                    f.writelines(f"{i}, ")
        else:
            print(f"no such doc: {doc}")

    def update_posts_list(self):
        post_list = []
        while all((i is not None for i in post_list)):
            post_list = []
            counter = self.last_post + 1
            for i in range(5):
                post_url = self.channel_url + f"/{counter}"
                post_text = TelegramPost(post_url).get_text()
                if post_text != self.stub and len(post_text) > 0:
                    self.posts_list.append(post_url)
                    self.last_post = counter
                    counter += 1
                else:
                    post_list.append(None)
                    counter += 1
        self.save_changes2doc()

    def get_last_post(self):
        post = TelegramPost(self.channel_url + f'/{self.last_post}')
        return post.get_url(), post.get_text()

    def get_posts_list(self):
        return self.posts_list


def get_latest_posts():
    for url, start_post in channel_list:
        channel = TelegramChannel(url, start_post)
        channel.update_posts_list()
        last = channel.get_last_post()
        yield last[0], last[1]

#
# for i in get_latest_posts():
#     print(i)
