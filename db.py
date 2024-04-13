import sqlite3

def createTable(chat_id):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS 'chat_{str(chat_id).replace('-', '')}'(
        id INTEGER,
        username TEXT,
        reputation INTEGER,
        cooldown ITEGER
    );""")
    connect.commit()

def isUserInDB(chat_id, user_id):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    return cursor.execute(f"SELECT id from chat_{str(chat_id).replace('-', '')} WHERE id = {user_id}").fetchone()

def addUser(chat_id, user_id, username):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"INSERT INTO chat_{str(chat_id).replace('-', '')} VALUES('{user_id}', '{username}', 0, 0)")
    connect.commit()

def getStatistics(chat_id):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"""SELECT username, reputation FROM chat_{str(chat_id).replace('-', '')} ORDER BY reputation DESC""")
    return cursor.fetchall()

def getUserList(chat_id):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    members = cursor.execute(f"""SELECT username from chat_{str(chat_id).replace('-', '')}""")
    return members.fetchall()