# ![Krasava bot](https://github.com/user-attachments/assets/6ce39da9-8203-4217-adaa-958e0a8ccc08)

[![Python3.v11+](https://img.shields.io/badge/Python-v3.11+-ffde71)](https://www.python.org/)
[![Telegram Bot API v8.0](https://img.shields.io/badge/Telegram%20Bot%20API-v8.0-3ab2ee.svg)](https://core.telegram.org/bots/api)
[![Pet Project](https://img.shields.io/badge/Pet%20Project-🐶-fff)](https://github.com/medwuu)
[![MIT license](https://img.shields.io/badge/MIT%20license-⚖️-fff)](https://github.com/medwuu/krasava-bot/blob/main/LICENSE)
[![Issues friendly](https://img.shields.io/badge/Issues%20friendly-🤗-fff)](https://github.com/medwuu/krasava-bot/issues)

## О боте:
`Krasava bot`, или просто `Красавчик` – это бот, который разнообразит опыт общения в чатах.

## Основные возможности:
* 👋🏻 Автоматичское приветствие новых пользователей;
* 🫡 А также прощание с ними;
* 📢 Упоминание всех пользователей чата;
* 🪙 Подброс монетки (с использованием сервиса [random.org](https://random.org));
* 📈 Система репутации (возможность добавления и отнятия очков, просмотр общей статистики);
* 🤩 Реакция бота на сообщения (рандомная реакция с вероятностью 10%);
* 🫱🏻‍🫲🏻 Также бот будет повторять реакции на сообщения другим пользователям за Вами (не более одной на сообщение).

## Добавление бота себе в чат:
✅ Бот [уже запущен](https://t.me/mirea_krasawa_bot). Вам достаточно добавить его в свой чат и выдать ему права администратора.
<details>
<summary>Необходимый минимум разрешений бота (фото)</summary>

![Изменение профиля группы, удаление и закрепление сообщений. По желанию можно добавить смешную должность боту](https://github.com/user-attachments/assets/4e475fe5-9165-424f-86e5-dcbc2cc66b64)
</details>

---
👋🏻 Поздоровайтесь с ботом, написав что-нибудь в чат, например `/start`.

## Установка сервиса (только для Linux):
1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/medwuu/krasava-bot.git
    cd krasava-bot
    ```

2. Создайте и заполните файл конфигурации:
    ```bash
    echo 'TOKEN="вставьте токен бота"' > .env
    ```

3. Выдайте права на запуск скриптов запуска и остановки сервиса:
    ```bash
    chmod -v +x krasava-bot/service_setup.sh krasava-bot/service_stop.sh
    ```

4. Запустите скритп автоматической установки сервиса:
    ```bash
    sudo ./krasava-bot/service_setup.sh
    ```
    Скрипт автоматически проверит существование необходимых файлов, создаст вируальное окружение (`.venv`), установит зависимости, установит сервис и запустит его

#### Готово! Теперь бот работает как сервис

- 🖐🏻 Остановить сервис можно командой
    ```bash
    sudo ./krasava-bot/service_stop.sh
    ```

## Ручной запуск (без сервиса):

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/medwuu/krasava-bot.git
    cd krasava-bot
    ```

2. Создайте и активируйте вируальное окружение:
* Windows:
    ```bash
    python3 -m venv .venv
    .venv\Scripts\activate
    ```
* Linux:
    ```bash
    : Если модуль venv не установлен
    sudo apt install python3-venv -y

    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

4. Создайте и заполните файл конфигурации:
    ```bash
    echo 'TOKEN="вставьте токен бота"' > .env
    ```

5. 🏁 Готово! Запустите бота
    ```bash
    python bot.py
    ```

6. 🖐🏻 Остановить бота можно сочетанием клавиш `Ctrl+C`

---

Понравился репозиторий? Поставь звёздочку ⭐