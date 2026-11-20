"""Seguimento de linha com antecipacao de curvas e comando diferencial PD."""

import math
import time

from .line_detection import LineDetector


class Navigator:
    def __init__(self, camera, motors, detector=None, base_speed=30, kp=40,
                 kd=1.5, min_speed=16, max_speed=60, curve_slowdown=0.6):
        values = (base_speed, kp, kd, min_speed, max_speed, curve_slowdown)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Os parametros devem ser finitos")
        if not 0 <= min_speed <= base_speed <= max_speed <= 100:
            raise ValueError("Usar 0 <= min_speed <= base_speed <= max_speed <= 100")
        if kp < 0 or kd < 0 or not 0 <= curve_slowdown <= 1:
            raise ValueError("Ganhos positivos; curve_slowdown entre 0 e 1")
        self.camera = camera
        self.motors = motors
        self.detector = detector if detector is not None else LineDetector()
        self.base_speed = base_speed
        self.kp = kp
        self.kd = kd
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.curve_slowdown = curve_slowdown
        self.last_speeds = (0.0, 0.0)
        self.last_frame = None
        self.last_mask = None
        self._last_error = None
        self._last_time = None
        self._derivative = 0.0
        self._stopped = False

    def stop(self):
        self.motors.stop()
        self.last_speeds = (0.0, 0.0)
        self._last_error = None
        self._last_time = None
        self._derivative = 0.0
        self._stopped = True

    def step(self):
        """Captura, deteta e comanda; para se perder a linha ou houver erro."""
        try:
            self.last_frame = self.camera.read()
            error, self.last_mask = self.detector.detect(self.last_frame)
            if error is None:
                if not self._stopped:
                    self.stop()
                return None
            if not math.isfinite(error):
                raise ValueError("Erro de detecao invalido")

            now = time.monotonic()
            if self._last_time is not None:
                dt = max(now - self._last_time, 0.001)
                raw_derivative = (error - self._last_error) / dt
                # Filtrar a derivada para nao amplificar ruido da imagem.
                alpha = dt / (0.10 + dt)
                self._derivative += alpha * (raw_derivative - self._derivative)
            self._last_error, self._last_time = error, now

            bend = min(1.0, max(abs(error), abs(getattr(self.detector, "curvature", 0.0))))
            speed = max(self.min_speed,
                        self.base_speed * (1 - self.curve_slowdown * bend))
            correction = self.kp * error + self.kd * self._derivative
            correction = max(-self.max_speed, min(self.max_speed, correction))
            # Linha a direita: roda esquerda mais rapida; esquerda: inverso.
            left = max(0.0, min(self.max_speed, speed + correction))
            right = max(0.0, min(self.max_speed, speed - correction))
            self.motors.drive(left, right)
            self.last_speeds = (left, right)
            self._stopped = False
            return error
        except BaseException:
            self.stop()
            raise

    def run(self):
        """Segue a linha ate Ctrl+C, libertando camera e GPIO no fim."""
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
    from .camera import Camera
    from .motors import MotorController

    navigator = Navigator(Camera(), MotorController())
    try:
        navigator.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
