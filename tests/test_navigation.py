import unittest

from navigation.navigation import Navigation


class FakeMotors:
    def __init__(self):
        self.commands = []

    def forward(self, speed):
        self.commands.append(("forward", speed))

    def turn_left(self, speed):
        self.commands.append(("turn_left", speed))

    def turn_right(self, speed):
        self.commands.append(("turn_right", speed))

    def stop(self):
        self.commands.append(("stop", None))


class SequenceDetector:
    def __init__(self, errors):
        self.errors = iter(errors)

    def detect(self, frame):
        return next(self.errors), None


class NavigationTests(unittest.TestCase):
    def test_repeated_line_loss_stops_once_and_does_not_reissue_commands(self):
        motors = FakeMotors()
        detector = SequenceDetector([-0.5, None, None, None])
        navigation = Navigation(motors, line_detector=detector)
        navigation.start()

        self.assertEqual(navigation.process_frame(None), -0.5)
        self.assertIsNone(navigation.process_frame(None))
        self.assertIsNone(navigation.process_frame(None))
        self.assertIsNone(navigation.process_frame(None))

        self.assertEqual(
            motors.commands,
            [("turn_left", 50), ("stop", None)]
        )


if __name__ == "__main__":
    unittest.main()