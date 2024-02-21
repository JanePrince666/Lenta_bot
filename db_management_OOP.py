import mysql.connector
from config import DATA_FOR_DATABASE
from profiler import time_of_function


class MySQL:
    # @time_of_function
    def __init__(self, host: str, user: str, password: str, db_name: str) -> object:
        """
        creates a connection to the database

        """
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )

    def do_commit(self, new_data):
        with self.connection.cursor() as cursor:
            cursor.execute(new_data)
            self.connection.commit()

    def get_data_from_database(self, inquiry):
        with self.connection.cursor() as cursor:
            cursor.execute(inquiry)
            return cursor.fetchall()

    def __del__(self):
        """
        closes a database connection when it is no longer needed
        """
        self.connection.close()


class ParsingChannels(MySQL):

    # @time_of_function
    def create_new_channel(self, url: str, stub: str, last_post_number: int):
        """
        creates a new channel in the ParsingChannel table

        :param stub: telegram channel stub
        :param url: telegram channel url
        :param last_post_number: int
        """
        if type(url) != str or len(url) == 0 or type(stub) != str or len(stub) == 0 or type(last_post_number) != int:
            return "Ошибка при получении данных"
        if self.check_url(url):
            return "Уже есть в базе данных"
        else:
            insert_query = (f"INSERT INTO `ParsingChannels` (url, stub, last_post_number) "
                            f"VALUES ('{url}', '{stub}', '{last_post_number}') ")
            self.do_commit(insert_query)
            return "Добавила!"

    # @time_of_function
    def select_channel_data(self, url: str):
        """
        returns data about the channel by its url

        :type url: str
        :return list(tuple(tg_channel_data))
        """
        select_channel_rows = (f"SELECT url, stub, last_post_number FROM `ParsingChannels`"
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

    def change_channel_stub(self, url: str, new_stub: str):
        """
        updates the stub for the telegram channel

        :param new_stub: str        :type url:
        """
        if self.check_url(url):
            change_query = f"UPDATE `ParsingChannels` SET stub = '{new_stub}' WHERE url = '{url}' "
            self.do_commit(change_query)

    # @time_of_function
    def get_channel_stub(self, url: str):
        """
        returns the telegram channel stub by url

        :type url: str
        """
        if self.check_url(url):
            select_channel_stub = (f"SELECT stub FROM `ParsingChannels`"
                                   f"WHERE url = '{url}' ")
            stub = self.get_data_from_database(select_channel_stub)[0][0]
            return stub

    # @time_of_function
    def get_channels_list(self):
        """
        returns a list of a list of all telegram channels in the database

        :return: generator(tuple(tg_channel_data))
        """
        select_all_channel = f"SELECT url, stub, last_post_number FROM `ParsingChannels` "
        channels = [i for i in self.get_data_from_database(select_all_channel)]
        return channels


class Users(MySQL):

    def add_user_and_user_channel(self, user_id: int, user_channel_id=None):
        """
        adds the user and his channels for posting to the users table

        :param user_channel_id: int or None
        :type user_id: int
        """
        insert_query = f"INSERT INTO `users` (user_id, user_channel_id) VALUES ('{user_id}', '{user_channel_id}')"
        self.do_commit(insert_query)

    def del_user_channel(self, channel_id: int):
        """
        delite the user channel for posting from the users table

        :param channel_id: int
        """
        delete_query = f"DELETE FROM `users` WHERE user_channel_id = '{channel_id}'"
        self.do_commit(delete_query)

    def del_user(self, user_id: int):
        """
        delite the user and his channels for posting from the users table

        :type user_id: int
        """
        delete_query = f"DELETE FROM `users` WHERE user_id = '{user_id}'"
        self.do_commit(delete_query)


class PostingList(MySQL):

    # @time_of_function
    def add_to_posting_list(self, post, post_text):
        """
        adds a post to the posting database table

        :param post_text: str
        :type post: object class TelegramPost
        """
        url = post.get_url()
        text = post_text
        insert_query = f"INSERT INTO `posting_list` (post_url, post_text) VALUES ('{url}', '{text}') "
        self.do_commit(insert_query)

    def get_posting_list(self):
        """
        returns a list of posts that need to be posted

        :return: list(tuple(str))
        """
        data = f"SELECT post_url, post_text FROM `posting_list` "
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
    def add_to_monitored(self, url, channel_id):
        pass

    def get_subscribed_user_chanel_list(self, url):
        pass

    def del_from_monitored(self, url, channel_id):
        pass

# connection = PostingList(*DATA_FOR_DATABASE).get_posting_list()
# print(connection)
