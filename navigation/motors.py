import gc
from importlib import import_module
import math


class MotorController:
    """
    Controlador dos dois motores do robô agrícola.

    Motor A: lado esquerdo
    Motor B: lado direito

    PWM aplicado diretamente às entradas de direção.
    Configuração destinada a drivers compatíveis com
    este modo de controlo, como o DRV8833.
    """

    # GPIOs - Numeração BCM
    AIN1 = 22
    AIN2 = 23
    BIN1 = 18
    BIN2 = 27
    NSLEEP = 17

    FREQUENCY = 2000

    MOTOR_PINS = (AIN1, AIN2, BIN1, BIN2)

    def __init__(self, gpio_module=None):
        if gpio_module is None:
            gpio_module = import_module("RPi.GPIO")

        self.gpio = gpio_module
        self._pwm_channels = {}
        self._cleaned_up = False
        self._enabled = False

        self.gpio.setwarnings(False)
        self.gpio.setmode(self.gpio.BCM)

        try:
            # Inicializar todos os GPIOs desligados
            self.gpio.setup(
                [*self.MOTOR_PINS, self.NSLEEP],
                self.gpio.OUT,
                initial=self.gpio.LOW
            )

            # Criar um objeto PWM por pino, apenas uma vez
            for pin in self.MOTOR_PINS:
                pwm = self.gpio.PWM(pin, self.FREQUENCY)
                self._pwm_channels[pin] = pwm
                pwm.start(0)

            self.enable()

            print("MotorController initialisé")

        except Exception:
            self._release_resources()
            raise

    # --------------------------------------------------
    # Ativação do driver
    # --------------------------------------------------

    def enable(self):
        self._check_available()

        if not self._enabled:
            self.gpio.output(self.NSLEEP, self.gpio.HIGH)
            self._enabled = True

    # --------------------------------------------------
    # Movimentos
    # --------------------------------------------------

  
    def forward(self, speed: float) -> tuple[float, float]:
        speed = self._limit_speed(speed)

        self._set_motor_speeds(
            speed, speed,
            self.AIN2, self.BIN1
        )

        return speed, speed

    def backward(self, speed: float) -> tuple[float, float]:
        speed = self._limit_speed(speed)

        self._set_motor_speeds(
            speed, speed,
            self.AIN1, self.BIN2
        )

        return speed, speed

    def turn_right(self, speed: float) -> tuple[float, float]:
        speed = self._limit_speed(speed)

        self._set_motor_speeds(
            speed, speed,
            self.AIN1, self.BIN1
        )

        return speed, speed

    def turn_left(self, speed: float) -> tuple[float, float]:
        speed = self._limit_speed(speed)

        self._set_motor_speeds(
            speed, speed,
            self.AIN2, self.BIN2
        )

        return speed, speed


    # --------------------------------------------------
    # Controlo interno dos motores
    # --------------------------------------------------

    def _set_motor_speeds(
        self,
        left_speed,
        right_speed,
        left_pin,
        right_pin
    ):
        self._check_available()
        self.enable()

        left_speed = self._limit_speed(left_speed)
        right_speed = self._limit_speed(right_speed)

        # Desativar os quatro sinais antes de
        # mudar a direção dos motores
        for pwm in self._pwm_channels.values():
            pwm.ChangeDutyCycle(0)

        # Aplicar as velocidades pretendidas
        self._pwm_channels[left_pin].ChangeDutyCycle(
            left_speed
        )

        self._pwm_channels[right_pin].ChangeDutyCycle(
            right_speed
        )

    # --------------------------------------------------
    # Paragem
    # --------------------------------------------------

    def stop(self) -> None:
        if self._cleaned_up:
            return

        for pwm in self._pwm_channels.values():
            pwm.ChangeDutyCycle(0)

        print("Moteurs arrêtés")

    # --------------------------------------------------
    # Desativação do driver
    # --------------------------------------------------

    def disable(self):
        if self._cleaned_up:
            return

        self.stop()

        self.gpio.output(
            self.NSLEEP,
            self.gpio.LOW
        )

        self._enabled = False

        print("Driver désactivé")

    # --------------------------------------------------
    # Limpeza dos GPIOs
    # --------------------------------------------------

    def cleanup(self):
        if self._cleaned_up:
            return

        try:
            self.disable()
        finally:
            self._release_resources()

        print("GPIO nettoyés")
        print("Sistema limpo e desligado.")


    def _release_resources(self):
        if self._cleaned_up:
            return

        self._cleaned_up = True
        self._enabled = False

        # Desativar o DRV8833
        try:
            self.gpio.output(self.NSLEEP, self.gpio.LOW)
        except Exception:
            pass

        # Parar os canais PWM
        for pwm in self._pwm_channels.values():
            try:
                pwm.stop()
            except Exception:
                pass
            
        self._pwm_channels.clear()
        gc.collect()

        # Libertar os GPIO
        self.gpio.cleanup()

    # --------------------------------------------------
    # Verificação do estado
    # --------------------------------------------------

    def _check_available(self):
        if self._cleaned_up:
            raise RuntimeError(
                "MotorController já foi desligado. "
                "Cria uma nova instância para "
                "voltar a controlar os motores."
            )

    # --------------------------------------------------
    # Limitação da velocidade
    # --------------------------------------------------

    @staticmethod
    def _limit_speed(speed):
        speed = float(speed)

        if not math.isfinite(speed):
            raise ValueError(
                "A velocidade deve ser um número finito."
            )

        return max(0.0, min(100.0, speed))
