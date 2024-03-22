import os
import time
import re
import random
import logging
import sqlite3
import telebot
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# bot token
load_dotenv()
bot = telebot.TeleBot(os.getenv("TOKEN"))

# регистрация пользователя в БД
def start(message):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    if str(message.chat.id)[0] != "-":
        bot.send_message(message.chat.id, "Бот работает только для групповых чатов!")
        return "dm"
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS chat_{str(message.chat.id)[1:] if str(message.chat.id)[0] == "-" else message.chat.id}(
        id INTEGER,
        username TEXT,
        reputation INTEGER,
        cooldown ITEGER
    );""")
    connect.commit()
    id = message.from_user.id
    user_check = cursor.execute(f"SELECT id from chat_{str(message.chat.id)[1:]} WHERE id = {id}").fetchone()
    if user_check is None:
        if message.from_user.username:
            username = message.from_user.username
        elif message.from_user.last_name:
            username = " ".join([message.from_user.first_name, message.from_user.last_name])
        else:
            username = message.from_user.first_name
        cursor.execute(f"INSERT INTO chat_{str(message.chat.id)[1:]} VALUES(?, ?, ?, ?);", [id, username, 0, 0])
        connect.commit()
        bot.send_message(message.chat.id, f"Привет, @{message.from_user.username}. Рад познакомиться с тобой! 😀\nТы можешь посмотреть список моих команд, написав /help")

# список команд бота
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Команды бота:\n" +
                    "/all – упомянуть всех людей в чате;\n" +
                    "/coinflip – подбросить монетку, чтобы решить спор;\n" +
                    "+rep @кому причина (не обязательно) – повысить репутацию пользователю. Например, <code>+rep @durov_russia спасибо за телегу</code>.\n<b>Изменять репутацию можно один раз в час</b>;\n" +
                    "-rep @кому причина – понизить репутацию пользователю. Синтаксис такой же;\n" +
                    "/statistics – топ пользователей по репутации в чате;\n" +
                    "/help – помощь по командам.",
                    parse_mode='html')

# статистика по репутации всех пользователей чата
@bot.message_handler(commands=['statistics'])
def statistics(message):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"""SELECT username, reputation FROM chat_{str(message.chat.id)[1:]} ORDER BY reputation DESC""")
    record = cursor.fetchall()
    user_stat = "@" + "\n@".join([user[0] + "   ---->   " + str(user[1]) for user in record])
    bot.send_message(message.chat.id, f"Статистика репутации всех пользователей:\n{user_stat}")

# пинг всех пользователей
@bot.message_handler(commands=['all'])
def ping_all(message):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    members = cursor.execute(f"""SELECT username from chat_{str(message.chat.id)[1:]}""").fetchall()
    bot.delete_message(message.chat.id, message.message_id)
    members_list = "@" + ", @".join([x[0] for x in members if x[0] != message.from_user.username])
    # использую html разметку, а не MD, потому что проблемы с никнеймами, в которых есть символ "_"
    bot.send_message(message.chat.id, f"@{message.from_user.username} упоминает всех\n<span class=\"tg-spoiler\">({members_list})</span>", 'html')

# подбросить монетку
@bot.message_handler(commands=['coinflip'])
def coinflip(message):
    bot.delete_message(message.chat.id, message.message_id)
    min_num = 0
    max_num = 1
    r = requests.get(f"https://www.random.org/integers/?num=1&min={min_num}&max={max_num}&col=1&base=10&format=plain&rnd=new&cl=w")
    if not r.ok:
        bot.send_message(message.chat.id, "Произошла ошибка при обращении к random.org.\nПопробуйте позже!")
        return
    soup = BeautifulSoup(r.text, "html.parser")
    answer = int(soup.find("span").text.strip())
    bot_message = bot.send_message(message.chat.id, f"@{message.from_user.username} подбрасывает монетку и выпадает...")
    time.sleep(2)
    bot.edit_message_text(f"{bot_message.text}\n<b>{'орёл' if answer == 0 else 'решка'}</b>{' – подкрутка? 🤨' if random.randint(0, 10) == 5 else ''}", message.chat.id, bot_message.message_id, parse_mode='html')

@bot.message_handler(content_types=['text'])
def text_handler(message):
    start(message)
    if message.text.lower()[:4] in ['+rep', '-rep', '+реп', '-реп']:
        reputation(message)
    # монструозная строка. читаю справа налево: убираю знаки препинания (все НЕ буквы) -> с помощью split() создаю массив слов -> проверяю, есть ли слово "лось" в этом массиве
    elif any(element_a in ['лось', 'лося', 'лосю', 'лосем', 'лосём', 'лосе', 'лосей',
                           'лоси', 'лосей', 'лосям', 'лосями', 'лосях'] for element_a in re.sub(r'[^\w\s]', '', message.text.lower()).split()):
        mooseMeme(message)


# добавление и отнимание репутации
def reputation(message):
        connect = sqlite3.connect("data.db")
        cursor = connect.cursor()
        cooldown = cursor.execute(f"SELECT cooldown from chat_{str(message.chat.id)[1:]} WHERE id = {message.from_user.id}").fetchone()[0]
        # проверка на кулдаун
        if round(time.time()) - cooldown < 3600:
            cooldown_remain = int(((time.time() - cooldown - 3600) / 60) // -1)
            bot.send_message(message.chat.id, f"Изменять репутацию можно только раз в час! Попробуй снова через {cooldown_remain} минут{'ы' if cooldown_remain in [2, 3, 4] else 'у' if cooldown == 1 else ''}")
            return "cooldown"
        to_whom = message.text.split()[1][1:]
        # вставить ник будущего бота
        if to_whom == bot.get_me().username:
            if message.text[0] == "-":
                bot.send_message(message.chat.id, f"Вы решили посягнуть на святое! Я конфисковать у вас {'кошка жена и ' if random.randint(0, 1) == 1 else ''}{random.randint(1, 10)} миска рис!")
            else:
                bot.send_message(message.chat.id, "Ой спасиба\n   🥺\n👉🏻 👈🏻")
            return "rep bot"
        if message.from_user.username != to_whom:
            cursor.execute(f"SELECT username, reputation from chat_{str(message.chat.id)[1:]}")
            current = cursor.fetchall()
            for user in current:
                if user[0] == to_whom:
                    rep = user[1] + 1 if message.text[0] == "+" else user[1] - 1
                    break
            try:
                cursor.execute(f"""UPDATE chat_{str(message.chat.id)[1:]} set reputation = ? where username = ?""", (rep, to_whom))
            except UnboundLocalError:
                bot.send_message(message.chat.id, "Такого пользователя нет в чате или он не написал /start")
                return UnboundLocalError
            cursor.execute(f"""UPDATE chat_{str(message.chat.id)[1:]} set cooldown = {time.time()} where id = {message.from_user.id}""")
            connect.commit()
            bot.delete_message(message.chat.id, message.message_id)
            try:
                bot.send_message(message.chat.id, f"@{message.from_user.username} {'повышает' if message.text[0] == '+' else 'понижает'} репутацию @{to_whom}.\nПричина: {message.text.split(' ', 2)[2]}.\nТеперь репутация равна {rep}")
            except IndexError:
                bot.send_message(message.chat.id, f"@{message.from_user.username} {'повышает' if message.text[0] == '+' else 'понижает'} репутацию @{to_whom}.\nПричина: нет.\nТеперь репутация равна {rep}")
        else:
            bot.send_message(message.chat.id, f"Нельзя {'повыcить' if message.text[0] == '+' else 'понизить'} репутацию самому себе!")

def mooseMeme(message):
    if 'лось' in message.text.lower().split(): ending = 'такой'
    elif 'лося' in message.text.lower().split(): ending = 'такого'
    elif 'лосю' in message.text.lower().split(): ending = 'такому'
    elif 'лосем' in message.text.lower().split(): ending = 'таким'
    elif 'лосём' in message.text.lower().split(): ending = 'такие'
    elif 'лосе' in message.text.lower().split(): ending = 'о таком'
    elif 'лосей' in message.text.lower().split(): ending = 'таких'
    elif 'лоси' in message.text.lower().split(): ending = 'такие'
    elif 'лосям' in message.text.lower().split(): ending = 'таким'
    elif 'лосями' in message.text.lower().split(): ending = 'такими'
    elif 'лосях' in message.text.lower().split(): ending = 'о таких'
    # тут лучше использовать id фотографии, но у меня на релизе не получалось. пришлось делать так
    with open('moose.jpg', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, f"@{message.from_user.username}, вот {ending}?")


while __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="logging.log", filemode="w",
                        format="%(asctime)s %(levelname)s %(message)s")
    try:
        logging.info("Bot start")
        bot.polling(True)
    except requests.exceptions.ReadTimeout:
        logging.warn("ReadTimeout error. Restarting bot...")
    except Exception as error:
        logging.critical(f"Error:\n{error}", exc_info=True)
        continue