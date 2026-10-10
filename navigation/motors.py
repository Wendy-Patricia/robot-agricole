from importlib import import_module
from .interfaces import MotorDriver


class MotorController(MotorDriver):
    AIN1 = 22
    AIN2 = 23
    BIN1 = 18
    BIN2 = 27
    NSLEEP = 17
    FREQUENCY = 2000

    def __init__(self, gpio_module=None):
        if gpio_module is None:
            gpio_module = import_module("RPi.GPIO")

        self.gpio = gpio_module
        self.gpio.setmode(self.gpio.BCM)
        self.gpio.setup(
            [self.AIN1, self.AIN2, self.BIN1, self.BIN2, self.NSLEEP],
            self.gpio.OUT
        )
        self.gpio.output(self.NSLEEP, self.gpio.HIGH)

        self._pwm_channels = {
            pin: self.gpio.PWM(pin, self.FREQUENCY)
            for pin in (self.AIN1, self.AIN2, self.BIN1, self.BIN2)
        }
        for pwm in self._pwm_channels.values():
            pwm.start(0)

    def forward(self, speed: float) -> None:
        speed = self._limit_speed(speed)
        self._set_motor_speeds(speed, speed, self.AIN1, self.BIN1)

    def backward(self, speed: float) -> None:
        speed = self._limit_speed(speed)
        self._set_motor_speeds(speed, speed, self.AIN2, self.BIN2)

    def turn_right(self, speed: float) -> None:
        speed = self._limit_speed(speed)
        self._set_motor_speeds(speed, speed, self.AIN1, self.BIN2)

    def turn_left(self, speed: float) -> None:
        speed = self._limit_speed(speed)
        self._set_motor_speeds(speed, speed, self.AIN2, self.BIN1)

    def _set_motor_speeds(self, left_speed, right_speed, left_pin, right_pin):
        self._set_motor(self.AIN1, self.AIN2, left_pin, left_speed)
        self._set_motor(self.BIN1, self.BIN2, right_pin, right_speed)

    def _set_motor(self, forward_pin, reverse_pin, active_pin, speed):
        self._pwm_channels[forward_pin].ChangeDutyCycle(0)
        self._pwm_channels[reverse_pin].ChangeDutyCycle(0)
        self._pwm_channels[active_pin].ChangeDutyCycle(speed)

    def stop(self) -> None:
        for pwm in self._pwm_channels.values():
            pwm.ChangeDutyCycle(0)

    def disable(self):
        self.stop()
        self.gpio.output(self.NSLEEP, self.gpio.LOW)

    def cleanup(self):
        self.disable()
        for pwm in self._pwm_channels.values():
            pwm.stop()
        self.gpio.cleanup()

    @staticmethod
    def _limit_speed(speed):
        return max(0, min(100, speed))