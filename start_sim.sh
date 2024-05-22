#!/bin/bash

# Проверка наличия аргумента
if [ -z "$1" ]; then
    echo "Usage: $0 <world_name>"
    exit 1
fi

# Имя мира
WORLD_NAME="$1"

# Путь к директории
FIRMWARE_PATH="$HOME/pxh/Firmware"

# Команда для выполнения
COMMAND=" sudo make px4_sitl gazebo-classic_typhoon_h480__$WORLD_NAME"

# Переход в указанную директорию
cd "$FIRMWARE_PATH" || { echo "Directory not found: $FIRMWARE_PATH"; exit 1; }

# Выполнение команды
$COMMAND