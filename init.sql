-- initdb/01_init.sql

-- Установка кодировки по умолчанию для новых баз данных и таблиц
SET @@global.character_set_server = 'utf8mb4';
SET @@global.collation_server = 'utf8mb4_unicode_ci';

-- Создание пользователя и предоставление ему привилегий
GRANT ALL PRIVILEGES ON *.* TO 'jane'@'%' IDENTIFIED BY MYSQL_PASSWORD WITH GRANT OPTION;
FLUSH PRIVILEGES;

-- Выбор базы данных
USE lenta_db;

-- Создание таблиц с указанием кодировки utf8mb4
CREATE TABLE IF NOT EXISTS ParsingChannels (
  url VARCHAR(100),
  last_post_number INT,
  channel_name VARCHAR(1000)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS monitored_telegram_channels (
  tg_channel_url VARCHAR(100),
  user_channel_id REAL
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS posting_list (
  post_url VARCHAR(100),
  post_text VARCHAR(10000),
  user_channel_id REAL
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS users (
  user_channel_id REAL,
  user_id INT,
  channel_name VARCHAR(1000)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
