import mysql.connector
from config import db_host, db_user_name, db_password


class MySQL:
    def __init__(self, host, user, password, db_name):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )

    def add_user(self, user_id, user_channel_id):
        insert_query = f"INSERT INTO `users` (user_id, user_channel_id) VALUES ('{user_id}', '{user_channel_id}')"
        with self.connection.cursor() as cursor:
            cursor.execute(insert_query)
            self.connection.commit()

    def del_user(self, user_id):
        delete_query = f"DELETE FROM `users` WHERE user_id = '{user_id}'"
        with self.connection.cursor() as cursor:
            cursor.execute(delete_query)
            self.connection.commit()

    def create_new_channel(self, url, stub, last_post_number: int):
        if not self.check_url(url):
            insert_query = (f"INSERT INTO `ParsingChannels` (url, stub, last_post_number) "
                            f"VALUES ('{url}', '{stub}', '{last_post_number}') ")
            with self.connection.cursor() as cursor:
                cursor.execute(insert_query)
                self.connection.commit()

    def select_channel_data(self, url):
        select_channel_rows = (f"SELECT url, stub, last_post_number FROM `ParsingChannels`"
                               f"WHERE url = '{url}' ")
        with self.connection.cursor() as cursor:
            cursor.execute(select_channel_rows)
            rows = cursor.fetchall()
            return rows

    def check_url(self, url):
        return len(self.select_channel_data(url)) > 0

    def change_channel_last_post(self, url, new_data: int):
        if self.check_url(url):
            change_query = f"UPDATE `ParsingChannels` SET last_post_number = '{new_data}' WHERE url = '{url}' "
            with self.connection.cursor() as cursor:
                cursor.execute(change_query)
                self.connection.commit()

    def get_channel_stub(self, url):
        if self.check_url(url):
            select_channel_stub = (f"SELECT stub FROM `ParsingChannels`"
                                   f"WHERE url = '{url}' ")
            with self.connection.cursor() as cursor:
                cursor.execute(select_channel_stub)
                stub = cursor.fetchall()[0][0]
                return stub

    def get_channels_list(self):
        select_all_channel = f"SELECT url, last_post_number FROM `ParsingChannels` "
        with self.connection.cursor() as cursor:
            cursor.execute(select_all_channel)
            for i in cursor.fetchall():
                yield i

    def select_all_data(self):
        select_all_rows = f"SELECT * FROM `ParsingChannels` "
        with self.connection.cursor() as cursor:
            cursor.execute(select_all_rows)
            rows = cursor.fetchall()
            return rows

    def __del__(self):
        self.connection.close()


connection = MySQL(db_host, db_user_name, db_password, "lenta_db")
# print([i for i in connection.get_channels_list()])
