import os
import time

import tobii_research as tr
from PyQt5.QtCore import pyqtSignal, QObject


class TrackDevice(QObject):
    calibration_signal = pyqtSignal(str)
    roadmap = {"Mode": "hover", "vertical_param": 0.0, "direction": (0.0, 0.0)}  # Параметры для обработки взгляда
    vertical_speed_threshold = 0.1
    vertical_move_time_threshold = 0.2
    last_gaze_y = None
    last_gaze_time = None
    diameter_threshold = 0.5
    validity_threshold = 0.2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.device = None
        self.tracker_info = "Трекер не найден"
        self.calibration_data = {}

    def find_device(self):

        found_eyetrackers = tr.find_all_eyetrackers()
        if found_eyetrackers:
            self.device = found_eyetrackers[0]
            self.tracker_info = f"Подключен трекер: {self.device.model} (ID: {self.device.serial_number})"
            return True
        else:
            return False

    def start_tracking(self):
        if self.device:
            self.device.subscribe_to(tr.EYETRACKER_GAZE_DATA, TrackDevice.gaze_data_callback, as_dictionary=True)

    def stop_tracking(self):
        if self.device:
            self.device.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, TrackDevice.gaze_data_callback)

    @classmethod
    def gaze_data_callback(cls, gaze_data):

        left_gaze_point = gaze_data['left_gaze_point_on_display_area']
        right_gaze_point = gaze_data['right_gaze_point_on_display_area']
        average_x = (left_gaze_point[0] + right_gaze_point[0]) / 2
        average_y = (left_gaze_point[1] + right_gaze_point[1]) / 2
        print("AY " ,average_y)
        print("AX ", average_x)
        curr_time = time.time()
        print("time = ", curr_time)

        if cls.last_gaze_y is not None and cls.last_gaze_time is not None:
            gaze_y_diff = average_y - cls.last_gaze_y
            time_diff = curr_time - cls.last_gaze_time
            print("In first", gaze_y_diff, " ", time_diff, " seconds")
            if abs(gaze_y_diff) > cls.vertical_speed_threshold and time_diff < cls.vertical_move_time_threshold:
                if gaze_y_diff > 0:
                    down_speed = -1.0
                else:
                    down_speed = 1.0
                cls.roadmap["Mode"] = "vertical"
                cls.roadmap["vertical_param"] = down_speed #Установка вертикальной скорости
                return
        cls.last_gaze_y = average_y
        cls.last_gaze_time = curr_time
        left_pupil_diameter = gaze_data["left_pupil_diameter"] # Определение моргания
        right_pupil_diameter = gaze_data["right_pupil_diameter"]
        left_pupil_validity = gaze_data["left_pupil_validity"]
        right_pupil_validity = gaze_data["right_pupil_validity"]
        if left_pupil_diameter < cls.diameter_threshold and right_pupil_diameter < cls.diameter_threshold or left_pupil_validity < cls.validity_threshold and right_pupil_validity < cls.validity_threshold:
            cls.roadmap["Mode"] = "hover"
            return

        direction_x = round(average_x / 0.5) * 0.5
        direction_y = round(average_y / 0.5) * 0.5
        cls.roadmap["Mode"] = "horizontal"
        cls.roadmap["direction"] = (direction_x, direction_y)
        return
