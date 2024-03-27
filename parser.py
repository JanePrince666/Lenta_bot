import datetime
import re
import time
import requests
import multiprocessing
from bs4 import BeautifulSoup as bs
from tor_python_easy.tor_control_port_client import TorControlPortClient

from config import DATA_FOR_DATABASE, tor_pass
from db_management_OOP import ParsingChannels, PostingList, MonitoredTelegramChannels
from profiler import time_of_function

tor_control_port_client = TorControlPortClient('localhost', 9051, tor_pass)
tor_control_port_client.change_connection_ip(seconds_wait=5)
proxy_config = {
    'http': 'socks5://localhost:9050',
    'https': 'socks5://localhost:9050',
}


def get_html(url):
    try:
        response = requests.get(url, proxies=proxy_config)
        soup = bs(response.content, 'html.parser')
        return soup
    except:
        print("Не удалось получить html")


def check_on_stub(url):
    soup = get_html(url)
    try:
        if soup.find('div', class_="tgme_page_additional"):
            return False
        else:
            return soup
    except:
        return False


def get_posts(url):
    soup = check_on_stub(url)
    if soup:
        posts = soup.find_all('div', class_="tgme_widget_message text_not_supported_wrap js-widget_message")
        return posts
    else:
        return False


# @time_of_function
def pars_channel(url, last_post_number, first_launch):
    posts = get_posts(url)
    attempt_counter = 0
    while not posts:
        attempt_counter += 1
        tor_control_port_client.change_connection_ip(seconds_wait=5)
        # print("Получила новый IP", file=open('report.txt', 'a'))
        posts = get_posts(url)
        if attempt_counter > 5:
            print("Ошибка при подключении к Тору")
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
            subscribed_user_channels = MonitoredTelegramChannels(*DATA_FOR_DATABASE).get_user_channels_subscribed_on_tg_channel(url)
            if not first_launch and len(subscribed_user_channels) > 0:
                for user_channel in subscribed_user_channels:
                    PostingList(*DATA_FOR_DATABASE).add_to_posting_list(post_url, text, user_channel)
    ParsingChannels(*DATA_FOR_DATABASE).change_channel_last_post(url, last_post_number)


def get_channel_lisl():
    connection = ParsingChannels(*DATA_FOR_DATABASE)
    channel_list = connection.get_channels_list()
    for i in range(0, len(channel_list), 20):
        unit = channel_list[i:i + 20]
        yield unit


def get_new_posts():
    first_launch = True
    # print("начала парсить")
    while True:
        # start = datetime.datetime.now()
        channels = get_channel_lisl()
        for unit in channels:
            for url, start_post in unit:
                # time.sleep(random.randint(0,5))
                # print(f"проверка канала {url} начата в {datetime.datetime.now()}", file=open('report.txt', 'a'))
                t = multiprocessing.Process(target=pars_channel, args=(url, start_post, first_launch,))
                t.start()
            # print(f"Отсечка в unit {datetime.datetime.now()}", file=open('report.txt', 'a'))
            # print(f"проверка канала {url} закончена в {datetime.datetime.now()}", file=open('report.txt', 'a'))
            # if first_launch:
            #     time.sleep(120)
            # else:
            time.sleep(10)
        # end = datetime.datetime.now()
        # print(f"{50*'-'}\nпроверка каналов закончена в {datetime.datetime.now()}\n общее время: {end-start}\n{50*'-'}", file=open('report.txt', 'a'))
        first_launch = False
        # end = datetime.datetime.now()
        # print(f'цикл get_new_posts:\n   start: {start}\n    finish: {end}\n    Время работы ' + str(end - start), file=open('report.txt', 'a'))
