import telebot
from config import token
from telebot import types
from utils import check_login, check_password
from database import DataBase
from detection import process_photo
import psycopg2
import requests
from PIL import Image
from datetime import datetime, date, time

bot = telebot.TeleBot(token) # токен лежит в файле config.py
fist_name = None
if_login = False
text_prompt = None
prompt = None
file_unique_id = None

db = DataBase()

if not db.check_table_users():
    db.create_table_users()    
'''
try:
    db.create_table_users()
except:
    print ('Таблица с пользователями уже создана')

try:
    db.create_table_images()
except:
    print ('Таблица с изображениями уже создана')
'''
@bot.message_handler(commands=['start'])
def start(message):
    global first_name
    first_name = message.from_user.first_name
    markup = types.InlineKeyboardMarkup(row_width = 2)
    btn1 = types.InlineKeyboardButton("💙 Регистрация", callback_data = 'registration')
    btn2 = types.InlineKeyboardButton("🤍 Вход", callback_data = 'login')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, text="Привет, {0}! Если ты у нас первый раз, региструйся 💙 !".format(first_name), reply_markup=markup)

@bot.callback_query_handler(func = lambda call: True)
def callback(call):
    global first_name
    global if_login
    if call.message:
        if call.data == 'registration':
            markup = types.InlineKeyboardMarkup(row_width = 2)
            btn1 = types.InlineKeyboardButton("Отмена", callback_data = 'decline')
            markup.add(btn1)
            msg = bot.send_message(call.message.chat.id,'Так-сс смотрю ты у нас первый раз 😎! Быстрее вводи свой логин!', reply_markup=markup)
            bot.register_next_step_handler(message=msg,
                                       callback=registr_login)
            
        if call.data == 'login':
            markup = types.InlineKeyboardMarkup(row_width = 2)
            btn1 = types.InlineKeyboardButton("Отмена", callback_data = 'decline')
            markup.add(btn1)
            msg = bot.send_message(call.message.chat.id, 'С возращением друг 🤗! Вводи логин и пароль через пробел!', reply_markup = markup)
            bot.register_next_step_handler(message=msg,
                                       callback=enter_login)
        if call.data == 'decline':
            msg = bot.send_message(call.message.chat.id,'Хорошо, возращаемся в главное меню')
            call.message.from_user.first_name = first_name
            start(call.message)
        if call.data == 'detection':
            msg = bot.send_message(call.message.chat.id,'Загрузи фотографию:')
        if call.data == 'more':
            if_login = True
            msg = bot.send_message(call.message.chat.id,'Загрузи фотографию:')
        
@bot.message_handler(content_types=['text'])
def registr_login(message):
    global login
    markup = types.InlineKeyboardMarkup(row_width = 2)
    btn1 = types.InlineKeyboardButton("Отмена", callback_data = 'decline')
    markup.add(btn1)
    
    if check_login(message.text):
        if db.check_login(str(message.text)):
            login = message.text
            msg = bot.send_message(message.chat.id,'Круто! Ввводи пароль',reply_markup=markup)
            bot.register_next_step_handler(message=msg,
                                            callback=registr_password)
        else:
            msg = bot.send_message(message.chat.id,'Такой логин уже занят! Введи другой!', reply_markup=markup)
            bot.register_next_step_handler(msg, registr_login)    
    else:
        msg = bot.send_message(message.chat.id,'Логин должен состоять только из букв и цифр! Введи еще раз!', reply_markup=markup)
        bot.register_next_step_handler(msg, registr_login)
@bot.message_handler(content_types=['text'])
def enter_login(message):
    global if_login
    global login_user
    markup = types.InlineKeyboardMarkup(row_width = 2)
    btn1 = types.InlineKeyboardButton("Отмена", callback_data = 'decline')
    markup.add(btn1)

    if len(message.text.split(' ')) == 2:
        login , password = message.text.split(' ')[0], message.text.split(' ')[1]
        if db.check_login_password(login, password):
            markup = types.InlineKeyboardMarkup(row_width = 2)
            btn1 = types.InlineKeyboardButton("Отмена", callback_data = 'decline')
            markup.add(btn1)
            msg = bot.send_message(message.chat.id,'Неверный логин или пароль! Попробуй еще раз!',reply_markup = markup)
            bot.register_next_step_handler(msg, enter_login)
        else:
            login_user = login
            markup = types.InlineKeyboardMarkup(row_width = 2)
            btn1 = types.InlineKeyboardButton("Отмена", callback_data = 'decline')
            btn2 = types.InlineKeyboardButton("Навалить кринжа", callback_data = 'detection')
            markup.add(btn1, btn2)
            msg = bot.send_message(message.chat.id,'Вход выполнен! Пора навалить кринжа!', reply_markup = markup) 
            if_login = True  
    else:
        markup = types.InlineKeyboardMarkup(row_width = 2)
        btn1 = types.InlineKeyboardButton("Отмена", callback_data = 'decline')
        markup.add(btn1)
        msg = bot.send_message(message.chat.id,'Неверный формат ввода! Попробуй еще раз', reply_markup = markup)
        bot.register_next_step_handler(msg, enter_login)       
@bot.message_handler(content_types=['text'])      
def registr_password(message):
    global password
    if check_password(message.text) == 'Поздравляю ты зарегистрирован!':
        password = message.text
        insert_to_db_users()
        bot.send_message(message.chat.id, check_password(message.text))
        start(message)

    else:
        msg = bot.send_message(message.chat.id,check_password(message.text))
        bot.register_next_step_handler(msg, registr_password)

def insert_to_db_users():
    global login
    global password
    db.insert_user(str(login), str(password))

def insert_to_db_images(image_bin, uploaded_on):
    global login_user
    global file_unique_id
    db.insert_images(str(login_user), str(file_unique_id), image_bin)

@bot.message_handler(content_types=['photo'])
def photo(message):
    if if_login:
        global file_unique_id
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)
        file_unique_id = file_info.file_unique_id
        #file_path = requests.get(f'https://api.telegram.org/bot{token}/getFile?file_id={fileID}').json()['result']['file_path']
        #img = Image.open(requests.get(f'https://api.telegram.org/file/bot{token}/{file_path}', stream=True).raw)
        #img_bin = img.convert('1')
        #uploaded_on = datetime.now()
        #insert_to_db_images(img_bin, uploaded_on = uploaded_on)
        with open(f'images/{file_unique_id}.jpg', 'wb') as new_file:
            new_file.write(downloaded_file)
            msg = bot.send_message(message.chat.id,'Отлично! Теперь пиши кого ищем на фото (для лучшего качества пиши запрос на английском)')
            bot.register_next_step_handler(msg, save_text_prompt)

    else:
        bot.send_message(message.chat.id,'Войди сначала в систему!')
        start(message)

@bot.message_handler(content_types=['text'])
def save_text_prompt(message):
    global text_prompt
    text_prompt = message.text
    msg = bot.send_message(message.chat.id,'Напиши на что заменить этот объект? (для лучшего качества пиши запрос на английском)')
    bot.register_next_step_handler(msg, save_prompt)

@bot.message_handler(content_types=['text'])
def save_prompt(message):
    global prompt
    prompt = message.text
    msg = bot.send_message(message.chat.id,'Все круто! Подожди буквально пару минут пока обработается изображение...')
    make_prediction(message)

def make_prediction(message):
    global if_login
    
    pred_image = process_photo(IMAGE_PATH = f'images/{file_unique_id}.jpg',
                               TEXT_PROMPT = text_prompt,
                               prompt = prompt)
    msg = bot.send_message(message.chat.id, 'Твое фото готово! Получай:')
    photo = open('images/' + file_unique_id + '_pred.jpg', 'rb')
    bot.send_photo(message.chat.id, photo)
    if_login = False

    markup = types.InlineKeyboardMarkup(row_width = 2)
    btn1 = types.InlineKeyboardButton("Еще!", callback_data = 'more')
    btn2 = types.InlineKeyboardButton("Выход!", callback_data = 'decline')
    markup.add(btn1, btn2)  
    msg = bot.send_message(message.chat.id, 'Еще? Или выход?', reply_markup = markup) 
bot.polling(none_stop=True)
