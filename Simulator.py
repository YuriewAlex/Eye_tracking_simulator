import subprocess


class GazeboSimulator:
    def __init__(self, qgroundcontrol_path="/home/alex/Apps/QGroundControl.AppImage",
                 world="empty"):
        self.qgroundcontrol_path = qgroundcontrol_path
        self.gazebo_loader = "./start_sim.sh"
        self.world = world

    def start_simulator(self):
        command = [self.gazebo_loader, self.world]
        subprocess.call(["chmod", "+x", self.gazebo_loader])
        process = subprocess.Popen(command, shell=False)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            print(f"Output:\n{stdout}")
        else:
            print(f"Error occurred: {stderr}")
        subprocess.call(["chmod", "+x", self.qgroundcontrol_path])

        subprocess.Popen([self.qgroundcontrol_path])

    def stop_simulator(self):
        subprocess.call(["sudo", "pkill", "px4"])
        subprocess.call(["pkill", "QGroundControl"])

    def set_world(self, world):
        self.world = world


