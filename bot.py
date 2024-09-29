import datetime
import os
import time
import random
import logging
import telebot
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

import db


load_dotenv()
bot = telebot.TeleBot(os.getenv("TOKEN"))

# регистрация пользователя в БД
def start(message):
    """Регистрация пользователя в БД"""
    if str(message.chat.id)[0] != "-":
        bot.send_message(message.chat.id, "Бот работает только для групповых чатов!")
        return "dm"
    # TODO: добавление пользователя без username
    if not message.from_user.username:
        bot.send_message(message.chat.id, f"Прости, пока не могу запомнить, как тебя зовут 🥺. Чтобы помочь мне, придумай себе никнейм!\n" +
                                          "Для этого перейди в настройки и впиши его в поле \"Имя пользователя\"")
        return "no username"
    db.createTable(message.chat.id)
    user_in_db = db.isUserInDB(message.chat.id, message.from_user.id)
    if not user_in_db:
        db.addUser(message.chat.id, message.from_user.id, message.from_user.username)
        bot.send_message(message.chat.id, f"Привет, @{message.from_user.username}. Рад познакомиться с тобой! 😀\nТы можешь посмотреть список моих команд, написав /help")
    elif user_in_db[1] != message.from_user.username:
        db.updateUsername(message.chat.id, message.from_user.id, message.from_user.username)
        bot.send_message(message.chat.id, "Ух ты! Вижу, ты обновил свой никнейм. Он тебе очень идёт. Теперь буду знать, что это именно ты")

@bot.message_handler(commands=['help'])
def help(message):
    """Список команд бота"""
    start(message)
    bot.send_message(message.chat.id, "Команды бота:\n" +
                    "/all – упомянуть всех людей в чате;\n" +
                    "/coinflip – подбросить монетку, чтобы решить спор;\n" +
                    "+rep @кому причина (не обязательно) – повысить репутацию пользователю. Например, <code>+rep @durov_russia спасибо за телегу</code>.\n<b>Изменять репутацию можно один раз в час</b>;\n" +
                    "-rep @кому причина – понизить репутацию пользователю. Синтаксис такой же;\n" +
                    "/statistics – топ пользователей по репутации в чате;\n" +
                    "/help – помощь по командам.",
                    parse_mode='html')

@bot.message_handler(commands=['statistics'])
def statistics(message):
    """Статистика по репутации всех пользователей чата"""
    start(message)
    records = db.getStatistics(message.chat.id)
    user_stat = "@" + "\n@".join([user[0] + "   ---->   " + str(user[1]) for user in records])
    bot.send_message(message.chat.id, f"Статистика репутации всех пользователей:\n{user_stat}")

@bot.message_handler(commands=['all'])
def ping_all(message):
    """Пинг всех пользователей"""
    start(message)
    members = db.getUserList(message.chat.id)
    bot.delete_message(message.chat.id, message.message_id)
    members_list = "@" + ", @".join([x[0] for x in members if x[0] != message.from_user.username])
    # использую html разметку, а не MD, потому что проблемы с никнеймами, в которых есть символ "_"
    bot.send_message(message.chat.id, f"@{message.from_user.username} упоминает всех\n<span class=\"tg-spoiler\">({members_list})</span>", 'html')

@bot.message_handler(commands=['coinflip'])
def coinflip(message):
    """Подбросить монетку"""
    start(message)
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
    anyText(message)
    if message.chat.type != "supergroup":
        bot.send_message(message.chat.id, "Бот работает только для групповых чатов!")
        return "dm"
    if message.text.lower()[:4] in ['+rep', '-rep', '+реп', '-реп']:
        reputation(message)


def anyText(message):
    """Функция, которая применяется для каждого сообщения"""
    reactions = ["👍", "👎", "❤", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "🥱", "🥴", "😍", "🐳", "❤‍🔥", "🌚", "🌭", "💯", "🤣", "⚡", "🍌", "🏆", "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈", "😴", "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", "🤝", "✍", "🤗", "🫡", "🎅", "🎄", "☃", "💅", "🤪", "🗿", "🆒", "💘", "🙉", "🦄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂", "🤷", "🤷‍♀", "😡"]
    url = f'https://api.telegram.org/bot{os.getenv("TOKEN")}/setMessageReaction'
    data = {
        'chat_id': message.chat.id,
        'message_id': message.message_id,
        'reaction': [
            {
                'type': 'emoji',
                'emoji': random.choice(reactions)
            }
        ],
        'is_big': False
    }

    r = True
    if random.randint(0, 10)==0: r = requests.post(url, json=data).ok
    if not r: logging.warning("Failed while sending message reaction!")

def reputation(message):
    """Добавление и отнимание репутации"""
    # проверка правильности написания команды
    try:
        to_whom = message.text.split()[1][1:]
    except IndexError:
        bot.send_message(message.chat.id, "Ошибка при вводе запроса. Проверьте синтаксис, написав команду /help")
        return

    if not db.isUserInDBByUsername(message.chat.id, to_whom):
        bot.send_message(message.chat.id, "Такого пользователя нет в чате или я ещё не знаком с ним. Попросите его написать тут что-то")

    # проверка на кулдаун
    cooldown = db.getCooldown(message.chat.id, message.from_user.id)
    if round(time.time()) - cooldown < 3600:
        cooldown_remain = int(((time.time() - cooldown - 3600) / 60) // -1)
        bot.send_message(message.chat.id, f"Изменять репутацию можно только раз в час! Попробуй снова через {cooldown_remain} минут{'ы' if cooldown_remain in [2, 3, 4] else 'у' if cooldown == 1 else ''}")
        return

    # репутация бота
    if to_whom == bot.get_me().username:
        if message.text[0] == "-":
            bot.send_message(message.chat.id, f"Вы решили посягнуть на святое! Я конфисковать у вас {'кошка жена и ' if random.randint(0, 1) == 1 else ''}{random.randint(1, 10)} миска рис!")
        else:
            bot.send_message(message.chat.id, "Ой спасиба\n   🥺\n👉🏻 👈🏻")
        return
    # репутация себе
    elif message.from_user.username == to_whom and message.text[0] in ["+", "-"]:
        bot.send_message(message.chat.id, f"Нельзя {'повыcить' if message.text[0] == '+' else 'понизить'} репутацию самому себе!")
    # репутация другому (так и надо)
    elif message.from_user.username != to_whom and message.text[0] in ["+", "-"]:
        db.updateReputation(message.chat.id, to_whom, message.text[0])
        db.setCooldown(message.chat.id, to_whom, time.time())
        bot.delete_message(message.chat.id, message.message_id)
        try:
            bot.send_message(message.chat.id, f"@{message.from_user.username} {'повышает' if message.text[0] == '+' else 'понижает'} репутацию @{to_whom}.\nПричина: {message.text.split(' ', 2)[2]}.")
        except IndexError:
            bot.send_message(message.chat.id, f"@{message.from_user.username} {'повышает' if message.text[0] == '+' else 'понижает'} репутацию @{to_whom}.\nПричина: нет.")


def main():
    logging.basicConfig(level=logging.INFO, filename=f"logs/logging_{datetime.datetime.today().strftime('%Y-%m-%d')}.log", filemode="w",
                        format="%(asctime)s %(levelname)s %(message)s")
    try:
        logging.info("Bot start")
        bot.polling(True)
    except requests.exceptions.ReadTimeout:
        logging.warning("ReadTimeout error. Restarting bot...")
    except Exception as error:
        logging.critical(f"Error:\n{error}", exc_info=True)

while __name__ == "__main__":
    main()