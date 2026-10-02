import sys
from navigation.motors import MotorController
import types

# --- fake GPIO ---
class FakePWM:
    def __init__(self, pin, frequency):
        self.pin = pin
        self.frequency = frequency
        self.duty = 0

    def start(self, duty):
        self.duty = duty

    def ChangeDutyCycle(self, duty):
        self.duty = duty


class FakeGPIO:
    BCM = "BCM"
    OUT = "OUT"
    HIGH = 1
    LOW = 0

    def __init__(self):
        self.mode = None
        self.outputs = {}
        self.pwm_instances = []

    def setmode(self, mode):
        self.mode = mode

    def setup(self, pins, mode):
        for pin in pins:
            self.outputs[pin] = self.LOW

    def output(self, pin, value):
        self.outputs[pin] = value

    def PWM(self, pin, frequency):
        pwm = FakePWM(pin, frequency)
        self.pwm_instances.append(pwm)
        return pwm

    def cleanup(self):
        self.outputs.clear()


# --- injeta o módulo fake antes do import ---
fake_rpi = types.ModuleType("RPi")
fake_rpi.GPIO = FakeGPIO()
sys.modules["RPi"] = fake_rpi
sys.modules["RPi.GPIO"] = fake_rpi.GPIO

# importa o controlador
from navigation.motors import MotorController

# --- teste ---
gpio = fake_rpi.GPIO
controller = MotorController()

controller.forward(50)
assert gpio.outputs[controller.AIN2] == gpio.LOW
assert gpio.outputs[controller.BIN2] == gpio.LOW

controller.turn_left(30)
controller.stop()

print("Teste de lógica do motor OK")