import sqlite3

class Database():
    def __init__(self, db_path="data.db"):
        self.connect = sqlite3.connect(db_path)
        self.cursor = self.connect.cursor()

    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        self.cursor.close()


    def createTable(self)->None:
        """
        Создание таблицы чата

        :param chat_id: ID чата, для которого надо проверить/создать таблицу
        :type chat_id: `int`

        :return: Создаёт таблицу, если необходимо
        :rtype: `None`
        """
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
            id INT NOT NULL,
            user_id INT NOT NULL,
            chat_id INT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            full_name TEXT,
            reputation INT DEFAULT 0,
            cooldown INT DEFAULT 0,
            is_active INT DEFAULT 1,
            PRIMARY KEY("id" AUTOINCREMENT)
        );""")

        self.connect.commit()

    def isUserInDB(self, chat_id: int, user_id: int)->sqlite3.Cursor | None:
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
        response = self.cursor.execute("SELECT user_id, username, full_name, is_active\
                                       FROM users\
                                       WHERE chat_id=? AND user_id=?",
                                       (chat_id, user_id))
        return response.fetchone()

    def updateUsername(self, user_id: int, new_username: str)->None:
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
        self.cursor.execute("UPDATE users\
                            SET username=?\
                            WHERE user_id=?",
                            (new_username, user_id))
        self.connect.commit()

    def updateFullName(self, user_id: int, new_full_name: str)->None:
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
        self.cursor.execute("UPDATE users\
                            SET full_name=?\
                            WHERE user_id=?",
                            (new_full_name, user_id))
        self.connect.commit()

    def isUserInDBByUsername(self, chat_id: int, username: str)->sqlite3.Cursor:
        """
        Проверка, есть ли пользователь в БД по его **username**

        :param chat_id: ID чата, в котором предположительно есть пользователь
        :type chat_id: `int`

        :param username: Username пользователя, наличие которого надо проверить в `chat_id`
        :type username: `str`

        :return: Если пользователь есть, массив `sqlite3.Cursor`, состоящий из id и username. Иначе – None
        :rtype: `sqlite3.Cursor | None`
        """
        response = self.cursor.execute("SELECT user_id\
                                       FROM users\
                                       WHERE chat_id=? AND username=? AND is_active=1",
                                       (chat_id, username))
        return response.fetchone()

    def addUser(self, chat_id: int, user_id: int, username: str, full_name: str)->None:
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
        self.cursor.execute("INSERT INTO users (chat_id, user_id, username, full_name)\
                            VALUES(?, ?, ?, ?)",
                            (chat_id, user_id, username, full_name))
        self.connect.commit()

    def getStatistics(self, chat_id: int)->list:
        """
        Получение репутации всех пользователей чата

        :param chat_id: ID чата
        :type chat_id: `int`

        :return: Массив пользователей. В каждом пользователе содержится информация о нём в виде `[id, username, full_name, reputation]`
        :rtype: `tuple[list[int, str, str, int]]`
        """
        response = self.cursor.execute("SELECT user_id, username, full_name, reputation\
                                       FROM users\
                                       WHERE chat_id=? AND is_active=1\
                                       ORDER BY reputation DESC",
                                       (chat_id,))
        return response.fetchall()

    def getUserList(self, chat_id: int)->list:
        """
        Получение списка пользователей чата

        :param chat_id: ID чата
        :type chat_id: `int`

        :return: Массив пользователей. В каждом пользователе содержится информация о нём в виде `[username]`
        :rtype: `list[list[str]]`
        """
        response = self.cursor.execute("SELECT user_id, username, full_name\
                                       FROM users\
                                       WHERE chat_id=? AND is_active=1",
                                       (chat_id,))
        return response.fetchall()

    def getCooldown(self, chat_id: int, user_id: int)->int:
        """
        Получение `cooldown` пользователя (timestamp последнего обращения к функции `reputation`)

        :param chat_id: ID чата
        :type chat_id: `int`

        :param user_id: ID пользователя
        :type user_id: `int`

        :return: Значение `timestamp` последнего использования команды `rep` пользователем в чате
        :rtype: `int`
        """
        response = self.cursor.execute("SELECT cooldown\
                                       FROM users\
                                       WHERE chat_id=? AND user_id=?",
                                       (chat_id, user_id))
        return response.fetchone()[0]

    def setCooldown(self, chat_id: int, user_id: int, timestamp: int | float)->None:
        """
        Установление нового значения `cooldown` для пользователя

        :param chat_id: ID чата
        :type chat_id: `int`

        :param user: ID пользователя
        :type user: `int`

        :param timestamp: Текущее значение `timestamp`
        :type timestamp: `int | float`

        :return: При успехе обновляет значение `timestamp`
        :rtype: `None`
        """
        self.cursor.execute("UPDATE users\
                            SET cooldown=?\
                            WHERE chat_id=? AND user_id=?",
                            (timestamp, chat_id, user_id))
        self.connect.commit()

    def updateReputation(self, chat_id: int, user: str | int, action: str)->None:
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
        if not action in ["+", "-"]:
            raise ValueError
        action = 1 if action == "+" else -1

        # идентификация по username
        if isinstance(user, str):
            self.cursor.execute("UPDATE users\
                                SET reputation=reputation+?\
                                WHERE chat_id=? AND username=?",
                                (action, chat_id, user))
        # идентификация по user_id (если username не задан)
        else:
            self.cursor.execute("UPDATE users\
                                SET reputation=reputation+?\
                                WHERE chat_id=? AND user_id=?",
                                (action, chat_id, user))
        self.connect.commit()

    def userActivation(self, chat_id: int, user_id: int)->None:
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
        self.cursor.execute("UPDATE users SET is_active=CASE\
                            WHEN is_active=1 THEN 0\
                            ELSE 1 END\
                            WHERE chat_id=? AND user_id=?",
                            (chat_id, user_id))
        self.connect.commit()