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

# Настройка прокси-сервера для обхода блокировок и анонимного доступа к веб-ресурсам.
tor_control_port_client = TorControlPortClient('localhost', 9051, tor_pass)

# Устанавливаем соединение с Tor Control Port и меняем IP-адрес через Tor каждые 5 секунд.
tor_control_port_client.change_connection_ip(seconds_wait=5)

# Задаем конфигурацию прокси-сервера для использования SOCKS5 прокси на локальном хосте и
# порту 9050 для HTTP и HTTPS запросов.
proxy_config = {
    'http': 'socks5://localhost:9050',
    'https': 'socks5://localhost:9050',
}


# Функция для получения HTML-кода веб-страницы 
def get_html(url: str):
    """
    return BeautifulSoup object by url
    
    :type url: str
    :return object
    """
    try:
        response = requests.get(url, proxies=proxy_config)
        soup = bs(response.content, 'html.parser')
        return soup
    except:
        print("Не удалось получить html")


def check_on_stub(url: str):
    """
    checks whether the received page is a telegram stub

    :type url: str
    :return object, bool
    """
    soup = get_html(url)
    try:
        if soup.find('div', class_="tgme_page_additional"):
            return False
        else:
            return soup
    except:
        return False


# Функция для извлечения постов из HTML-кода веб-страницы.
def get_posts(url: str):
    """
    returns posts found on the channel page as a list

    :type url: str
    :return list, bool
    """
    soup = check_on_stub(url)
    if soup:
        posts = soup.find_all('div', class_="tgme_widget_message text_not_supported_wrap js-widget_message")
        return posts
    else:
        return False


# Функция парсинга канала
# @time_of_function
def pars_channel(url: str, last_post_number: int, first_launch: bool):
    """
    function of parsing Telegram channel . The result of the work is reflected in the database

    :param url: str
    :param last_post_number: int
    :type first_launch: bool
    """
    # Извлекает посты с канала, используя функцию get_posts.
    posts = get_posts(url)
    attempt_counter = 0

    # Повторяет попытки получения постов, меняя IP-адрес через Tor при неудачных попытках.
    while not posts:
        attempt_counter += 1
        tor_control_port_client.change_connection_ip(seconds_wait=5)
        # print("Получила новый IP", file=open('report.txt', 'a'))
        posts = get_posts(url)
        if attempt_counter > 5:
            print("Ошибка при подключении к Тору")
    last_post_number = last_post_number

    # Проверяет каждый пост на наличие новой информации и обновляет последний номер поста для канала.
    for post in posts:
        post_url_data = post['data-post']
        post_number = int(re.search('\/\d+', post_url_data).group()[1:])
        post_url = "https://t.me/" + post_url_data
        try:
            text = post.find_all('div', class_="tgme_widget_message_text js-message_text")[0].text
        except:
            text = ""

        # При обнаружении нового поста, добавляет его в список для публикации для подписчиков канала,
        # если это не первый запуск бота и если есть каналы, которые подписаны на данный телеграм канал
        if post_number > last_post_number:
            last_post_number = post_number
            subscribed_user_channels = MonitoredTelegramChannels(
                *DATA_FOR_DATABASE).get_user_channels_subscribed_on_tg_channel(url)
            if not first_launch and len(subscribed_user_channels) > 0:
                for user_channel in subscribed_user_channels:
                    PostingList(*DATA_FOR_DATABASE).add_to_posting_list(post_url, text, user_channel)
    ParsingChannels(*DATA_FOR_DATABASE).change_channel_last_post(url, last_post_number)


# Функция для получения списка каналов.
def get_channel_lisl() -> list[str]:
    """
    return generator for get_new_posts

    :rtype: list[str]
    """
    connection = ParsingChannels(*DATA_FOR_DATABASE)
    channel_list = connection.get_channels_list()

    # Разделяет список каналов на подсписки по 20 элементов и возвращает
    # их по одному при каждом вызове функции с помощью генератора.
    for i in range(0, len(channel_list), 20):
        unit = channel_list[i:i + 20]
        yield unit


# Функция для получения новых постов с каналов.
def get_new_posts():
    first_launch = True # Устанавливает флаг первого запуска в True.

    # Бесконечный цикл для обработки новых постов.
    while True:
        channels = get_channel_lisl()
        for unit in channels:

            # Для каждого из 20 канала запускает параллельный процесс парсинга постов с указанием URL канала,
            # номера последнего поста и флага первого запуска.
            for url, start_post in unit:
                t = multiprocessing.Process(target=pars_channel, args=(url, start_post, first_launch,))
                t.start()

            # После обработки 20 каналов ждет 10 секунд, чтобы не запускалось бесконечное количество
            # процессов одновременно. Затем продолжает.
            time.sleep(10)

        # После завершения парсинга каналов в первый раз полностью устанавливая флаг первого запуска в False.
        first_launch = False
