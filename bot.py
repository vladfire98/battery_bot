#!/bin/python3

import telebot
from telebot import types
from envs import TOKEN, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST
import psycopg2


bot = telebot.TeleBot(TOKEN)

users = {
            'admins': [424488454], 
            'users': []
        }

dick = {
    'types': ['Литиевый', 'Натрий-ионный', 'Никель-цинковый', 'Литиевый', 'Натрий-ионный', 'Никель-цинковый', 'Литиевый', 'Натрий-ионный', 'Никель-цинковый'],
    'sizes': ['200', '300', '400']
}

try:
    # пытаемся подключиться к базе данных
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    print("Соединение к БД установлено!")
except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
    print('Can`t establish connection to database')

cursor = conn.cursor()


@bot.message_handler(commands=['admin'])
def start_message(message):
    keyboardmain = types.InlineKeyboardMarkup()
    create_user_button = types.InlineKeyboardButton(text="Добавить пользователя", callback_data="add_user")
    delete_user_button = types.InlineKeyboardButton(text="Удалить пользователя", callback_data="del_user")
    keyboardmain.add(create_user_button, delete_user_button)

    if message.from_user.id in users['admins']:
        bot.send_message(message.chat.id, "Админка пользователей", reply_markup=keyboardmain)
        @bot.callback_query_handler(func=lambda call: True)
        def callback_inline(call):
            if call.data == "add_user":
                sent = bot.send_message(message.chat.id, "Пришли id пользователя")
                bot.register_next_step_handler(sent, create_user)
            elif call.data == "del_user":
                sent = bot.send_message(message.chat.id, "Пришли id пользователя")
                bot.register_next_step_handler(sent, delete_user)
    else:
        bot.reply_to(message, "Permission denied")


@bot.message_handler(func=lambda message: message.text == 'list')
def create_order(message):
    bot.send_message(message.chat.id, f"{users}")

def create_user(message):
    try:
        #global user_id
        user_id = message.text
        users['users'].append(int(user_id))
        bot.send_message(message.chat.id, f"Пользователь с id {user_id} успешно добавлен в группу users. {users}")
        print(users)
    except ValueError:
        bot.reply_to(message, "Неверный формат ID")

def delete_user(message):
    try:
        #global user_id
        user_id = message.text
        users['users'].remove(int(user_id))
        bot.send_message(message.chat.id, f"Пользователь с id {user_id} успешно удален. {users}")
        print(users)
    except ValueError:
        bot.reply_to(message, "Неверный формат ID")


@bot.message_handler(commands=['start'])
def start(message):
    buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Создать заказ")
    btn2 = types.KeyboardButton("Удалить заказ")
    btn3 = types.KeyboardButton("Посмотреть активные заказы")
    buttons.add(btn1, btn2, btn3)
    #bot.send_message(message.chat.id, text="Привет, {0.first_name}!".format(message.from_user), reply_markup=buttons)
    bot.send_message(message.chat.id, text="Используйте меню внизу для дальшейшего взаимодействия".format(message.from_user), reply_markup=buttons)

@bot.message_handler(func=lambda message: message.text == 'Создать заказ')
def create_order(message):
    if (message.from_user.id in users['users']) or (message.from_user.id in users['admins']):
        buttons_type = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for battery_type in dick['types']:
            buttons_type.add(types.KeyboardButton(battery_type))
        sent = bot.send_message(message.chat.id, "Выберите тип аккумулятора:", reply_markup=buttons_type)
        bot.register_next_step_handler(sent, define_size)
    else:
        bot.send_message(message.chat.id, "Permission denied!")

def define_size(message):
    global select_type
    select_type = message.text
    buttons_size = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for battery_size in dick['sizes']:
        buttons_size.add(types.KeyboardButton(battery_size))
    sent = bot.send_message(message.chat.id, "Выберите размер аккумулятора:", reply_markup=buttons_size)
    bot.register_next_step_handler(sent, handle_confirmation)

def handle_confirmation(message):
    global select_size
    select_size = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Принять'), types.KeyboardButton('Отменить'))
    sent = bot.send_message(message.chat.id, f"Ваш заказ на аккумулятор {select_type} размером {select_size} мАч. Нажмите 'Принять' для подтверждения или 'Отменить' для отмены.", reply_markup=markup)
    #bot.send_message(message.chat.id, f"Тип {select_type} размер {select_size}")
    bot.register_next_step_handler(sent, result_message)

def result_message(message):
    if message.text == 'Принять':
        #cursor.execute("insert into public.alfa (operation, price, uptime) values (%s, %s, current_date)", ('ПОПОЛНЕНИЕ', in_price[1:]))
        cursor.execute("INSERT INTO public.orders (type_battery, size_battery, createdate) VALUES (%s, %s, date_trunc('second', now()) )", (select_type, select_size))
        conn.commit()
        bot.send_message(message.chat.id, "Спасибо! Ваш заказ принят!")
    elif message.text == 'Отменить':
        bot.send_message(message.chat.id, "Действие отменено.")
    start(message)

def insert_db(typ, size):
    print(f"Тип {typ} размер {size}")

@bot.message_handler(content_types=['contact'])
def get_contact(message):
    try:
        contact_id = message.contact.user_id
        bot.reply_to(message, f"ID этого контакта: {contact_id}")
    except BaseException:
        bot.reply_to(message, 'Ожидался контакт пользователя')

bot.polling(none_stop=True)


'''@bot.message_handler(func=lambda message: message.text == 'Добавить пользователя')
def create_user(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, user_id)
    sent = bot.send_message(message.chat.id, "Пришлите контакт пользователя")
    bot.register_next_step_handler(sent, get_contact)   

@bot.message_handler(content_types=['contact'])
def get_contact(message):
    try:
        contact_id = message.contact.user_id
        bot.reply_to(message, f"ID этого контакта: {contact_id}")
    except BaseException:
        bot.reply_to(message, 'Ожидался контакт пользователя')'''