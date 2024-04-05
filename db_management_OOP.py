import mysql.connector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MySQL:
    # @time_of_function
    def __init__(self, host: str, port: int, user: str, password: str, db_name: str) -> object:
        """
        creates a connection to the database

        """
        try:
            self.connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=db_name
            )
            # logger.info("Успешное подключение к базе данных.")
        except mysql.connector.Error as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")

    def do_commit(self, new_data):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(new_data)
                self.connection.commit()
                # logger.info("Успешное добавление в базу данных.")
        except Exception as e:
            logger.error(f"Ошибка добавления в базу данных: {e}")

    def get_data_from_database(self, inquiry):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(inquiry)
                # logger.error(f"Успешное получение данных из базы данных")
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка получения данных из базы данных: {e}")

    def __del__(self):
        """
        closes a database connection when it is no longer needed
        """
        try:
            self.connection.close()
        except Exception as e:
            logger.error(f"Ошибка закрытия базы данных: {e}")

        # self.connection.close()


class ParsingChannels(MySQL):

    # @time_of_function
    def create_new_channel(self, url: str, last_post_number: int, name: str):
        """
        creates a new channel in the ParsingChannel table

        :param name:
        :param url: telegram channel url
        :param last_post_number: int
        """
        if type(url) != str or len(url) == 0 or len(name) == 0 or type(last_post_number) != int:
            return "Ошибка при получении данных"
        if not self.check_url(url):
            insert_query = (f"INSERT INTO `ParsingChannels` (url, last_post_number, channel_name) "
                            f"VALUES ('{url}', '{last_post_number}', '{name}') ")
            self.do_commit(insert_query)
            return "Добавила!"

    # @time_of_function
    def select_channel_data(self, url: str):
        """
        returns data about the channel by its url

        :type url: str
        :return list(tuple(tg_channel_data))
        """
        select_channel_rows = (f"SELECT url, last_post_number FROM `ParsingChannels`"
                               f"WHERE url = '{url}' ")
        rows = self.get_data_from_database(select_channel_rows)
        return rows

    # @time_of_function
    def check_url(self, url: str):
        """
        checks the presence of a channel in the database

        :type url: str
        """
        return len(self.select_channel_data(url)) > 0

    # @time_of_function
    def change_channel_last_post(self, url: str, new_data: int):
        """
        updates the number of the last post for the telegram channel

        :param new_data: int
        :type url: str
        """
        if self.check_url(url):
            change_query = f"UPDATE `ParsingChannels` SET last_post_number = '{new_data}' WHERE url = '{url}' "
            self.do_commit(change_query)

    def change_channel_name(self, url: str, new_data: str):
        if self.check_url(url):
            change_query = f"UPDATE `ParsingChannels` SET channel_name = '{new_data}' WHERE url = '{url}' "
            self.do_commit(change_query)

    # @time_of_function
    def get_last_post_number(self, url: str):
        """
        returns the telegram channel last_post_number by url

        :type url: str
        """
        if self.check_url(url):
            select_channel_last_post_number = (f"SELECT last_post_number FROM `ParsingChannels`"
                                               f"WHERE url = '{url}' ")
            number = self.get_data_from_database(select_channel_last_post_number)[0][0]
            return number

    def get_channel_name(self, url: str):
        """
        returns the telegram channel name by url

        :type url: str
        """
        if self.check_url(url):
            select_channel_name = (f"SELECT channel_name FROM `ParsingChannels`"
                                   f"WHERE url = '{url}' ")
            name = self.get_data_from_database(select_channel_name)[0][0]
            return name

    # @time_of_function
    def get_channels_list(self):
        """
        returns a list of a list of all telegram channels in the database

        :return: generator(tuple(tg_channel_data))
        """
        select_all_channel = f"SELECT url, last_post_number FROM `ParsingChannels` "
        channels = [i for i in self.get_data_from_database(select_all_channel)]
        return channels


class Users(MySQL):

    def add_user_and_user_channel(self, user_id: int, user_channel_id: int, channel_name: str):
        """
        adds the user and his channels for posting to the users table

        :param user_id: int
        :param channel_name: str
        :param user_channel_id: int
        """
        insert_query = f"INSERT INTO `users` (user_channel_id, user_id, channel_name) VALUES ({user_channel_id}, '{user_id}', '{channel_name}')"
        self.do_commit(insert_query)

    def get_user_channels(self, user_id: int):
        """
        return list of tuple of user_channel_id and channel_name
        :type user_id: int
        :return: list(tuple)
        """
        select_all_user_channels = f"SELECT user_channel_id, channel_name FROM `users` WHERE user_id = {user_id}"
        user_channels = [i for i in self.get_data_from_database(select_all_user_channels)]
        return user_channels

    def del_user_channel(self, channel_id: int):
        """
        delite the user channel for posting from the users table

        :param channel_id: int
        """
        delete_query = f"DELETE FROM `users` WHERE user_channel_id = {channel_id}"
        self.do_commit(delete_query)

    def del_user(self, user_id: int):
        """
        delite the user and his channels for posting from the users table

        :type user_id: int
        """
        delete_query = f"DELETE FROM `users` WHERE user_id = {user_id}"
        self.do_commit(delete_query)


class PostingList(MySQL):

    # @time_of_function
    def add_to_posting_list(self, url: str, text: str, user_channel: int):
        """
        adds a post to the posting database table

        :param text: str        :type url:
        """
        insert_query = f"INSERT INTO `posting_list` (post_url, post_text, user_channel_id) VALUES ('{url}', '{text}', {user_channel}) "
        self.do_commit(insert_query)

    def get_posting_list(self):
        """
        returns a list of posts that need to be posted

        :return: list(tuple(str))
        """
        data = f"SELECT post_url, post_text, user_channel_id FROM `posting_list` "
        rows = self.get_data_from_database(data)
        return rows

    def del_from_posting_list(self, post_url):
        """
        deletes a post from the posting database table by its url

        :type post_url: str
        """
        delete_query = f"DELETE FROM `posting_list` WHERE post_url = '{post_url}' "
        self.do_commit(delete_query)


class MonitoredTelegramChannels(MySQL):
    def add_to_monitored(self, url: str, channel_id: int):
        """
        Adds the URL of the Telegram channel to the list of monitored channels for the specified user channel.

        :param url: str
        :type channel_id: int
        """
        monitored_channels = self.get_subscribed_user_chanel_list(channel_id)
        if url in monitored_channels:
            return "Уже в канале"
        else:
            insert_query = f"INSERT INTO `monitored_telegram_channels` (user_channel_id, tg_channel_url) VALUES ({channel_id}, '{url}')"
            self.do_commit(insert_query)
            return "Добавила"

    def get_subscribed_user_chanel_list(self, user_channel_id: int):
        """
        return list of urls of telegram channels, subscribed on user channel/chat
        :type user_channel_id: int
        :return list[str]
        """
        data = (f"SELECT tg_channel_url FROM `monitored_telegram_channels` "
                f"WHERE user_channel_id = {user_channel_id} ")

        return [item[0] for item in self.get_data_from_database(data)]

    def get_user_channels_subscribed_on_tg_channel(self, tg_channel_url: str):
        """
        return list of user's channels id that subscribed on monitored telegram channel

        :type tg_channel_url: str
        :return list[float]
        """
        data = (f"SELECT user_channel_id FROM `monitored_telegram_channels` "
                f"WHERE tg_channel_url = '{tg_channel_url}' ")
        return [item[0] for item in self.get_data_from_database(data)]

    def del_from_monitored(self, user_channel_id: int):
        """
        delite user channel and all it's subscription

        :type user_channel_id: int
        """
        delete_query = f"DELETE FROM `monitored_telegram_channels` WHERE user_channel_id = '{user_channel_id}'"
        self.do_commit(delete_query)

    def del_tg_channel_from_monitored(self, user_channel_id: int, tg_channel_url: int):
        """
        delite telegram channel from monitored channels

        :param user_channel_id: int
        :type tg_channel_url: str
        """
        delete_query = (f"DELETE FROM `monitored_telegram_channels` WHERE user_channel_id = '{user_channel_id}'"
                        f"AND tg_channel_url = '{tg_channel_url}'")
        self.do_commit(delete_query)
