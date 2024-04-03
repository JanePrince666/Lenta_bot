   -- initdb/01_init.sql
   GRANT ALL PRIVILEGES ON *.* TO 'jane'@'%' IDENTIFIED BY 'PrinceoFhalfblood3464_' WITH GRANT OPTION;
FLUSH PRIVILEGES;

   USE lenta_db;

   CREATE TABLE IF NOT EXISTS ParsingChannels (
     url VARCHAR(100),
     last_post_number INT,
     channel_name VARCHAR(100)
   );

   CREATE TABLE IF NOT EXISTS monitored_telegram_channels (
     tg_channel_url VARCHAR(100),
     user_channel_id REAL
   );

   CREATE TABLE IF NOT EXISTS posting_list (
     post_url VARCHAR(100),
     post_text VARCHAR(10000),
     user_channel_id REAL
   );

   CREATE TABLE IF NOT EXISTS users (
     user_channel_id REAL,
     user_id INT,
     channel_name VARCHAR(100)
   );

