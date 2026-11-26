import gc
from importlib import import_module
import math


class MotorController:
    """
    Contrôleur des deux moteurs du robot agricole.

    Moteur A : côté gauche
    Moteur B : côté droit

    PWM appliqué directement aux entrées de direction.
    Configuration destinée aux pilotes compatibles avec
    ce mode de commande, comme le DRV8833.
    """

    # GPIO - Numérotation BCM
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
        if hasattr(self.gpio, "PWM"):
            self.gpio.PWM.__del__ = lambda self: None

        self._pwm_channels = {}
        self._cleaned_up = False
        self._enabled = False

        self.gpio.setwarnings(False)
        self.gpio.setmode(self.gpio.BCM)

        try:
            # Initialiser tous les GPIO à l'état bas
            self.gpio.setup(
                [*self.MOTOR_PINS, self.NSLEEP],
                self.gpio.OUT,
                initial=self.gpio.LOW
            )

            # Créer un objet PWM par broche, une seule fois
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
    # Activation du pilote
    # --------------------------------------------------

    def enable(self):
        self._check_available()

        if not self._enabled:
            self.gpio.output(self.NSLEEP, self.gpio.HIGH)
            self._enabled = True

    def drive(self, left_speed: float, right_speed: float) -> tuple[float, float]:
        """
        Permite controlar cada roda independentemente (suporta valores negativos para ré).
        Essencial para curvas suaves com PID sem parar o robô.
        """
        self._check_available()
        self.enable()

        left_speed = self._limit_signed_speed(left_speed)
        right_speed = self._limit_signed_speed(right_speed)

        # Controle do Motor Esquerdo (A)
        if left_speed >= 0:
            self._pwm_channels[self.AIN2].ChangeDutyCycle(0)
            self._pwm_channels[self.AIN1].ChangeDutyCycle(left_speed)
        else:
            self._pwm_channels[self.AIN1].ChangeDutyCycle(0)
            self._pwm_channels[self.AIN2].ChangeDutyCycle(abs(left_speed))

        # Controle do Motor Direito (B)
        if right_speed >= 0:
            self._pwm_channels[self.BIN1].ChangeDutyCycle(0)
            self._pwm_channels[self.BIN2].ChangeDutyCycle(right_speed)
        else:
            self._pwm_channels[self.BIN2].ChangeDutyCycle(0)
            self._pwm_channels[self.BIN1].ChangeDutyCycle(abs(right_speed))

        return left_speed, right_speed
    
    @staticmethod
    def _limit_signed_speed(speed):
        speed = float(speed)

        if not math.isfinite(speed):
            raise ValueError("La vitesse doit être un nombre fini.")

        return max(-100.0, min(100.0, speed))
    # --------------------------------------------------
    # Mouvements
    # --------------------------------------------------

    def forward(self, speed: float) -> tuple[float, float]:
        speed = self._limit_speed(speed)

        self._set_motor_speeds(
            speed, speed,
            self.AIN1, self.BIN2
        )


        return speed, speed

    def backward(self, speed: float) -> tuple[float, float]:
        speed = self._limit_speed(speed)

        self._set_motor_speeds(
            speed, speed,
            self.AIN2, self.BIN1
        )

        return speed, speed

    def turn_right(self, speed: float) -> tuple[float, float]:
        speed = self._limit_speed(speed)

        self._set_motor_speeds(
            speed, speed,
            self.AIN2, self.BIN2
        )

        return speed, speed

    def turn_left(self, speed: float) -> tuple[float, float]:
        speed = self._limit_speed(speed)

        self._set_motor_speeds(
            speed, speed,
            self.AIN1, self.BIN1
        )

        return speed, speed

    # --------------------------------------------------
    # Commande interne des moteurs
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

        # Désactiver les quatre signaux avant de
        # changer le sens de rotation des moteurs
        for pwm in self._pwm_channels.values():
            pwm.ChangeDutyCycle(0)

        # Appliquer les vitesses souhaitées
        self._pwm_channels[left_pin].ChangeDutyCycle(
            left_speed
        )

        self._pwm_channels[right_pin].ChangeDutyCycle(
            right_speed
        )

    # --------------------------------------------------
    # Arrêt
    # --------------------------------------------------

    def stop(self) -> None:
        if self._cleaned_up:
            return

        for pwm in self._pwm_channels.values():
            pwm.ChangeDutyCycle(0)

        print("Moteurs arrêtés")

    # --------------------------------------------------
    # Désactivation du pilote
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
    # Nettoyage des GPIO
    # --------------------------------------------------

    def cleanup(self):
        if self._cleaned_up:
            return

        try:
            self.disable()
        finally:
            self._release_resources()

        print("GPIO nettoyés")
        print("Système nettoyé et désactivé.")

    def _release_resources(self):
        if self._cleaned_up:
            return

        self._cleaned_up = True
        self._enabled = False

        # Désactiver le DRV8833
        try:
            self.gpio.output(self.NSLEEP, self.gpio.LOW)
        except Exception:
            pass

        # Arrêter les canaux PWM
        for pwm in self._pwm_channels.values():
            try:
                pwm.stop()
            except Exception:
                pass

        self._pwm_channels.clear()
        gc.collect()

        # Libérer les GPIO
        self.gpio.cleanup()

    # --------------------------------------------------
    # Vérification de l'état
    # --------------------------------------------------

    def _check_available(self):
        if self._cleaned_up:
            raise RuntimeError(
                "MotorController a déjà été désactivé. "
                "Créez une nouvelle instance pour "
                "commander à nouveau les moteurs."
            )

    # --------------------------------------------------
    # Limitation de la vitesse
    # --------------------------------------------------

    @staticmethod
    def _limit_speed(speed):
        speed = float(speed)

        if not math.isfinite(speed):
            raise ValueError(
                "La vitesse doit être un nombre fini."
            )

        return max(0.0, min(100.0, speed))
    
    