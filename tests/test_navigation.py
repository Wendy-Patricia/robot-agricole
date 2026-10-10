import unittest

from navigation.navigation import Navigation
from simulation.fake_motors import FakeMotorController


class SequenceDetector:
    def __init__(self, errors):
        self.errors = iter(errors)

    def detect(self, frame):
        return next(self.errors), None


class NavigationTests(unittest.TestCase):
    def test_repeated_line_loss_stops_once_and_does_not_reissue_commands(self):
        motors = FakeMotorController()
        detector = SequenceDetector([-0.5, 0.0, 0.5, None, None])
        navigation = Navigation(motors, line_detector=detector)
        navigation.start()

        self.assertEqual(navigation.process_frame(None), -0.5)
        self.assertEqual(navigation.process_frame(None), 0.0)
        self.assertEqual(navigation.process_frame(None), 0.5)
        self.assertIsNone(navigation.process_frame(None))
        self.assertIsNone(navigation.process_frame(None))

        self.assertEqual(
            motors.commands,
            [
                ("turn_left", 50),
                ("forward", 50),
                ("turn_right", 50),
                ("stop", None),
            ]
        )


if __name__ == "__main__":
    unittest.main()