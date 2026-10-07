import RPi.GPIO as GPIO
import time

AIN1 = 18
AIN2 = 27
NSLEEP = 17

BIN1 = 22
BIN2 = 23

GPIO.setmode(GPIO.BCM)

GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(NSLEEP, GPIO.OUT)

GPIO.setup(BIN1, GPIO.OUT)
GPIO.setup(BIN2, GPIO.OUT)

try:
    print("Activation du driver moteur")
    GPIO.output(NSLEEP, GPIO.HIGH)

    print("Moteur gauche")
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.LOW)
    time.sleep(1)

    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.LOW)

    time.sleep(1)

    print("Moteur droit")
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.LOW)
    time.sleep(1)

    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.LOW)

finally:
    GPIO.output(NSLEEP, GPIO.LOW)
    GPIO.cleanup()
    print("Test terminé")