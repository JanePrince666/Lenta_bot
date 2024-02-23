import datetime
import random
import re
import time
import requests
from bs4 import BeautifulSoup as bs
from tor_python_easy.tor_control_port_client import TorControlPortClient

from config import DATA_FOR_DATABASE, tor_pass
from db_management_OOP import ParsingChannels, PostingList
from profiler import time_of_function

tor_control_port_client = TorControlPortClient('localhost', 9051, tor_pass)
tor_control_port_client.change_connection_ip(seconds_wait=5)
proxy_config = {
    'http': 'socks5://localhost:9050',
    'https': 'socks5://localhost:9050',
}


def get_posts(url):
    response = requests.get(url, proxies=proxy_config)
    soup = bs(response.content, 'html.parser')
    posts = soup.find_all('div', class_="tgme_widget_message text_not_supported_wrap js-widget_message")
    return posts


@time_of_function
def pars_channel(url, last_post_number, first_launch):
    posts = get_posts(url)
    while len(posts) == 0:
        tor_control_port_client.change_connection_ip(seconds_wait=5)
        # print("Получила новый IP", file=open('report.txt', 'a'))
        posts = get_posts(url)
    last_post_number = last_post_number
    for post in posts:
        post_url_data = post['data-post']
        post_number = int(re.search('\/\d+', post_url_data).group()[1:])
        post_url = "https://t.me/" + post_url_data
        try:
            text = post.find_all('div', class_="tgme_widget_message_text js-message_text")[0].text
        except:
            text = ""
        # print(url, last_post_number, post_url_data, post_number)
        if post_number > last_post_number:
            last_post_number = post_number
            if not first_launch:
                PostingList(*DATA_FOR_DATABASE).add_to_posting_list(post_url, text)
    ParsingChannels(*DATA_FOR_DATABASE).change_channel_last_post(url, last_post_number)
