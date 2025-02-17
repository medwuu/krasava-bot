#!/bin/bash

function print_error {
    echo "$1" 1>&2
    exit 1
}

# Проверка, выполняется ли скрипт с правами root
if [ "$EUID" -ne 0 ]; then
    print_error "Пожалуйста, запустите скрипт с правами суперпользователя (sudo)."
fi

# Получение текущего пользователя
USER=$(logname)
GROUP=$USER

# Путь к домашней директории пользователя
if pwd | grep "krasava-bot" ; then
    PROJECT_DIR=$(pwd)
else
    PROJECT_DIR="$(pwd)/krasava-bot"
fi

# Параметры проекта
SERVICE_NAME="krasava-bot.service"
VENV_DIR="$PROJECT_DIR/.venv"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"
BOT_SCRIPT="$PROJECT_DIR/bot.py"
DB_SCRIPT="$PROJECT_DIR/db.py"
ENV_FILE="$PROJECT_DIR/.env"

# Проверка существования директории проекта
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Директория проекта не найдена: $PROJECT_DIR"
fi

# Проверка существования файла requirements.txt
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    print_error "Файл requirements.txt не найден: $REQUIREMENTS_FILE"
fi

# Проверка существования файла бота
if [ ! -f "$BOT_SCRIPT" ]; then
    print_error "Файл бота не найден: $BOT_SCRIPT"
fi

# Проверка существования файла скрипта базы данных
if [ ! -f "$DB_SCRIPT" ]; then
    print_error "Скрипт базы данных не найден: $DB_SCRIPT"
fi

# Проверка существования файла .env
if [ ! -f "$ENV_FILE" ]; then
    print_error "Файл переменных окружения не найден: $ENV_FILE"
fi

# Создание виртуального окружения, если оно не существует
if [ ! -d "$VENV_DIR" ]; then
    echo "Создание виртуального окружения в $VENV_DIR..."
    python3 -m venv "$VENV_DIR" || print_error "Не удалось создать виртуальное окружение."
    echo "Виртуальное окружение успешно создано."
fi

# Установка зависимостей из requirements.txt
echo "Установка зависимостей из $REQUIREMENTS_FILE..."
source "$VENV_DIR/bin/activate" || print_error "Не удалось активировать виртуальное окружение."
pip install --upgrade pip --quiet || print_error "Не удалось обновить pip."
pip install -r $REQUIREMENTS_FILE --quiet || print_error "Не удалось установить зависимости."
deactivate
echo "Зависимости успешно установлены."

# Путь к файлу сервиса systemd
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"

# Генерация содержимого сервиса
SERVICE_CONTENT="[Unit]
Description=Krasava-bot Service
After=network.target

[Service]
Type=simple
User=$USER
Group=$GROUP
WorkingDirectory=$PROJECT_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$VENV_DIR/bin/python3 $BOT_SCRIPT
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"

# Создание файла сервиса
echo "$SERVICE_CONTENT" > /tmp/$SERVICE_NAME

# Установка правильных прав доступа
chmod 644 /tmp/$SERVICE_NAME

# Перемещение файла сервиса в директорию systemd
mv /tmp/$SERVICE_NAME "$SERVICE_FILE" || print_error "Не удалось переместить файл сервиса в $SERVICE_FILE"

echo "Файл сервиса $SERVICE_NAME успешно создан."

# Перезагрузка конфигурации systemd
systemctl daemon-reload || print_error "Не удалось перезагрузить конфигурацию systemd."

# Включение сервиса для автозапуска при старте системы
systemctl enable "$SERVICE_NAME" || print_error "Не удалось включить сервис $SERVICE_NAME."

# Запуск сервиса
systemctl start "$SERVICE_NAME" || print_error "Не удалось запустить сервис $SERVICE_NAME."

echo "Сервис $SERVICE_NAME успешно запущена и включена для автозапуска."

# Вывод статуса сервиса
systemctl status "$SERVICE_NAME" --no-pager