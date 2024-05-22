#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <world_name>"
    exit 1
fi

WORLD_NAME="$1"

FIRMWARE_PATH="$HOME/px4_directory/PX4-Autopilot"

COMMAND=" sudo make px4_sitl gazebo-classic_typhoon_h480__$WORLD_NAME"

cd "$FIRMWARE_PATH" || { echo "Directory not found: $FIRMWARE_PATH"; exit 1; }

$COMMAND