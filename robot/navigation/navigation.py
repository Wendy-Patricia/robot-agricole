from time import monotonic

from .line_detection import detect_line_center


class PID:
    def __init__(self, kp, ki, kd, integral_limit=1.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral_limit = integral_limit
        self.reset()

    def reset(self):
        self.integral = 0.0
        self.previous_error = None

    def update(self, error, dt):
        self.integral += error * dt
        self.integral = max(
            -self.integral_limit,
            min(self.integral, self.integral_limit),
        )

        derivative = 0.0
        if self.previous_error is not None:
            derivative = (error - self.previous_error) / dt

        self.previous_error = error

        return (
            self.kp * error
            + self.ki * self.integral
            + self.kd * derivative
        )


def follow_line(read_frame, set_motor_speeds, base_speed=0.25, threshold=80):
    """Segue a linha usando velocidades de avanço entre 0.0 e 1.0."""
    pid = PID(kp=0.35, ki=0.0, kd=0.0)
    previous_time = monotonic()

    try:
        while True:
            frame = read_frame()
            if frame is None:
                raise RuntimeError("A câmara deixou de fornecer imagens.")

            track_center, _ = detect_line_center(frame, threshold)

            current_time = monotonic()
            dt = max(current_time - previous_time, 0.001)
            previous_time = current_time

            if track_center is None:
                # Arrêt jusqu'à ce que la ligne soit de nouveau visible.
                set_motor_speeds(0.0, 0.0)
                pid.reset()
                continue

            frame_center = (frame.shape[1] - 1) / 2
            error_pixels = track_center - frame_center
            error = error_pixels / max(frame_center, 1.0)

            if error == 0.0:
                pid.reset()
                correction = 0.0
            else:
                correction = pid.update(error, dt)

            left_speed = max(0.0, min(1.0, base_speed + correction))
            right_speed = max(0.0, min(1.0, base_speed - correction))

            set_motor_speeds(left_speed, right_speed)

    except KeyboardInterrupt:
        pass
    finally:
        set_motor_speeds(0.0, 0.0)

def main():
    from .camera import Camera
    from .motors import MotorController

    camera = Camera(camera_index=0)

    try:
        camera.start()
        motors = MotorController()

        try:
            def set_motor_speeds(left_speed, right_speed):
                # Convertit les valeurs de 0 à 1 en pourcentages PWM.
                motors.drive(left_speed * 100.0, right_speed * 100.0)

            follow_line(
                read_frame=camera.read,
                set_motor_speeds=set_motor_speeds,
                base_speed=0.25,
                threshold=80,
            )
        finally:
            motors.cleanup()
    finally:
        camera.stop()


if __name__ == "__main__":
    main()