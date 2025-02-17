#!/bin/bash

function print_error {
    echo "$1" 1>&2
    exit 1
}

SERVICE_NAME="krasava-bot.service"

# Проверка, выполняется ли скрипт с правами root
if [ "$EUID" -ne 0 ]; then
    print_error "Пожалуйста, запустите скрипт с правами суперпользователя (sudo)."
fi

# Проверка, есть ли сервис
if ! systemctl list-units --full -all | grep -Fq "$SERVICE_NAME"; then
    echo "Нет сервиса $SERVICE_NAME!"
    exit 1
fi

echo "Начинаю процесс удаления сервиса $SERVICE_NAME..."

# Остановка сервиса
systemctl stop $SERVICE_NAME || print_error "Не удалось остановить сервис $SERVICE_NAME!"

# Отключение сервиса
systemctl disable $SERVICE_NAME || print_error "Не удалось отключить сервис $SERVICE_NAME!"

# Удаление файла сервиса
rm /etc/systemd/system/$SERVICE_NAME || print_error "Не удалось удалить файл сервиса $SERVICE_NAME!"

# Перезагрузка демона Systemd
systemctl daemon-reload || print_error "Не удалось перезагрузить демона Systemd!"

echo "Сервис $SERVICE_NAME успешно удалён и отключён!"