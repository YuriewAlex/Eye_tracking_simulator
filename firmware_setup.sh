#!/bin/bash

current_dir=$(pwd)

cd /

sudo mkdir /my_px4_directory

cd /my_px4_directory

sudo git clone https://github.com/PX4/PX4-Autopilot.git --recursive

cd PX4-Autopilot

bash ./Tools/setup/ubuntu.sh


cd "$current_dir"

mkdir -p apps

cd apps

wget https://d176tv9ibo4jno.cloudfront.net/latest/QGroundControl.AppImage -O QGroundControl.AppImage


chmod +x QGroundControl.AppImage


echo "PX4-Autopilot успешно установлен и настройка завершена."
echo "Приложение QGroundControl загружено в папку 'apps' и готово к использованию."

# Проверить наличие Python 3.8
python_version=$(python3.8 --version 2>&1)
if [[ $python_version == *"Python 3.8"* ]]; then
    echo "Python 3.8 уже установлен: $python_version"
else
    echo "Python 3.8 не найден, устанавливаю..."
    sudo apt update
    sudo apt install -y python3.8 python3.8-venv python3.8-dev
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
    sudo update-alternatives --set python3 /usr/bin/python3.8
fi


python3.8 -m ensurepip --upgrade
python3.8 -m pip install --upgrade pip

python3.8 -m pip install PyQt5 asyncio tobii_research mavsdk pyqt-sip PyQtWebEngine

echo "Все необходимые библиотеки успешно установлены."