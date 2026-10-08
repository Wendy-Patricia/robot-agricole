import unittest

from navigation.motors import MotorController


class FakePWM:
    def __init__(self, pin, frequency):
        self.pin = pin
        self.frequency = frequency
        self.duty_cycle = None
        self.started = False
        self.stopped = False

    def start(self, duty_cycle):
        self.started = True
        self.duty_cycle = duty_cycle

    def ChangeDutyCycle(self, duty_cycle):
        self.duty_cycle = duty_cycle

    def stop(self):
        self.stopped = True


class FakeGPIO:
    BCM = "BCM"
    OUT = "OUT"
    HIGH = 1
    LOW = 0

    def __init__(self):
        self.pwm_channels = {}

    def setmode(self, mode):
        self.mode = mode

    def setup(self, pins, direction):
        self.pins = pins
        self.direction = direction

    def output(self, pin, value):
        pass

    def PWM(self, pin, frequency):
        pwm = FakePWM(pin, frequency)
        self.pwm_channels[pin] = pwm
        return pwm

    def cleanup(self):
        pass


class MotorControllerPWMTests(unittest.TestCase):
    def setUp(self):
        self.gpio = FakeGPIO()
        self.motor = MotorController(gpio_module=self.gpio)

    def test_reuses_four_pwm_channels_for_all_motions(self):
        self.motor.forward(60)
        self.motor.backward(40)
        self.motor.turn_right(30)
        self.motor.turn_left(20)

        self.assertEqual(len(self.gpio.pwm_channels), 4)
        self.assertTrue(all(pwm.started for pwm in self.gpio.pwm_channels.values()))

    def test_stop_sets_every_duty_cycle_to_zero(self):
        self.motor.forward(60)

        self.motor.stop()

        self.assertTrue(
            all(pwm.duty_cycle == 0 for pwm in self.gpio.pwm_channels.values())
        )

    def test_limits_speed_to_motor_range(self):
        self.motor.forward(140)
        self.assertEqual(self.gpio.pwm_channels[self.motor.AIN1].duty_cycle, 100)

        self.motor.backward(-10)
        self.assertEqual(self.gpio.pwm_channels[self.motor.AIN2].duty_cycle, 0)


if __name__ == "__main__":
    unittest.main()