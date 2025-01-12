import sqlite3

def createTable(chat_id: int)->None:
    """
    Создание таблицы чата

    :param chat_id: ID чата, для которого надо проверить/создать таблицу
    :type chat_id: `int`

    :return: Создаёт таблицу, если необходимо
    :rtype: `None`
    """
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS 'chat_{str(chat_id).replace('-', '')}'(
        id INT NOT NULL UNIQUE,
        username TEXT NOT NULL UNIQUE,
        full_name TEXT,
        reputation INT DEFAULT 0,
        cooldown INT DEFAULT 0,
        is_active INT DEFAULT 1,
        PRIMARY KEY("id")
    );""")
    connect.commit()

def isUserInDB(chat_id: int, user_id: int)->sqlite3.Cursor | None:
    """
    Проверка, есть ли пользователь в БД по его **ID**

    :param chat_id: ID чата, в котором предположительно находится пользователь
    :type chat_id: `int`

    :param user_id: ID пользователя, наличие которого надо проверить в `chat_id`
    :type user_id: `int`

    :return: Если пользователь есть, массив `sqlite3.Cursor`, состоящий из:
    `[id, username, full_name и "был ли пользователь раньше в этом чате"]`. Иначе – None
    :rtype: `sqlite3.Cursor | None`
    """
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    return cursor.execute(f"SELECT id, username, full_name, is_active FROM chat_{str(chat_id).replace('-', '')} WHERE id='{user_id}'").fetchone()

def updateUsername(chat_id: int, user_id: int, new_username: str)->None:
    """
    Обновление usernam'а пользователя в БД

    :param chat_id: ID чата, в котором предположительно находится пользователь
    :type chat_id: `int`

    :param user_id: ID пользователя
    :type user_id: `int`

    :param new_username: Новый username
    :type new_username: `str`

    :return: В случае успеха обновляет username
    :rtype: `None`
    """
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"UPDATE chat_{str(chat_id).replace('-', '')} SET username='{new_username}' WHERE id={user_id}")
    connect.commit()

def updateFullName(chat_id: int, user_id: int, new_full_name: str)->None:
    """
    Обновление full_nam'а пользователя в БД

    :param chat_id: ID чата, в котором предположительно находится пользователь
    :type chat_id: `int`

    :param user_id: ID пользователя
    :type user_id: `int`

    :param new_full_name: Новый full_name
    :type new_full_name: `str`

    :return: В случае успеха обновляет full_name
    :rtype: `None`
    """
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"UPDATE chat_{str(chat_id).replace('-', '')} SET full_name='{new_full_name}' WHERE id={user_id}")
    connect.commit()

def isUserInDBByUsername(chat_id: int, username: str)->sqlite3.Cursor:
    """
    Проверка, есть ли пользователь в БД по его **username**

    :param chat_id: ID чата, в котором предположительно есть пользователь
    :type chat_id: `int`

    :param username: Username пользователя, наличие которого надо проверить в `chat_id`
    :type username: `str`

    :return: Если пользователь есть, массив `sqlite3.Cursor`, состоящий из id и username. Иначе – None
    :rtype: `sqlite3.Cursor | None`
    """
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    return cursor.execute(f"SELECT id from chat_{str(chat_id).replace('-', '')} WHERE username='{username}'").fetchone()

def addUser(chat_id: int, user_id: int, username: str, full_name: str)->None:
    """
    Добавление нового пользователя

    :param chat_id: ID чата
    :type chat_id: `int`

    :param user_id: ID пользователя
    :type user_id: `int`

    :param username: Username пользователя
    :type username: `str`

    :param full_name: Имя пользователя (не путать с username)
    :type full_name: `str`

    :return: Добавляет пользователя при успехе
    :rtype: `None`
    """
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"INSERT INTO chat_{str(chat_id).replace('-', '')} VALUES('{user_id}', '{username}', '{full_name}', 0, 0)")
    connect.commit()

def getStatistics(chat_id: int)->list:
    """
    Получение репутации всех пользователей чата

    :param chat_id: ID чата
    :type chat_id: `int`

    :return: Массив пользователей. В каждом пользователе содержится информация о нём в виде `[id, username, full_name, reputation]`
    :rtype: `tuple[list[int, str, str, int]]`
    """
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"SELECT id, username, full_name, reputation FROM chat_{str(chat_id).replace('-', '')} WHERE is_active=1 ORDER BY reputation DESC")
    return cursor.fetchall()

def getUserList(chat_id: int)->list:
    """
    Получение списка пользователей чата

    :param chat_id: ID чата
    :type chat_id: `int`

    :return: Массив пользователей. В каждом пользователе содержится информация о нём в виде `[username]`
    :rtype: `list[list[str]]`
    """
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"SELECT id, username, full_name FROM chat_{str(chat_id).replace('-', '')} WHERE is_active=1")
    return cursor.fetchall()

def getCooldown(chat_id: int, user_id: int)->int:
    """
    Получение `cooldown` пользователя (timestamp последнего обращения к функции `reputation`)

    :param chat_id: ID чата
    :type chat_id: `int`

    :param user_id: ID пользователя
    :type user_id: `int`

    :return: Значение `timestamp` последнего использования команды `rep` пользователем в чате
    :rtype: `int`
    """
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"SELECT cooldown from chat_{str(chat_id).replace('-', '')} WHERE id={user_id}")
    return cursor.fetchone()[0]

def setCooldown(chat_id: int, user: str | int, timestamp: int | float)->None:
    """
    Установление нового значения `cooldown` для пользователя

    :param chat_id: ID чата
    :type chat_id: `int`

    :param user: Username (если задан) или ID пользователя
    :type user: `str | int`

    :param timestamp: Текущее значение `timestamp`
    :type timestamp: `int`

    :return: При успехе обновляет значение `timestamp`
    :rtype: `None`
    """
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()

    # идентификация по username
    if type(user) == str:
        cursor.execute(f"UPDATE chat_{str(chat_id).replace('-', '')} SET cooldown={timestamp} WHERE username='{user}'")
    # идентификация по id (если username не задан)
    else:
        cursor.execute(f"UPDATE chat_{str(chat_id).replace('-', '')} SET cooldown={timestamp} WHERE id='{user}'")
    connect.commit()

def updateReputation(chat_id: int, user: str | int, action: str)->None:
    """
    Обновление репутации пользователя

    :param chat_id: ID чата
    :type chat_id: `int`

    :param user: Username (если задан) или ID пользователя
    :type user: `str | int`

    :param action: Повышение `+` или понижение `-` репутации
    :type action: `str` (`+ | -`)

    :return: При успехе обновляет репутацию
    :rtype: `None`
    """
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()

    # идентификация по username
    if type(user) == str:
        cursor.execute(f"UPDATE chat_{str(chat_id).replace('-', '')} SET reputation=reputation{action}1 WHERE username='{user}'")
    # идентификация по id (если username не задан)
    else:
        cursor.execute(f"UPDATE chat_{str(chat_id).replace('-', '')} SET reputation=reputation{action}1 WHERE id='{user}'")
    connect.commit()

def userActivation(chat_id: int, user_id: int)->None:
    """
    Изменение состояния "активации" пользователя из базы данных.
    Значение может быть равно `0` (пользователь был в чате, но вышел) или `1` (пользователь сейчас в чате)

    :param chat_id: ID чата
    :type chat_id: `int`

    :param user_id: ID пользователя
    :type user_id: `int`

    :return: При успехе меняет значение `is_active` в БД
    :rtype: `None`
    """
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute(f"UPDATE chat_{str(chat_id).replace('-', '')} SET 'is_active'= CASE\
                   WHEN is_active = 1 THEN 0\
                   ELSE 1 END\
                   WHERE id={user_id}")
    connect.commit()