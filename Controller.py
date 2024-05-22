import time

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from mavsdk import System
import asyncio

from mavsdk.offboard import VelocityNedYaw, VelocityBodyYawspeed

from Track import TrackDevice


class DroneController(QObject):
    drone_connected = pyqtSignal(bool, str)

    def __init__(self, track_device=TrackDevice()):
        super().__init__()
        self.drone = System()
        self.track_device = track_device
        self.on_flight = False

    async def connect_drone(self):
        await self.drone.connect(system_address="udp://:14540")
        print("Waiting for drone to connect...")

        async for state in self.drone.core.connection_state():
            if state.is_connected:
                print("Drone connected!")
                async for health in self.drone.telemetry.health():
                    if health.is_global_position_ok and health.is_home_position_ok:
                        print("-- Global position estimate OK")
                        break
                self.drone_connected.emit(True, "Drone connected!")
                return True
        self.drone_connected.emit(False, "Drone failed to connect.")
        return False

    async def calibrate(self):
        print("-- Starting gyroscope calibration")
        async for progress_data in self.drone.calibration.calibrate_gyro():
            print(progress_data)
        print("-- Gyroscope calibration finished")

        print("-- Starting accelerometer calibration")
        async for progress_data in self.drone.calibration.calibrate_accelerometer():
            print(progress_data)
        print("-- Accelerometer calibration finished")

        print("-- Starting magnetometer calibration")
        """async for progress_data in self.drone.calibration.calibrate_magnetometer():
            print(progress_data)
        print("-- Magnetometer calibration finished")

        print("-- Starting board level horizon calibration")
        async for progress_data in self.drone.calibration.calibrate_level_horizon():
            print(progress_data)
        print("-- Board level calibration finished")"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Default)
        msg.setText("An error occurred")
        msg.setInformativeText("Калибровка выполнена успешно")
        msg.setWindowTitle("Error")
        msg.exec_()
    async def start_drone(self):
        print("Arming the drone...")
        await self.drone.action.arm()

        print("Taking off...")
        await self.drone.action.takeoff()
        await asyncio.sleep(5)
        await self.drone.offboard.set_velocity_ned(VelocityNedYaw(1.0, 0.0, 0.0, 0.0))
        await self.drone.offboard.start()
        self.on_flight = True
        return True

    async def stop_drone(self):
        self.on_flight = False
        print("Landing the drone...")
        await self.drone.offboard.stop()
        await self.drone.action.land()

    async def control_drone(self):
        #self.track_device.start_tracking()

            print(TrackDevice.roadmap)
            mode = TrackDevice.roadmap["Mode"]
            vertical_param = TrackDevice.roadmap["vertical_param"]
            direction = TrackDevice.roadmap["direction"]
            if mode == "hover":
                await self.hover_drone()
            elif mode == "vertical":
                await self.updown_drone(vertical_param)
            elif mode == "horizontal":
                #print(direction)
                await self.setDirection_drone(direction)
            #time.sleep(2)


    async def hover_drone(self):
        await self.drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.2, 0.0))
        await asyncio.sleep(5)

    async def updown_drone(self, vertical_param):
        await self.drone.offboard.set_velocity_ned(VelocityNedYaw(0, 0, vertical_param, 0))
        await asyncio.sleep(2)


    async def setDirection_drone(self, direction):
        #print("Setting direction...")
        yaw, roll, pitch = False, False, False
        yawspeed, rollspeed, pitchspeed = None, None, None
        #print("Setting yaw...")
        if direction[0] in (0, 1) and direction[1] in (0, 0.5):
            yaw = True
            yawspeed = VelocityBodyYawspeed(1, 0, 0, -10+20*direction[0])
        elif direction[0] == 0 and direction[1] == 1 or direction[0] == 1 and direction[1] == 0:
            roll = True
            rollspeed = VelocityBodyYawspeed(1, direction[0]-0.5, 0, 0)
        elif direction[1] in (0, 1):
            pitch = True
            pitchspeed = VelocityBodyYawspeed(2 - direction[1] * 1.5, 0, 0, 0)
        if yaw:
            await self.drone.offboard.set_velocity_body(yawspeed)
        elif roll:
            await self.drone.offboard.set_velocity_body(rollspeed)
        elif pitch:
            await self.drone.offboard.set_velocity_body(pitchspeed)
        else:
            await self.drone.offboard.set_velocity_ned(VelocityNedYaw(1.0, 0.0, 0.0, 0.0))
        await asyncio.sleep(2)