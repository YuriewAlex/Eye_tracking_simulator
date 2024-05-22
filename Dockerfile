FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    sudo \
    git \
    wget \
    python3.8 \
    python3.8-venv \
    python3.8-dev \
    python3-pip \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libglu1-mesa-dev freeglut3-dev mesa-common-dev \
    && apt-get clean

# Set Python 3.8 as the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1 && \
    update-alternatives --set python3 /usr/bin/python3.8

# Upgrade pip and install required Python libraries
RUN python3.8 -m pip install --upgrade pip && \
    python3.8 -m pip install PyQt5 asyncio tobii_research mavsdk pyqt-sip PyQtWebEngine

# Create a directory for the PX4-Autopilot repository
RUN mkdir -p /root/my_px4_directory

# Clone the PX4-Autopilot repository and run the setup script
RUN cd /root/my_px4_directory && \
    git clone https://github.com/PX4/PX4-Autopilot.git --recursive && \
    cd PX4-Autopilot && \
    bash ./Tools/setup/ubuntu.sh

# Create an apps directory and download QGroundControl
RUN mkdir -p /root/apps && \
    cd /root/apps && \
    wget https://d176tv9ibo4jno.cloudfront.net/latest/QGroundControl.AppImage -O QGroundControl.AppImage && \
    chmod +x QGroundControl.AppImage

# Set the working directory to /Tracker
WORKDIR /Tracker

# Mount the Tracker directory from the host
VOLUME ["/Tracker"]

# Set the entrypoint to run App.py
ENTRYPOINT ["python3", "App.py"]