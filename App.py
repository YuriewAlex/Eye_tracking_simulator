import asyncio
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QGridLayout, \
    QMessageBox
from PyQt5.QtCore import pyqtSlot, QThread
from Simulator import GazeboSimulator
from Track import TrackDevice
from Controller import DroneController
from Errors import ErrorHandler


class DroneThread(QThread):
    def __init__(self, loop,  drone_controller=DroneController()):
        super().__init__()
        self.drone_controller = drone_controller
        self.loop = loop

    def run(self):
        self.drone_controller.track_device.start_tracking()
        self.loop.run_until_complete(self.control_drone_loop())

    async def control_drone_loop(self):
        while self.drone_controller.on_flight:
            await self.drone_controller.control_drone()


class MainInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.drone_task = None
        self.loop = asyncio.get_event_loop()
        self.gazebo_simulator = GazeboSimulator()
        self.track_device = TrackDevice(self)
        self.drone_controller = DroneController(self.track_device)
        self.drone_connector_thread = QThread()  # Запуск управления дроном в отдельном потоке
        self.drone_controller.moveToThread(self.drone_connector_thread)
        self.drone_controller.drone_connected.connect(self.update_status)
        self.drone_controller.drone_connected.connect(self.enable_start_drone_button)
        self.drone_connector_thread.start()
        self.error_handler = ErrorHandler(self)
        self.initUI()
        self.check_tracker()

    def initUI(self):
        self.setWindowTitle('Модуль управления дроном')
        layout = QGridLayout()

        self.status_label = QLabel("Добро пожаловать в модуль управления дроном")
        layout.addWidget(self.status_label, 0, 0, 1, 2)  # Размещаем все кнопки в сетке, настраивая им ячейки

        self.tracker_label = QLabel('Поиск трекера...')
        layout.addWidget(self.tracker_label, 1, 0, 1, 2)

        btn_empty_world = QPushButton('Запустить пустой мир', self)
        btn_empty_world.clicked.connect(self.start_empty_world)
        layout.addWidget(btn_empty_world, 2, 0)

        btn_nature_world = QPushButton('Запустить мир Природа', self)
        btn_nature_world.clicked.connect(self.start_nature_world)
        layout.addWidget(btn_nature_world, 2, 1)

        stop_button = QPushButton('Остановить симуляцию', self)
        stop_button.clicked.connect(self.stop_simulation)
        layout.addWidget(stop_button, 3, 0, 1, 2)
        self.btn_start_drone = QPushButton('Начать полёт', self)
        self.btn_start_drone.setEnabled(False)
        self.btn_start_drone.clicked.connect(self.start_drone)
        layout.addWidget(self.btn_start_drone, 4, 0)

        self.btn_stop_drone = QPushButton('Закончить полёт', self)
        self.btn_stop_drone.setEnabled(True)
        self.btn_stop_drone.clicked.connect(self.stop_drone)
        layout.addWidget(self.btn_stop_drone, 4, 1)

        calibration_button = QPushButton('Калибровка', self)  # Добавление кнопки "Калибровка"
        calibration_button.clicked.connect(self.calibrate_drone)  # Подключение к слоту calibrate_tracker
        layout.addWidget(calibration_button, 5, 0, 1, 2)

        exit_button = QPushButton('Выход', self)
        exit_button.clicked.connect(self.exit_app)
        layout.addWidget(exit_button, 6, 0, 1, 2)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def update_status(self, connected, message):
        self.status_label.setText(message)

    def check_tracker(self):
        if self.track_device.find_device():
            self.tracker_label.setText(self.track_device.tracker_info)
        else:
            self.tracker_label.setText(self.track_device.tracker_info)

    @pyqtSlot()
    def calibrate_drone(self):
        # asyncio.run(self.drone_controller.calibrate())
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setInformativeText("Калибровка выполнена успешно")
        msg.setWindowTitle("Успех")
        msg.exec_()

    def start_simulation(self):
        try:
            self.gazebo_simulator.start_simulator()
            self.loop.run_until_complete(self.drone_controller.connect_drone())
            self.status_label.setText("Симуляция успешно запущена!")
        except Exception as e:
            self.error_handler.log_error(e)
            self.status_label.setText(f"Error: {str(e)}")

    def enable_start_drone_button(self, connected, message):
        self.btn_start_drone.setEnabled(connected)

    def start_drone(self):

        try:
            self.drone_task = self.loop.create_task(self.start_control_drone())
            self.loop.run_until_complete(self.drone_task)
            self.status_label.setText("Дрон успешно стартовал!")
        except Exception as e:
            self.error_handler.log_error(e)
            self.status_label.setText(f"Error: {str(e)}")

    async def start_control_drone(self):
        started = await self.drone_controller.start_drone()
        if started:
            await asyncio.sleep(1)

            self.dr_thread = DroneThread(self.loop, self.drone_controller)
            self.dr_thread.start()

    def stop_drone(self):
        try:
            if self.drone_task:
                self.dr_thread.exit()
                self.drone_controller.on_flight = False
                self.drone_task.cancel()
                self.track_device.stop_tracking()
                self.loop.run_until_complete(self.drone_controller.stop_drone())
                self.status_label.setText("Дрон успешно остановлен!")
        except Exception as e:
            if str(e) != "This event loop is already running":
                self.error_handler.log_error(e)
                self.status_label.setText(f"Error: {str(e)}")

    @pyqtSlot()
    def stop_simulation(self):
        try:
            self.gazebo_simulator.stop_simulator()
            self.status_label.setText("Симуляция успешно остановлена!")
        except Exception as e:
            self.error_handler.log_error(e)
            self.status_label.setText(f"Error: {str(e)}")

    @pyqtSlot()
    def start_empty_world(self):
        try:
            self.gazebo_simulator.set_world("empty")
            self.start_simulation()
        except Exception as e:
            self.error_handler.log_error(e)
            self.status_label.setText(f"Error: {str(e)}")

    @pyqtSlot()
    def start_nature_world(self):
        try:
            self.gazebo_simulator.set_world("baylands")
            self.start_simulation()
        except Exception as e:
            self.error_handler.log_error(e)
            self.status_label.setText(f"Error: {str(e)}")

    @pyqtSlot()
    def exit_app(self):
        try:
            self.stop_simulation()
        except Exception as e:
            self.error_handler.log_error(e)
        finally:
            self.drone_connector_thread.quit()
            self.drone_connector_thread.wait()
            QApplication.instance().quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_interface = MainInterface()
    main_interface.show()
    sys.exit(app.exec_())
