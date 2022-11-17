import os
import telebot
import logging
import mysql.connector
from telebot import types
from config import *
from flask import Flask, request


bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)

curator_password = "qwerty"
teacher_password = "z123456"

mydb = mysql.connector.connect(
    host = "containers-us-west-117.railway.app",
    port = "5550",
    user = "root",
    password = "O53tgAfYAUfJUOTYaa6Y",
    database = "railway"
)
mycursor = mydb.cursor(buffered=True)

@bot.message_handler(commands=["start"])
def first(message):
    service = telebot.types.ReplyKeyboardMarkup(True, True)
    service.row('Ученик', 'Куратор')
    service.row('Учитель')
    send = bot.send_message(message.chat.id, f"Hello, {message.from_user.first_name}! Выберите роль", reply_markup=service)
    bot.register_next_step_handler(send, second)


def second(message):
    if message.text == 'Ученик':
        user_id = message.from_user.id
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, 'Хорошо', reply_markup=a)
        mycursor.execute(f'SELECT userid FROM students WHERE userid = {user_id}')
        result = mycursor.fetchone()

        if not result:
            msg = bot.send_message(message.chat.id, f"Введите свое Имя, Фамилию, Класс, Литтер(только на английском), Email в этой последовательности")
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

    if message.text == 'Учитель':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, 'Хорошо', reply_markup=a)
        msg = bot.send_message(message.chat.id, f"Введите пароль учителей")
        bot.register_next_step_handler(msg, input_password_teacher)

def input_data_student(message):
    user_id = message.from_user.id
    x = message.text.split()
    if len(x) == 5:
        mycursor.execute(f"INSERT INTO students(userid, name, surname, class, litter, email) VALUES({user_id}, '{x[0]}', '{x[1]}', {x[2]},'{x[3]}', '{x[4]}')")
        mydb.commit()
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
        user_id = message.from_user.id
        mycursor.execute(f'SELECT curid FROM curators WHERE curid = {user_id}')
        result = mycursor.fetchone()
        if not result:
            msg = bot.send_message(message.chat.id, f"Введите свое Имя, Фамилию, Отчество, Шанырак, Email в этой последовательности")
            bot.register_next_step_handler(msg, input_data_curator)
        else:
            service = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
            service.row('Назначить мероприятие')
            msg = bot.send_message(message.chat.id, f"Успешно авторизовались!", reply_markup = service)
            bot.register_next_step_handler(msg, main_curator)
    else:
        msg = bot.send_message(message.chat.id, f"Пароль не правильный")
        bot.register_next_step_handler(msg, first)

def input_password_teacher(message):
    if message.text == teacher_password:
        user_id = message.from_user.id
        mycursor.execute(f'SELECT tid FROM teachers WHERE tid = {user_id}')
        result = mycursor.fetchone()
        if not result:
            msg = bot.send_message(message.chat.id, f"Введите свое Имя, Фамилию, Предмет, Email в этой последовательности")
            bot.register_next_step_handler(msg, input_data_teacher)
        else:
            service = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
            service.row('Класс')
            msg = bot.send_message(message.chat.id, f"Успешно авторизовались!", reply_markup = service)
            bot.register_next_step_handler(msg, main_teacher)
    else:
        msg = bot.send_message(message.chat.id, f"Пароль не правильный")
        bot.register_next_step_handler(msg, first)


def input_data_teacher(message):
    user_id = message.from_user.id
    x = message.text.split()
    if len(x) == 4:
        mycursor.execute(f"INSERT INTO teachers(tid, name, surname, subject, email) VALUES({user_id}, '{x[0]}', '{x[1]}', '{x[2]}', '{x[3]}')")
        mydb.commit()
        mycursor.execute(f"SELECT tid FROM teachers WHERE tid = {user_id}")
        result = mycursor.fetchone()
        if not result:
            msg = bot.send_message(message.chat.id, f"Что то пошло не так, попробуйте еще раз, введите еще раз")
            bot.register_next_step_handler(msg, input_data_teacher)
        else:
            service = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
            service.row('Назначить мероприятие')
            msg = bot.send_message(message.chat.id, f"Аккаунт успешно создан!", reply_markup = service)
            bot.register_next_step_handler(msg, main_teacher)
    else:
        msg = bot.send_message(message.chat.id, f"Что то пошло не так, попробуйте еще раз")
        bot.register_next_step_handler(msg, input_data_teacher)

def input_data_curator(message):
    user_id = message.from_user.id
    x = message.text.split()
    if len(x) == 5:
        mycursor.execute(f"INSERT INTO curators(curid, name, surname, fathername, shanyrak, email) VALUES({user_id}, '{x[0]}', '{x[1]}', '{x[2]}', '{x[3]}', '{x[4]}')")
        mydb.commit()
        mycursor.execute(f"SELECT curid FROM curators WHERE curid = {user_id}") #выбирает айди из базы данных
        result = mycursor.fetchone()
        if not result:
            msg = bot.send_message(message.chat.id, f"Что то пошло не так, попробуйте еще раз") #выдает ошибку
            bot.register_next_step_handler(msg, input_data_curator)
        else:
            service = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
            service.row('Назначить мероприятие')
            msg = bot.send_message(message.chat.id, f"Аккаунт успешно создан!", reply_markup = service) #создает аккаунт
            bot.register_next_step_handler(msg, main_curator)
    else:
        msg = bot.send_message(message.chat.id, f"Что то пошло не так, попробуйте еще раз")
        bot.register_next_step_handler(msg, input_data_curator)


def main(message):
    if message.text == 'Расписание':
        id = message.from_user.id
        mycursor.execute(f"SELECT class, litter FROM students WHERE userid = {id}")
        result = mycursor.fetchall()
        a = str(result[0][0]) + result[0][1]
        file = open(f"{a}" + '.png', 'rb')
        bot.send_photo(message.chat.id, file, "Расписание")

def main_curator(message):
    if message.text == 'Назначить мероприятие':
        msg = bot.send_message(message.chat.id, "Введите сообщение")
        bot.register_next_step_handler(msg, event)


def main_teacher(message):
    if message.text == 'Класс':
        msg = bot.send_message(message.chat.id, "Введите класс(класс и литер отделены пробелом)")
        bot.register_next_step_handler(msg, usp)

def usp(message):
    x = message.text.split()
    mycursor.execute("SELECT userid, name, surname FROM students WHERE class = %s AND litter = %s", (x[0], x[1]))
    result = mycursor.fetchall()
    reply_message = "- All class:\n"
    for i in range(len(result)):
        reply_message += f"{result[i][0]} {result[i][1]}) {result[i][2]}\n"
    bot.send_message(message.chat.id, reply_message)
    msg = bot.send_message(message.chat.id, "Введите id учеников которые отсутвовали на уроке через пробел")
    bot.register_next_step_handler(msg, progul)


def progul(message):
    x = message.text.split()
    a = mycursor.execute("SELECT curid FROM curators")
    allresult = []
    for i in range(len(x)):
        mycursor.execute("SELECT name, surname FROM students WHERE userid = %s", (x[i]))
        result = mycursor.fetchall()
        allresult.append(result)
    for i in range(len(allresult)):
        bot.send_message(message.chat.id, f"{allresult[i]}")
    bot.send_message(a, "ОТСУТСВОВАЛИ")

def event(message):
    a = mycursor.execute("SELECT userid FROM students")
    result = mycursor.fetchall()
    for i in range(len(result)):
        for j in range(len(result[i])):
            bot.send_message(result[i][j], message.text)
    msg = bot.send_message(message.chat.id, "Сообщение отправлено")
    bot.register_next_step_handler(msg, main_curator)


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
