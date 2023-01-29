import telebot
import sqlite3
import time
import random


TOKEN = ""
bot = telebot.TeleBot(TOKEN)


# регистрация пользователя в БД
@bot.message_handler(commands=['start'])
def start(message):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    if str(message.chat.id)[0] != "-":
        bot.send_message(message.chat.id, "Бот работает только для групповых чатов!")
        return 0
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS chat_{str(message.chat.id)[1:]}(
        id INTEGER,
        username TEXT,
        reputation INTEGER
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
        cursor.execute(f"INSERT INTO chat_{str(message.chat.id)[1:]} VALUES(?, ?, ?);", [id, username, 0])
        connect.commit()
        bot.send_message(message.chat.id, "Успешная регистрация!")
    else:
        bot.send_message(message.chat.id, "Ты уже регистрировался!")

# список команд бота
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Команды бота:\n/start – команда для регистрации, если вы ещё не сделали этого;\n/all – упомянуть всех людей в чате;\n/coinflip – подбросить монетку, чтобы решить спор;\n+rep @кому причина (не обязательно) – повысить репутацию пользователю. Например, <code>+rep @durov_russia спасибо за телегу</code>;\n-rep @кому причина – понизить репутацию пользователю. Синтаксис такой же;\n/statistics – топ пользователей по репутации в чате.", parse_mode='html')

# статистика по репутации всех пользователей чата
@bot.message_handler(commands=['statistics'])
def statistics(message):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"""SELECT username, reputation FROM chat_{str(message.chat.id)[1:]} ORDER BY reputation DESC""")
    record = cursor.fetchall()
    user_stat = "".join([user[0] + "   ---->   " + str(user[1]) + "\n" for user in record])
    bot.send_message(message.chat.id, f"Статистика репутации всех пользователей:\n{user_stat}")

# пинг всех пользователей
@bot.message_handler(commands=['all'])
def ping_all(message):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    members = cursor.execute(f"""SELECT username from chat_{str(message.chat.id)[1:]}""").fetchall()
    bot.delete_message(message.chat.id, message.message_id)
    members_list = "\n@".join([x[0] for x in members if x[0] != message.from_user.username])
    bot.send_message(message.chat.id, f"@{message.from_user.username} упоминает:\n\n@{members_list}")

# подбросить монетку
@bot.message_handler(commands=['coinflip'])
def coinflip(message):
    bot_message = bot.send_message(message.chat.id, f"@{message.from_user.username} подбрасывает монетку и выпадает...")
    time.sleep(1)
    bot.edit_message_text(f"{bot_message.text}\n<b>{'орёл' if random.randint(0, 1) == 0 else 'решка'}</b>{' – подкрутка? 🤨' if random.randint(0, 10) == 5 else ''}", message.chat.id, bot_message.message_id, parse_mode='html')

# добавление и отнимание репутации
@bot.message_handler(content_types=['text'])
def reputation(message):
    if message.text[:4] == '+rep' or message.text[:4] == '-rep':
        to_whom = message.text.split()[1][1:]
        # вставить ник будущего бота
        if to_whom == "test9443224bot":
            bot.send_message(message.chat.id, "Вы решили посягнуть на святое!")
            return 0
        if message.from_user.username != to_whom:
            connect = sqlite3.connect("data.db")
            cursor = connect.cursor()
            cursor.execute(f"SELECT username, reputation from chat_{str(message.chat.id)[1:]}")
            current = cursor.fetchall()
            for user in current:
                if user[0] == to_whom:
                    rep = user[1] + 1 if message.text[0] == "+" else user[1] - 1
            cursor.execute(f"""UPDATE chat_{str(message.chat.id)[1:]} set reputation = ? where username = ?""", (rep, to_whom))
            connect.commit()
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, f"@{message.from_user.username} {'повышает' if message.text[0] == '+' else 'понижает'} репутацию @{to_whom}.\nПричина: {message.text.split(' ', 2)[-1] if message.text.split(' ', 2)[-1] else 'нет'}.\nТеперь репутация равна {rep}")
        else:
            bot.send_message(message.chat.id, f"Нельзя {'повыcить' if message.text[0] == '+' else 'понизить'} репутацию самому себе!")

            
if __name__ == "__main__":
    bot.polling()
