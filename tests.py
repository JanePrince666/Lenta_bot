import datetime
import multiprocessing
import random
import re
import time

import requests
from bs4 import BeautifulSoup as bs
from tor_python_easy.tor_control_port_client import TorControlPortClient
from tor_python_easy.tor_socks_get_ip_client import TorSocksGetIpClient
from config import DATA_FOR_DATABASE
from db_management_OOP import ParsingChannels, PostingList



# from profiler import time_of_function


proxy_config = {
        'http': 'socks5://localhost:9050',
        'https': 'socks5://localhost:9050'}
ip_client = TorSocksGetIpClient(proxy_config)
tor_control_port_client = TorControlPortClient('localhost', 9051, 'PrinceoFhalfblood3264')

# for it in range(10):
#     old_ip = ip_client.get_ip()
#     tor_control_port_client.change_connection_ip(seconds_wait=15)
#     new_ip = ip_client.get_ip()
#     print(f'iteration {it + 1} ::  {old_ip} -> {new_ip}')
#
#
# @time_of_function
# def get_new_ip():
#     for it in range(10):
#         old_ip = ip_client.get_ip()
#
#
# get_new_ip()


# def get_text(url):
#         response = requests.get(url)
#         soup = bs(response.content, 'html.parser')
#         posts = soup.find_all('div', class_="tgme_widget_message text_not_supported_wrap js-widget_message")
#         for post in posts:
#                 post_url = post['data-post']
#                 post_number = int(re.search('\d+', post_url).group())
#                 post_url = "https://t.me/"+post_url
#                 text = post.find_all('div', class_="tgme_widget_message_text js-message_text")[0].text
#                 print(f"{post_number}\n{post_url}\n{text}\n{30*'-'}")
#
# get_text('https://t.me/s/rusbrief')

def get_posts(url):
    response = requests.get(url, proxies=proxy_config)
    soup = bs(response.content, 'html.parser')
    posts = soup.find_all('div', class_="tgme_widget_message text_not_supported_wrap js-widget_message")
    return posts


def pars_channel(url, last_post_number, first_launch):
    posts = get_posts(url)
    while len(posts) == 0:
        tor_control_port_client.change_connection_ip(seconds_wait=5)
        posts = get_posts(url)
    last_post_number = last_post_number
    text = ""
    post_url = ""
    for post in posts:
        post_url_data = post['data-post']
        post_number = int(re.search('\/\d+', post_url_data).group()[1:])
        post_url = "https://t.me/" + post_url_data
        text = post.find_all('div', class_="tgme_widget_message_text js-message_text")[0].text
        if post_number > last_post_number:
            last_post_number = post_number
            if not first_launch:
                PostingList(*DATA_FOR_DATABASE).add_to_posting_list(post_url, text)
    ParsingChannels(*DATA_FOR_DATABASE).change_channel_last_post(url, last_post_number)


pars_channel('https://t.me/s/adm_gelen', 11862, first_launch=False)
