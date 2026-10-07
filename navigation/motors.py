import RPi.GPIO as GPIO
import time


class MotorController:

    # GPIO Motor A
    AIN1 = 22
    AIN2 = 23

    # GPIO Motor B
    BIN1 = 18
    BIN2 = 27

    # Standby do TB6612FNG
    NSLEEP = 17

    # PWM
    FREQUENCY = 2000

    def __init__(self):
        
        GPIO.setmode(GPIO.BCM)


        GPIO.setup(
            [
                self.AIN1,
                self.AIN2,
                self.BIN1,
                self.BIN2,
                self.NSLEEP
            ],
            GPIO.OUT
        )

        GPIO.output(self.NSLEEP, GPIO.HIGH)

        print("MotorController inicialisé")

    def forward(self, speed):
        """
        Faire avancer les deux moteurs.
        speed: 0 à 100
        """

        speed = self._limit_speed(speed)

        pwm_a = GPIO.PWM(self.AIN1, self.FREQUENCY)
        pwm_b = GPIO.PWM(self.BIN1, self.FREQUENCY)

        pwm_a.start(0)
        pwm_b.start(0)

        # Direction avant
        GPIO.output(self.AIN2, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.LOW)

        # Vitesse
        pwm_a.ChangeDutyCycle(speed)
        pwm_b.ChangeDutyCycle(speed)

        return pwm_a, pwm_b

    def backward(self, speed):
        """
        Faire reculer les deux moteurs.
        speed: 0 à 100
        """

        speed = self._limit_speed(speed)

        pwm_a = GPIO.PWM(self.AIN2, self.FREQUENCY)
        pwm_b = GPIO.PWM(self.BIN2, self.FREQUENCY)

        pwm_a.start(0)
        pwm_b.start(0)

        # Direction arrière
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.BIN1, GPIO.LOW)

        # Vitesse
        pwm_a.ChangeDutyCycle(speed)
        pwm_b.ChangeDutyCycle(speed)

        return pwm_a, pwm_b


    def turn_right(self, speed):
        """
        Tourner vers la droite (Moteur gauche avance, moteur droit recule).
        """
        speed = self._limit_speed(speed)

        # Moteur gauche (Motor A) : AVANCE (AIN1 PWM, AIN2 LOW)
        GPIO.output(self.AIN2, GPIO.LOW)
        pwm_left = GPIO.PWM(self.AIN1, self.FREQUENCY)
        pwm_left.start(0)

        # Moteur droit (Motor B) : RECULE (BIN1 LOW, BIN2 PWM)
        GPIO.output(self.BIN1, GPIO.LOW)
        pwm_right = GPIO.PWM(self.BIN2, self.FREQUENCY)
        pwm_right.start(0)

        pwm_left.ChangeDutyCycle(speed)
        pwm_right.ChangeDutyCycle(speed)

        return pwm_left, pwm_right

    def turn_left(self, speed):
        """
        Tourner vers la gauche (Moteur gauche recule, moteur droit avance).
        """
        speed = self._limit_speed(speed)

        # Moteur gauche (Motor A) : RECULE (AIN1 LOW, AIN2 PWM)
        GPIO.output(self.AIN1, GPIO.LOW)
        pwm_left = GPIO.PWM(self.AIN2, self.FREQUENCY)
        pwm_left.start(0)

        # Moteur droit (Motor B) : AVANCE (BIN1 PWM, BIN2 LOW)
        GPIO.output(self.BIN2, GPIO.LOW)
        pwm_right = GPIO.PWM(self.BIN1, self.FREQUENCY)
        pwm_right.start(0)

        pwm_left.ChangeDutyCycle(speed)
        pwm_right.ChangeDutyCycle(speed)

        return pwm_left, pwm_right

    def stop(self):
        """
        Arrêter les deux moteurs.
        """

        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.LOW)

        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.LOW)

        print("Moteurs arrêtés")

    def disable(self):
        """
        Désactiver le TB6612FNG.
        """

        self.stop()

        GPIO.output(self.NSLEEP, GPIO.LOW)

        print("TB6612FNG désactivé")

    def cleanup(self):
        """
        Nettoyer les GPIO.
        """

        self.disable()
        GPIO.cleanup()

        print("GPIO nettoyés")

    @staticmethod
    def _limit_speed(speed):
        """
        Garantir que la vitesse est comprise entre 0 et 100.
        """

        if speed < 0:
            return 0

        if speed > 100:
            return 100

        return speed