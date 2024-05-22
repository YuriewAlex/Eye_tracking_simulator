# Модуль для симулятора PX4 Gazebo

Этот модуль позволяет управлять моделями дронов в симуляторе PX4 Gazebo при помощи взгляда. Для его использования необходимо устройство отслеживания взгляда Tobii.

## Требования

- Ubuntu 20.04
- Устройство отслеживания взгляда Tobii

## Установка

Для установки модуля выполните следующую команду в терминале:

```sh
sudo ./firmware_setup.sh
```
## Запуск через Docker контейнер


Для запуска Docker контейнера выполните следующие команды в терминале:


```sh
docker build -t my_px4_image .
xhost +local:root
docker run -it \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /path/to/your/Tracker:/Tracker \
    --device=/dev/dri \
    my_px4_image
```
