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
    return cursor.execute(f"SELECT id from chat_{str(chat_id).replace('-', '')} WHERE id={user_id}").fetchone()

def isUserInDBByUsername(chat_id, username):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    return cursor.execute(f"SELECT id from chat_{str(chat_id).replace('-', '')} WHERE username='{username}'").fetchone()

def addUser(chat_id, user_id, username):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"INSERT INTO chat_{str(chat_id).replace('-', '')} VALUES('{user_id}', '{username}', 0, 0)")
    connect.commit()

def getStatistics(chat_id):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"SELECT username, reputation FROM chat_{str(chat_id).replace('-', '')} ORDER BY reputation DESC")
    return cursor.fetchall()

def getUserList(chat_id):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"SELECT username from chat_{str(chat_id).replace('-', '')}")
    return cursor.fetchall()

def getCooldown(chat_id, user_id):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"SELECT cooldown from chat_{str(chat_id).replace('-', '')} WHERE id={user_id}")
    return cursor.fetchone()[0]

def setCooldown(chat_id, username, timestamp):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"UPDATE chat_{str(chat_id).replace('-', '')} SET cooldown={timestamp} WHERE username='{username}'")
    connect.commit()

def updateReputation(chat_id, user_id, action):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"UPDATE chat_{str(chat_id).replace('-', '')} SET reputation=reputation{action}1 WHERE username='{user_id}'")
    connect.commit()