import unittest

import cv2
import numpy as np

from navigation.line_detection import LineDetector


class LineDetectorColorTests(unittest.TestCase):
    def make_frame_with_line(self, color):
        frame = np.full((100, 100, 3), 255, dtype=np.uint8)
        cv2.rectangle(frame, (20, 55), (35, 95), color, -1)
        return frame

    def test_detects_red_line(self):
        detector = LineDetector(min_area=100, color="red")

        error, mask = detector.detect(self.make_frame_with_line((0, 0, 255)))

        self.assertIsNotNone(error)
        self.assertLess(error, 0)
        self.assertGreater(cv2.countNonZero(mask), 0)

    def test_detects_green_line(self):
        detector = LineDetector(min_area=100, color="green")

        error, mask = detector.detect(self.make_frame_with_line((0, 255, 0)))

        self.assertIsNotNone(error)
        self.assertLess(error, 0)
        self.assertGreater(cv2.countNonZero(mask), 0)

    def test_black_remains_the_default_color(self):
        detector = LineDetector(min_area=100)

        error, mask = detector.detect(self.make_frame_with_line((0, 0, 0)))

        self.assertIsNotNone(error)
        self.assertLess(error, 0)
        self.assertGreater(cv2.countNonZero(mask), 0)

    def test_rejects_unknown_color(self):
        with self.assertRaises(ValueError):
            LineDetector(color="turquoise")


if __name__ == "__main__":
    unittest.main()