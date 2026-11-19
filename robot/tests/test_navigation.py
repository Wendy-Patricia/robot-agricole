"""
Tests de navigation du robot agricole.

Modes disponibles :
    1. Simulation (sans moteurs)
    2. Navigation réelle
    3. Test de détection uniquement
"""

from contextlib import ExitStack
import cv2
import time

from robot.navigation.camera import Camera
from robot.navigation.line_detection import LineDetector
from robot.navigation.motors import MotorController
from robot.navigation.navigation import Navigation


# ==================================================
# SIMULATION DES MOTEURS
# ==================================================

class MockMotorController:
    """
    Simule les moteurs sans utiliser les GPIO.
    """

    def __init__(self):
        self.last_action = "STOP"
        self.last_speed = 0
        print("[SIMULATION] Moteurs virtuels initialisés")

    def forward(self, speed):
        self.last_action = "FORWARD"
        self.last_speed = speed

    def backward(self, speed):
        self.last_action = "BACKWARD"
        self.last_speed = speed

    def turn_left(self, speed):
        self.last_action = "LEFT"
        self.last_speed = speed

    def turn_right(self, speed):
        self.last_action = "RIGHT"
        self.last_speed = speed

    def stop(self):
        self.last_action = "STOP"
        self.last_speed = 0

    def cleanup(self):
        self.stop()
        print("[SIMULATION] Moteurs nettoyés")


# ==================================================
# MODE 1 - SIMULATION
# ==================================================

def test_simulation():
    """
    Teste la navigation avec la caméra réelle,
    mais sans activer les moteurs.
    """

    print("\n" + "=" * 50)
    print("TEST 1 : SIMULATION DE NAVIGATION")
    print("=" * 50)

    camera = Camera(
        camera_index=0,
        width=640,
        height=480
    )

    detector = LineDetector(min_area=500)

    motors = MockMotorController()

    navigation = Navigation(
        camera=camera,
        line_detector=detector,
        motor_controller=motors,
        base_speed=60,
        min_speed=40,
        max_speed=80,
        kp=0.8,
        tolerance=0.12,
        lost_limit=5,
        correction_time=0.08
    )

    try:
        camera.start()

        print("[INFO] Simulation démarrée")
        print("[INFO] Appuyer sur Q pour quitter")

        while True:

            frame = camera.read()

            error, mask = detector.detect(frame)

            direction = navigation.navigate(error)

            debug_frame = navigation.draw_debug(
                frame.copy(),
                error,
                direction
            )

            speed = motors.last_speed

            cv2.putText(
                debug_frame,
                f"Vitesse: {speed:.1f}%",
                (20, 105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            cv2.putText(
                debug_frame,
                "MODE SIMULATION",
                (20, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.imshow(
                "TEST - Navigation Simulation",
                debug_frame
            )

            cv2.imshow(
                "TEST - Masque",
                mask
            )

            print(
                f"\rErreur: {str(error):>7} | "
                f"Direction: {direction:<8} | "
                f"Commande: {motors.last_action:<8} | "
                f"Vitesse: {speed:.1f}%",
                end="",
                flush=True
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\n[INFO] Interruption utilisateur")

    finally:
        motors.stop()
        camera.stop()
        cv2.destroyAllWindows()
        motors.cleanup()

        print("\n[TEST] Simulation terminée")


# ==================================================
# MODE 2 - NAVIGATION REELLE
# ==================================================

def test_real_navigation():
    """
    Teste le suivi de ligne avec les vrais moteurs.

    ATTENTION :
    Placer le robot dans un environnement sécurisé.
    """

    print("\n" + "=" * 50)
    print("TEST 2 : NAVIGATION REELLE")
    print("=" * 50)

    print("[ATTENTION] Les moteurs vont être activés !")

    confirmation = input(
        "Activer les moteurs ? (oui/non) : "
    ).strip().lower()

    if confirmation != "oui":
        print("[INFO] Test annulé")
        return

    camera = Camera(
        camera_index=0,
        width=640,
        height=480
    )

    detector = LineDetector(min_area=500)

    motors = None

    try:
        motors = MotorController()

        navigation = Navigation(
            camera=camera,
            line_detector=detector,
            motor_controller=motors,
            base_speed=45,
            min_speed=35,
            max_speed=55,
            kp=0.8,
            tolerance=0.12,
            lost_limit=5,
            correction_time=0.08
        )

        print("[INFO] Navigation réelle démarrée")

        navigation.run(show_debug=True)

    except KeyboardInterrupt:
        print("\n[INFO] Arrêt demandé")

    finally:
        if motors is not None:
            motors.stop()
            motors.cleanup()

        camera.stop()
        cv2.destroyAllWindows()

        print("[TEST] Navigation réelle terminée")


# ==================================================
# MODE 3 - DETECTION UNIQUEMENT
# ==================================================

def test_line_detection():
    """
    Vérifie uniquement la détection de ligne.
    Aucun moteur n'est initialisé.
    """

    print("\n" + "=" * 50)
    print("TEST 3 : DETECTION DE LIGNE")
    print("=" * 50)

    camera = Camera(
        camera_index=0,
        width=640,
        height=480
    )

    detector = LineDetector(min_area=500)

    try:
        camera.start()

        while True:

            frame = camera.read()

            error, mask = detector.detect(frame)

            height, width = frame.shape[:2]
            center_x = width // 2

            cv2.line(
                frame,
                (center_x, 0),
                (center_x, height),
                (255, 0, 0),
                2
            )

            if error is not None:

                line_x = int(
                    center_x + error * center_x
                )

                cv2.circle(
                    frame,
                    (line_x, int(height * 0.75)),
                    10,
                    (0, 255, 0),
                    -1
                )

                message = f"Erreur: {error:.3f}"

            else:
                message = "Ligne non detectee"

            cv2.putText(
                frame,
                message,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

            cv2.imshow(
                "TEST - Detection",
                frame
            )

            cv2.imshow(
                "TEST - Masque HSV",
                mask
            )

            print(f"\r{message:<40}", end="", flush=True)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\n[INFO] Interruption")

    finally:
        camera.stop()
        cv2.destroyAllWindows()

        print("\n[TEST] Détection terminée")


# ==================================================
# MENU PRINCIPAL
# ==================================================

def main():

    print("\n" + "=" * 50)
    print("       ROBOT AGRICOLE")
    print("       TEST NAVIGATION")
    print("=" * 50)

    print("\nChoisir un mode :")
    print("1 - Simulation (caméra + moteurs virtuels)")
    print("2 - Navigation réelle (caméra + moteurs)")
    print("3 - Détection de ligne uniquement")
    print("0 - Quitter")

    choice = input("\nVotre choix : ").strip()

    if choice == "1":
        test_simulation()

    elif choice == "2":
        test_real_navigation()

    elif choice == "3":
        test_line_detection()

    elif choice == "0":
        print("[INFO] Programme terminé")

    else:
        print("[ERREUR] Choix invalide")


if __name__ == "__main__":
    main()
