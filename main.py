import os
import telebot
import logging
import psycopg2
from telebot import types
from config import *
from flask import Flask, request

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)

db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()

curator_password = "SeniorsTop"

@bot.message_handler(commands=["start"])
def first(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add('Ученик')
    keyboard.add('Куратор')
    send = bot.send_message(message.chat.id, f"Hello, {message.from_user.first_name}!", reply_markup=keyboard)
    bot.register_next_step_handler(send, second)

def second(message):
    if message.text == 'Ученик':
        keyboard = telebot.types.ReplyKeyboardMarkup(True,False)
        user_id = message.from_user.id
        db_object.execute(f"SELECT userid FROM students WHERE userid = {user_id}")
        result = db_object.fetchone()
        if not result:
            msg = bot.send_message(message.chat.id, f"Введите свое Имя, Фамилию, класс, литтер, email, номер(все цифры слитно и через 8) в этой последовательности")
            bot.register_next_step_handler(msg, input_data_student)
        if result:
            keyboard = telebot.types.ReplyKeyboardMarkup(True,False)
            keyboard.row('Расписание', 'Мероприятия')
            keyboard.add('Клубная деятельность/олимпиадная подготовка')
            keyboard.add('Маршрутный лист')

    elif message.text == 'Куратор':
        msg = bot.send_message(message.chat.id, f"Введите пароль кураторов", reply_markup=keyboard)
        bot.register_next_step_handler(msg, input_password_curator)
    else:
        bot.send_message(message.chat.id,'Я не понял')

def input_data_student(message):
    user_id = message.from_user.id
    x = message.text.split()
    if len(x) == 6:
        db_object.execute(f"INSERT INTO students(userid, name, surname, class, litter, email, phone) VALUES({user_id}, '{x[0]}', '{x[1]}', {x[2]},'{x[3]}', '{x[4]}', {x[5]})")
        db_connection.commit()
        keyboard = telebot.types.ReplyKeyboardMarkup(True,False)
        keyboard.row('Расписание', 'Мероприятия')
        keyboard.add('Клубная деятельность/олимпиадная подготовка')
        keyboard.add('Маршрутный лист')
    else:
        msg = bot.send_message(message.chat.id, f"Что то пошло не так, попробуйте еще раз")
        bot.register_next_step_handler(msg, input_data_student)

def input_password_curator(message):
    if message.text == curator_password:
        msg = bot.send_message(message.chat.id, f"Введите свое Имя, Фамилию, класс, литтер, email, номер(все цифры слитно и через 8) в этой последовательности", reply_markup=keyboard)
        bot.register_next_step_handler(msg, input_data_curator)
    else:
        msg = bot.send_message(message.chat.id, f"Пароль не правильный")
        bot.register_next_step_handler(msg, first)

def input_data_curator(message):
    user_id = message.from_user.id
    x = message.text.split()
    if len(x) == 6:
        db_object.execute(f"INSERT INTO students(curid, name, surname, fathername, shanyrak, email, phone) VALUES({user_id}, '{x[0]}', '{x[1]}', '{x[2]}', '{x[3]}', '{x[4]}', {x[5]})")
        db_connection.commit()
    else:
        msg = bot.send_message(message.chat.id, f"Что то пошло не так, попробуйте еще раз", reply_markup=keyboard)
        bot.register_next_step_handler(msg, input_data_curator)

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
