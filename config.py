from aiogram import Bot
import os


my_token = os.getenv('BOT_TOKEN')
# Объект бота
bot = Bot(token=my_token)


db_host = "mysql"
db_port = 3306
db_user_name = "jane"
db_password = os.getenv('DB_JANE_PASSWORD')
db_name = "lenta_db"

DATA_FOR_DATABASE = (db_host, db_port, db_user_name, db_password, db_name)

