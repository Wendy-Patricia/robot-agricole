"""Suivi de ligne avec une commande différentielle proportionnelle."""

from line_detection import LineDetector


class Navigator:
    def __init__(self, camera, motors, detector=None, base_speed=30, kp=25):
        self.camera = camera
        self.motors = motors
        self.detector = detector if detector is not None else LineDetector()
        self.base_speed = base_speed
        self.kp = kp

    def step(self):
        """Capture une image et commande les moteurs pour cette image."""
        try:
            frame = self.camera.read()
            error, _ = self.detector.detect(frame)
        except Exception:
            self.motors.stop()
            raise

        if error is None:
            self.motors.stop()
            return None

        correction = self.kp * error
        left_speed = self.base_speed + correction
        right_speed = self.base_speed - correction
        self.motors.drive(left_speed, right_speed)
        return error

    def run(self):
        """Démarre la caméra et suit la ligne jusqu'à l'arrêt du programme."""
        try:
            self.camera.start()
            while True:
                self.step()
        finally:
            try:
                self.motors.cleanup()
            finally:
                self.camera.stop()


def main():
    from camera import Camera
    from motors import MotorController

    navigator = Navigator(Camera(), MotorController())
    try:
        navigator.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
