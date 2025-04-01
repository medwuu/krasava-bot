import datetime
import os
import time
import random
import logging
from logging.handlers import TimedRotatingFileHandler
import telebot
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from multipledispatch import dispatch

from db import Database


load_dotenv()
if not "TOKEN" in os.environ:
    print("Файл \".env\" не существует или переменная \"TOKEN\" не задана!")
    exit(1)
bot = telebot.TeleBot(os.getenv("TOKEN"))
db = Database(os.getenv("DATABASE_NAME", "data.db"))


@bot.message_handler(commands=['start'])
def start(message):
    """Регистрация пользователя в БД"""
    if message.chat.type != "supergroup":
        bot.send_message(message.chat.id, "Бот работает только для групповых чатов!")
        return
    # добавление бота
    if message.from_user.is_bot:
        return

    with Database() as db:
        db.createTable(message.chat.id)
        user_in_db = db.isUserInDB(message.chat.id, message.from_user.id)

    # добавление нового пользователя
    if not user_in_db:
        with Database() as db:
            db.addUser(message.chat.id, message.from_user.id, message.from_user.username, message.from_user.full_name)
        mention = getMention(message)
        bot.send_message(message.chat.id,
                         f"Привет, {mention}. Рад познакомиться с тобой! 😀\n" +
                         "Ты можешь посмотреть список моих команд, написав /help",
                         parse_mode='html', disable_notification=True)
        return
    # активация пользователя, который уже был в чате
    elif not user_in_db[3]:
        with Database() as db:
            db.userActivation(message.chat.id, message.from_user.id)
            db.setCooldown(message.chat.id, message.from_user.id, time.time())
        mention = getMention(message)
        bot.send_message(message.chat.id,
                        f"С возвращением, {mention}! Рад снова видеть тебя! 😀\n" +
                        "Если ты забыл мои команды, то можешь посмотреть их, написав /help",
                        parse_mode='html', disable_notification=True)
        return

    # обновление username
    if user_in_db[1] != str(message.from_user.username):
        with Database() as db:
            db.updateUsername(message.chat.id, message.from_user.id, message.from_user.username)
        if message.from_user.username:
            bot.send_message(message.chat.id,
                             "Ух ты! Вижу, ты обновил свой никнейм. Он тебе очень идёт. Теперь буду знать, что это именно ты 😉",
                             disable_notification=True)
        else:
            bot.send_message(message.chat.id,
                             "Ой-ой! Вижу, ты удалил свой никнейм. Надеюсь, на то есть веская причина. Не переживай, я всё ещё тебя узнаю 😉",
                             disable_notification=True)

    # обновление full_name. проверяется при каждом обращении к боту для поддержания актуальности данных
    if user_in_db[2] != message.from_user.full_name:
        with Database() as db:
            db.updateFullName(message.chat.id, message.from_user.id, message.from_user.full_name)

    else:
        # повторное прописывание "/start"
        if message.text == "/start":
            bot.send_message(message.chat.id, "Не нужно, мы уже знакомы 😊", disable_notification=True)

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
                    parse_mode='html', disable_notification=True)

@bot.message_handler(commands=['statistics'])
def statistics(message):
    """Статистика по репутации всех пользователей чата"""
    start(message)
    with Database() as db:
        records = db.getStatistics(message.chat.id)
    user_stat = "\n".join([getMention(*user[:-1]) + "   ---->   " + str(user[3]) for user in records])
    bot.send_message(message.chat.id, f"Статистика репутации всех пользователей:\n{user_stat}", parse_mode='html')

@bot.message_handler(commands=['all'])
def ping_all(message):
    """Пинг всех пользователей"""
    start(message)
    with Database() as db:
        members = db.getUserList(message.chat.id)
    bot.delete_message(message.chat.id, message.message_id)
    members_list = ", ".join([getMention(*x) for x in members if x[0] != message.from_user.id])
    bot.send_message(message.chat.id, f"{getMention(message)} упоминает всех\n<span class=\"tg-spoiler\">({members_list})</span>", parse_mode='html')

@bot.message_handler(commands=['coinflip'])
def coinflip(message):
    """Подбросить монетку (на базе [random.org](https://random.org))"""
    start(message)
    bot.delete_message(message.chat.id, message.message_id)
    min_num = 0
    max_num = 1
    r = requests.get(f"https://www.random.org/integers/?num=1&min={min_num}&max={max_num}&col=1&base=10&format=plain&rnd=new&cl=w")
    if r.ok:
        soup = BeautifulSoup(r.text, "html.parser")
        answer = int(soup.find("span").text.strip())
    # на случай ошибки с random.org
    else:
        bot.send_message(message.chat.id, "Произошла ошибка при обращении к random.org.\nБудет использован встроенный рандомайзер", disable_notification=True)
        answer = random.randint(0, 1)
    bot_message = bot.send_message(message.chat.id, f"{getMention(message)} подбрасывает монетку и выпадает...", parse_mode='html')
    time.sleep(2)
    bot.edit_message_text(f"{bot_message.text}\n<b>{'орёл' if answer == 0 else 'решка'}</b>{' – подкрутка? 🤨' if random.randint(0, 10) == 5 else ''}", message.chat.id, bot_message.message_id, parse_mode='html')


@bot.message_handler(content_types=['text'])
def text_handler(message):
    start(message)
    anyText(message)
    if message.chat.type != "supergroup":
        bot.send_message(message.chat.id, "Бот работает только для групповых чатов!")
        return
    if message.text.lower()[:4] in ['+rep', '-rep', '+реп', '-реп']:
        reputation(message)

@bot.message_handler(content_types=['new_chat_members'])
def newChatMembers(message):
    """Реакция на присоединение пользователя к чату"""
    start(message)

@bot.message_handler(content_types=['left_chat_member'])
def leftChatMember(message):
    """Реакция на выход пользователя из чата"""
    # выход бота
    if message.from_user.is_bot:
        return
    with Database() as db:
        db.userActivation(message.chat.id, message.from_user.id)
    bot.send_message(message.chat.id,
                     f"Мне очень жаль, что ты ушёл, <a href=\"tg://user?id={message.from_user.id}\">{message.from_user.full_name}</a> 😢", parse_mode='html',
                     disable_notification=True)


def anyText(message):
    """Функция, которая применяется для каждого сообщения"""
    if random.randint(0, 10)==0:
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

        r = requests.post(url, json=data)
        if not r.ok:
            logging.warning("Failed while sending message reaction!")

def reputation(message):
    """Добавление и отнимание репутации"""
    # проверка правильности написания команды
    try:
        if not message.entities:
            raise TypeError
        # с usernam'ом
        if message.entities[0].type == 'mention' and message.text.split()[1][0] == "@":
            to_whom = message.text.split()[1][1:]
            to_whom_mention = "@" + to_whom
        # без username
        elif message.entities[0].type == 'text_mention':
            to_whom = message.entities[0].user.id
            to_whom_mention = f'<a href=\"tg://user?id={to_whom}\">{message.entities[0].user.full_name}</a>'
        else:
            raise IndexError
    except (IndexError, TypeError):
        bot.send_message(message.chat.id,
                         "Ошибка при вводе команды. Проверьте синтаксис, написав команду /help",
                         disable_notification=True)
        return

    # репутация бота
    if to_whom == bot.get_me().username:
        if message.text[0] == "-":
            bot.send_message(message.chat.id,
                             f"Вы решили посягнуть на святое! Я конфисковать у вас {'кошка жена и ' if random.randint(0, 1) == 1 else ''}{random.randint(1, 10)} миска рис!",
                             disable_notification=True)
        else:
            bot.send_message(message.chat.id,
                             "Ой спасиба\n   🥺\n👉🏻 👈🏻",
                             disable_notification=True)
        return

    # есть ли пользователь в БД
    with Database() as db:
        if not db.isUserInDBByUsername(message.chat.id, to_whom) and not db.isUserInDB(message.chat.id, to_whom):
            bot.send_message(message.chat.id,
                             "Такого пользователя нет в чате или я ещё не знаком с ним. Попросите его написать тут что-то",
                             disable_notification=True)
            return

    # проверка на кулдаун
    with Database() as db:
        cooldown = db.getCooldown(message.chat.id, message.from_user.id)
    if round(time.time()) - cooldown < 3600:
        cooldown_remain = int(((time.time() - cooldown - 3600) / 60) // -1)
        bot.send_message(message.chat.id,
                         f"Изменять репутацию можно только раз в час! Попробуй снова через {cooldown_remain} минут{'ы' if cooldown_remain in [2, 3, 4] else 'у' if cooldown == 1 else ''}",
                         disable_notification=True)
        return

    # репутация себе
    if message.from_user.username == to_whom or message.from_user.id == to_whom:
        bot.send_message(message.chat.id,
                         f"Нельзя {'повыcить' if message.text[0] == '+' else 'понизить'} репутацию самому себе!",
                         disable_notification=True)
    # репутация другому (так и надо)
    else:
        with Database() as db:
            db.updateReputation(message.chat.id, to_whom, message.text[0])
            db.setCooldown(message.chat.id, message.from_user.id, time.time())
        bot.delete_message(message.chat.id, message.message_id)
        if len(message.text.split(' ')) > 2:
            reputation_reason = message.html_text.split(' ', 2)[2]
            if len(reputation_reason) > 100:
                bot.send_message(message.chat.id,
                                 "Причина слишком длинная! Сообщение будет обрезано до 100 символов",
                                 disable_notification=True)
                reputation_reason = message.text.split(' ', 2)[2][:100] + "..."
            bot.send_message(message.chat.id, f"{getMention(message)} {'повышает' if message.text[0] == '+' else 'понижает'} репутацию {to_whom_mention}.\nПричина: {reputation_reason}.", parse_mode='html')
        else:
            bot.send_message(message.chat.id, f"{getMention(message)} {'повышает' if message.text[0] == '+' else 'понижает'} репутацию {to_whom_mention}.\nПричина: нет.", parse_mode='html')


@dispatch(telebot.types.Message)
def getMention(message: telebot.types.Message)->str:
    """
    Определяет вид упоминания пользователя (у функции есть перегрузка, см. ниже)

    :param message: "сырое" сообщение от пользователя
    :type message: `telebot.types.Message`

    :return: @username (при наличии) или ссылка вида @full_name (html разметка и ссылка вида tg://user?id=xxxxxxx)
    :rtype: `str`
    """
    if message.from_user.username and message.from_user.username != 'None':
        mention = "@" + message.from_user.username
    else:
        mention = f"<a href=\"tg://user?id={message.from_user.id}\">{message.from_user.full_name}</a>"
    return mention

@dispatch(int, str, str)
def getMention(id: int, username: str, full_name: str)->str:
    """
    Определяет вид упоминания пользователя (у функции есть перегрузка, см. выше)

    :param id: ID пользователя
    :type user_id: `int`

    :param username: Username пользователя
    :type username: `str`

    :param full_name: Имя пользователя (не путать с username)
    :type username: `str`

    :return: @username (при наличии) или ссылка вида @full_name (html разметка и ссылка вида tg://user?id=xxxxxxx)
    :rtype: `str`
    """
    if username and username != 'None':
        mention = "@" + username
    else:
        mention = f"<a href=\"tg://user?id={id}\">{full_name}</a>"
    return mention


def setupLogger()->logging.Logger:
    """
    Настройка логгера (`logging.Logger`)

    :return: экземпляр логгера
    :rtype: logging.Logger
    """
    if not os.path.exists("logs/"):
        os.makedirs("logs/")

    logger = logging.getLogger("BotLogger")
    logger.setLevel(logging.INFO)
    log_format = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    log_file = f"logs/logging_{datetime.datetime.today().strftime('%Y-%m-%d')}.log"
    handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=30)
    handler.setFormatter(log_format)

    if logger.handlers:
        logger.handlers.clear()
    logger.addHandler(handler)
    return logger


def main():
    logging = setupLogger()
    try:
        logging.info("Bot start")
        bot.polling(True)
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
        logging.warning("Requests lib error. Restarting bot...\n\n")
    except Exception as error:
        logging.critical(f"Unexpected error:\n{error}", exc_info=True)

while __name__ == "__main__":
    main()