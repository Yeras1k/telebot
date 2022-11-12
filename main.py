import os
import telebot
import logging
import psycopg2
import mysql.connector
from telebot import types
from config import *
from flask import Flask, request


bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)

db_connection = conn = psycopg2.connect(
    host="containers-us-west-89.railway.app",
    database="railway",
    user="postgres",
    password="3FsStuIdSScdHsm6KBxn")
    
db_object = db_connection.cursor()
curator_password = "SeniorsTop"

@bot.message_handler(commands=["start"])
def first(message):
    service = telebot.types.ReplyKeyboardMarkup(True, True)
    service.row('Ученик')
    service.row('Куратор')
    send = bot.send_message(message.chat.id, f"Hello, {message.from_user.first_name}! Выберите роль", reply_markup=service)
    bot.register_next_step_handler(send, second)

def second(message):
    if message.text == 'Ученик':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, 'Хорошо', reply_markup=a)
        user_id = message.from_user.id
        db_object.execute(f'SELECT userid FROM students WHERE userid = {user_id}')
        result = db_object.fetchone()
        if result:
            msg = bot.send_message(message.chat.id, f"Введите свое Имя, Фамилию, Класс, Литтер, Email, Номер(все цифры слитно и через 8) в этой последовательности")
            bot.register_next_step_handler(msg, input_data_student)
        else:
            service = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
            service.row('Расписание')
            service.row('Мероприятия')
            service.row('Клубная деятельность')
            msg = bot.send_message(message.chat.id, f"Успешно авторизовались", reply_markup = service)
            bot.register_next_step_handler(msg, main)

    if message.text == 'Куратор':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, 'Хорошо', reply_markup=a)
        msg = bot.send_message(message.chat.id, f"Введите пароль кураторов")
        bot.register_next_step_handler(msg, input_password_curator)


def input_data_student(message):

    user_id = message.from_user.id
    x = message.text.split()
    if len(x) == 6:
        db_object.execute(f"INSERT INTO students(userid, name, surname, class, litter, email, phone) VALUES({user_id}, '{x[0]}', '{x[1]}', {x[2]},'{x[3]}', '{x[4]}', {x[5]})")
        db_connection.commit()
        service = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
        service.row('Расписание')
        service.row('Мероприятия')
        service.row('Клубная деятельность')
        msg = bot.send_message(message.chat.id, f"Успешно авторизовались", reply_markup = service)
        bot.register_next_step_handler(msg, main)
    else:
        msg = bot.send_message(message.chat.id, f"Что то пошло не так, попробуйте еще раз")
        bot.register_next_step_handler(msg, input_data_student)

def input_password_curator(message):
    if message.text == curator_password:
        result = check_curator(message.from_user.id)
        if result == False:
            msg = bot.send_message(message.chat.id, f"Введите свое Имя, Фамилию, Отчество, Шанырак, Email, Номер(все цифры слитно и через 8) в этой последовательности")
            bot.register_next_step_handler(msg, input_data_curator)
        else:
            service = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
            service.row('Расписание')
            service.row('Мероприятия')
            service.row('Клубная деятельность')
            msg = bot.send_message(message.chat.id, f"Успешно авторизовались!", reply_markup = service)
            bot.register_next_step_handler(msg, main_curator)
    else:
        msg = bot.send_message(message.chat.id, f"Пароль не правильный")
        bot.register_next_step_handler(msg, first)

def input_data_curator(message):
    user_id = message.from_user.id
    x = message.text.split()
    if len(x) == 6:
        db_object.execute(f"INSERT INTO curators(curid, name, surname, fathername, shanyrak, email, phone) VALUES({user_id}, '{x[0]}', '{x[1]}', '{x[2]}', '{x[3]}', '{x[4]}', {x[5]})")
        db_connection.commit()
        result = check_curator(message.from_user.id)
        if not result:
            msg = bot.send_message(message.chat.id, f"Что то пошло не так, попробуйте еще раз")
            bot.register_next_step_handler(msg, input_data_curator)
        else:
            service = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
            service.row('Расписание')
            service.row('Мероприятия')
            service.row('Клубная деятельность')
            msg = bot.send_message(message.chat.id, f"Аккаунт успешно создан!", reply_markup = service)
            bot.register_next_step_handler(msg, main_curator)
    else:
        msg = bot.send_message(message.chat.id, f"Что то пошло не так, попробуйте еще раз")
        bot.register_next_step_handler(msg, input_data_curator)

def check_student(id):
    db_object.execute(f"SELECT userid FROM students WHERE userid = {id}")
    result = db_object.fetchone()
    return result


def check_curator(id):
    db_object.execute(f"SELECT curid FROM curators WHERE curid = {id}")
    result = db_object.fetchone()
    return result


def main(message):
    if message.text == 'Расписание':
        id = message.from_user.id
        db_object.execute(f"SELECT class, litter FROM students WHERE userid = {id}")
        result = db_object.fetchall()
        bot.send_message(message.chat.id, f"{result}")

def main_curator(message):
    bot.send_message(message.message.chat.id, "Нажмите что нибудь")


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
