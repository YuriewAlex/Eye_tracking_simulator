import asyncio
import unittest
from unittest.mock import patch, AsyncMock, MagicMock
import time
from mavsdk.offboard import VelocityNedYaw

from Track import TrackDevice
from Controller import DroneController

class TestTrackDevice(unittest.TestCase):
    @patch('time.time')
    def test_vertical_movement(self, mock_time):
        mock_time.return_value = 0
        gaze_data = {
            'left_gaze_point_on_display_area': (0.0, 0.0),
            'right_gaze_point_on_display_area': (0.0, 0.0),
            'left_pupil_diameter': 0.5,
            'right_pupil_diameter': 0.5,
            'left_pupil_validity': 0.8,
            'right_pupil_validity': 0.8
        }
        #TrackDevice.gaze_data_callback(gaze_data)
        self.assertEqual(TrackDevice.roadmap["Mode"], "hover")
        TrackDevice.gaze_data_callback(gaze_data)
        TrackDevice.gaze_data_callback(gaze_data)
        # Simulate rapid downward movement
        gaze_data['left_gaze_point_on_display_area'] = (0.0, 0.5)
        gaze_data['right_gaze_point_on_display_area'] = (0.0, 0.5)
        mock_time.return_value = 0.01
        TrackDevice.gaze_data_callback(gaze_data)
        self.assertEqual(TrackDevice.roadmap["Mode"], "vertical")
        self.assertEqual(TrackDevice.roadmap["vertical_param"], -1.0)

    @patch('time.time', return_value=0)
    def test_horizontal_movement(self, mock_time):
        gaze_data = {
            'left_gaze_point_on_display_area': (0.1, 0.1),
            'right_gaze_point_on_display_area': (0.1, 0.1),
            'left_pupil_diameter': 0.5,
            'right_pupil_diameter': 0.5,
            'left_pupil_validity': 0.8,
            'right_pupil_validity': 0.8
        }
        TrackDevice.gaze_data_callback(gaze_data)
        self.assertEqual(TrackDevice.roadmap["Mode"], "horizontal")
        self.assertEqual(TrackDevice.roadmap["direction"], (0.0, 0.0))

        # Simulate gaze towards right
        gaze_data['left_gaze_point_on_display_area'] = (0.6, 0.1)
        gaze_data['right_gaze_point_on_display_area'] = (0.6, 0.1)
        TrackDevice.gaze_data_callback(gaze_data)
        self.assertEqual(TrackDevice.roadmap["Mode"], "horizontal")
        self.assertEqual(TrackDevice.roadmap["direction"], (0.5, 0.0))

"""class TestDroneController(unittest.TestCase):

    @patch('mavsdk.System')
    @patch('Track.TrackDevice')
    def test_drone_controller_connection(self, MockTrackDevice, MockSystem):
        mock_system = MockSystem.return_value
        mock_system.core.connection_state = AsyncMock(return_value=iter([MagicMock(is_connected=True)]))
        mock_system.telemetry.health = AsyncMock(return_value=iter([MagicMock(is_global_position_ok=True, is_home_position_ok=True)]))

        mock_track_device = MockTrackDevice.return_value

        drone_controller = DroneController(mock_track_device)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(drone_controller.connect_drone())

        self.assertTrue(drone_controller.drone_connected)
        mock_system.connect.assert_called_with(system_address="udp://:14540")

    @patch('mavsdk.System')
    @patch('Track.TrackDevice')
    def test_drone_movement_with_gaze_data(self, MockTrackDevice, MockSystem):
        mock_system = MockSystem.return_value
        mock_system.offboard.set_velocity_ned = AsyncMock()
        mock_system.offboard.start = AsyncMock()
        mock_system.action.arm = AsyncMock()
        mock_system.action.takeoff = AsyncMock()
        mock_system.action.land = AsyncMock()

        mock_track_device = MockTrackDevice.return_value

        drone_controller = DroneController(mock_track_device)

        # Simulate drone connection
        loop = asyncio.get_event_loop()
        loop.run_until_complete(drone_controller.connect_drone())

        # Simulate receiving gaze data
        TrackDevice.gaze_data_callback({
            'left_gaze_point_on_display_area': (0.6, 0.1),
            'right_gaze_point_on_display_area': (0.6, 0.1),
            'left_pupil_diameter': 0.5,
            'right_pupil_diameter': 0.5,
            'left_pupil_validity': 0.8,
            'right_pupil_validity': 0.8
        })


        drone_controller.control_drone = AsyncMock()
        loop.run_until_complete(drone_controller.control_drone())


        mock_system.offboard.set_velocity_ned.assert_called_with(VelocityNedYaw(1, 0.0, 0, 0))
        mock_system.offboard.start.assert_called_once()"""

if __name__ == '__main__':
    unittest.main()
