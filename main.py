import os
import telebot
import logging
import psycopg2
from config import *
from flask import Flask, request

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)

db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()



@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    bot.reply_to(message, f"Hello, {message.from_user.first_name}!")
    db_object.execute(f"SELECT id FROM students WHERE id = {user_id}")
    result = db_object.fetchone()
    if not result:
        msg = bot.send_message(message.chat.id, f"Введите свое Имя, Фамилию, класс, литтер, email, номер(все цифры слитно и через 8) в этой последовательности")
        bot.register_next_step_handler(msg, input_data)

def input_data(message):
    user_id = message.from_user.id
    data1 = message.text.split()
    bot.send_message(message.chat.id, f"{data1}")
    db_object.execute(f"INSERT INTO students(id, name, surname, class, litter, email, phone) VALUES ({user_id}, '{data1[0]}', '{data1[1]}', {data1[2]}, '{data1[3]}', '{data1[4]}', {data1[5]})")
    db_connection.commit()

@server.route(f"/{BOT_TOKEN}", methods=["POST"])
def redirect_message():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
