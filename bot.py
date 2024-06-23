#!/bin/python3

import telebot
from telebot import types
from telebot.types import ReplyKeyboardRemove
from envs import TOKEN, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST
import psycopg2
import re


bot = telebot.TeleBot(TOKEN)

users = {
            'admins': [424488454, 798583829], 
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


@bot.message_handler(commands=['start'])
def start(message):
    buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Создать заказ")
    btn2 = types.KeyboardButton("Удалить заказ")
    btn3 = types.KeyboardButton("Посмотреть активные заказы")
    buttons.add(btn1, btn2, btn3)
    #bot.send_message(message.chat.id, text="Привет, {0.first_name}!".format(message.from_user), reply_markup=buttons)
    bot.send_message(message.chat.id, text="Используйте меню внизу для дальшейшего взаимодействия".format(message.from_user), reply_markup=buttons)


#================ADMIN PANEL====================
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

@bot.message_handler(func=lambda message: message.text == 'list')
def create_order(message):
    bot.send_message(message.chat.id, f"{users}")



#================CREATE ORDER====================
@bot.message_handler(func=lambda message: message.text == 'Создать заказ')
def create_order(message):
    if (message.from_user.id in users['users']) or (message.from_user.id in users['admins']):
        buttons_type = types.ReplyKeyboardMarkup(resize_keyboard=True)
        cursor.execute("select element_type from public.elements")
        elements = cursor.fetchall()
        print(elements)
        for element in elements:
            buttons_type.add(types.KeyboardButton(element[0]))
        sent = bot.send_message(message.chat.id, "Выберите тип аккумулятора:", reply_markup=buttons_type)
        bot.register_next_step_handler(sent, question_size)
    else:
        bot.send_message(message.chat.id, "Permission denied!")

'''def define_size(message):
    global select_type
    select_type = message.text
    buttons_size = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for battery_size in dick['sizes']:
        buttons_size.add(types.KeyboardButton(battery_size))
    sent = bot.send_message(message.chat.id, "Выберите размер аккумулятора:", reply_markup=buttons_size)
    bot.register_next_step_handler(sent, handle_confirmation)'''

def question_size(message):
    global select_type
    select_type = message.text
    sent = bot.send_message(message.chat.id, "Размер АКБ(мм)", reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(sent, question_voltage)

def question_voltage(message):
    global select_size
    select_size = message.text
    if (re.match("^[0-9]+[x][0-9]+", select_size.lower()) or re.match("^[0-9]+[х][0-9]+", select_size.lower()) ):
#        print("букв нет")
        sent = bot.send_message(message.chat.id, "Напряжение(nom(V))")
        bot.register_next_step_handler(sent, question_lenght)
    else:
        print("тут есть буквы")
        sent = bot.send_message(message.chat.id, f"Допустимый формат записи ЧИСЛОхЧИСЛО (например 300х200).\nПовторите попытку.")
        bot.register_next_step_handler(sent, question_voltage)

def question_lenght(message):
    global select_voltage
    select_voltage = message.text
    if re.match("^[0-9,.]+$", select_voltage):
        print("chars not found")
        sent = bot.send_message(message.chat.id, "Укажите длину выводов(мм)")
        bot.register_next_step_handler(sent, question_name)
    else:
        sent = bot.send_message(message.chat.id, f"Неверный формат записи.\nНеобходимо указывать без единиц измерения (только число).\nПовторите попытку.")
        bot.register_next_step_handler(sent, question_lenght)

def question_name(message):
    global select_lenghts
    select_lenghts = message.text
    if re.match("^[0-9,.]+$", select_lenghts):
        print("chars not found")
        sent = bot.send_message(message.chat.id, "ФИО")
        bot.register_next_step_handler(sent, question_number_phone)
    else:
        sent = bot.send_message(message.chat.id, f"Неверный формат записи.\nНеобходимо указывать без единиц измерения (только число).\nПовторите попытку.")
        bot.register_next_step_handler(sent, question_name)

def question_number_phone(message):
    global select_FIO
    select_FIO = message.text
    sent = bot.send_message(message.chat.id, "Укажите номер телефона (в формате 7XXXXXXXXX)")
    bot.register_next_step_handler(sent, handle_confirmation)



def handle_confirmation(message):
    global select_number_phone
    select_number_phone = message.text
    if (re.match("[0-9]+", select_number_phone) and len(select_number_phone)<=11):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Принять'), types.KeyboardButton('Отменить'))
        message_confirmation=f"Тип ячеек: {select_type}\nДлина выводов: {select_lenghts} мм\nНапряжение: {select_voltage} V\nРазмер АКБ: {select_size} мм\nИмя клиента: {select_FIO}\nНомер телефона: {select_number_phone}\nНажмите 'Принять' для подтверждения или 'Отменить' для отмены."
        sent = bot.send_message(message.chat.id, message_confirmation, reply_markup=markup)
        #bot.send_message(message.chat.id, f"Тип {select_type} размер {select_size}")
        bot.register_next_step_handler(sent, result_message)
    else:
        sent = bot.send_message(message.chat.id, f"Неверный формат записи.\nПовторите попытку.")
        bot.register_next_step_handler(sent, handle_confirmation)

def result_message(message):
    if message.text == 'Принять':
        #cursor.execute("insert into public.alfa (operation, price, uptime) values (%s, %s, current_date)", ('ПОПОЛНЕНИЕ', in_price[1:]))
        cursor.execute("INSERT INTO public.orders (type_battery, size_battery, voltage_battery, lenghts_battery, FIO, number_phone, createdate) \
                       VALUES (%s, %s, %s, %s, %s, %s, date_trunc('second', now()) )", \
                       (select_type, select_size, int(select_voltage), int(select_lenghts), select_FIO, int(select_number_phone)))
        conn.commit()
        bot.send_message(message.chat.id, "Спасибо! Ваш заказ принят!")
    elif message.text == 'Отменить':
        bot.send_message(message.chat.id, "Действие отменено.")
    start(message)

def insert_db(typ, size):
    print(f"Тип {typ} размер {size}")


#================LIST ORDERS====================
@bot.message_handler(func=lambda message: message.text == 'Посмотреть активные заказы')
def list_orders(message):
    if (message.from_user.id in users['users']) or (message.from_user.id in users['admins']):
        cursor.execute("SELECT order_id, type_battery, size_battery, voltage_battery, lenghts_battery, FIO, number_phone, createdate \
                       FROM public.orders")
        orders = cursor.fetchall()
        print(orders)
        for order in orders:
            order_id = order[0]
            type_battery = order[1]
            size_battery = order[2]
            voltage_battery = order[3] 
            lenghts_battery = order[4]
            FIO = order[5]
            number_phone = order[6]
            createdate = order[7]
            bot.send_message(message.chat.id, f"Номер заказа: {order_id}\nТип ячеек: {type_battery}\nРазмер АКБ: {size_battery}мм\nНапряжение: {voltage_battery}V\nДлина выводов: {lenghts_battery}мм\nФИО: {FIO}\nНомер телефона: {number_phone}\nДата создания заказа: {createdate}")
        conn.commit()
    else:
        bot.send_message(message.chat.id, "Permission denied!")

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