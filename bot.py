import telebot
import sqlite3

TOKEN = ""
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        id INT,
        username TEXT,
        reputation INT
    );""")
    connect.commit()
    id = message.from_user.id
    user_check = cursor.execute(f"SELECT id from users WHERE id = {id}").fetchone()
    if user_check is None:
        if message.from_user.username:
            username = message.from_user.username
        elif message.from_user.last_name:
            username = " ".join([message.from_user.first_name, message.from_user.last_name])
        else:
            username = message.from_user.first_name
        cursor.execute("INSERT INTO users VALUES(?, ?, ?);", [id, username, 0])
        connect.commit()
        bot.send_message(message.chat.id, "Успешная регистрация!")
    else:
        bot.send_message(message.chat.id, "Ты уже регистрировался!")

@bot.message_handler(commands=['statistics'])
def statistics(message):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute("""SELECT username, reputation FROM users ORDER BY reputation DESC""")
    record = cursor.fetchall()
    user_stat = "".join([user[0] + "   ---->   " + str(user[1]) + "\n" for user in record])
    bot.send_message(message.chat.id, f"Статистика репутации всех пользователей:\n{user_stat}")

@bot.message_handler(commands=['all'])
def ping_all(message):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    members = cursor.execute("""SELECT username from users""").fetchall()
    bot.delete_message(message.chat.id, message.message_id)
    members_list = "\n@".join([x[0] for x in members if x[0] != message.from_user.username])
    bot.send_message(message.chat.id, f"@{message.from_user.username} упоминает:\n\n@{members_list}")


@bot.message_handler(content_types=['text'])
def reputation(message):
    if message.text[:4] == '+rep' or message.text[:4] == '-rep':
        to_who = message.text.split()[1][1:]
        # вставить ник будущего бота
        if to_who == "test9443224bot":
            bot.send_message(message.chat.id, "Вы решили посягнуть на святое!")
            return 0
        if message.from_user.username != to_who:
            connect = sqlite3.connect("data.db")
            cursor = connect.cursor()
            cursor.execute(f"SELECT username, reputation from users")
            current = cursor.fetchall()
            for user in current:
                if user[0] == to_who:
                    rep = user[1] + 1 if message.text[0] == "+" else user[1] - 1
            cursor.execute(f"""UPDATE users set reputation = ? where username = ?""", (rep, to_who))
            connect.commit()
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, f"@{message.from_user.username} {'повышает' if message.text[0] == '+' else 'понижает'} репутацию @{to_who}.\nПричина: {message.text.split(' ', 2)[-1] if message.text.split(' ', 2)[-1] else 'нет'}.\nТеперь репутация равна {rep}")
        else:
            bot.send_message(message.chat.id, f"Нельзя {'повыcить' if message.text[0] == '+' else 'понизить'} репутацию самому себе!")


if __name__ == "__main__":
    bot.polling()