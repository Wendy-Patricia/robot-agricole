
"""
Tests de navigation du robot agricole.

Modes :
1 - Simulation
2 - Navigation réelle
3 - Détection de ligne
0 - Quitter
"""

import cv2

from robot.navigation.camera import Camera
from robot.navigation.line_detection import LineDetector
from robot.navigation.motors import MotorController
from robot.navigation.navigation import Navigation


class MockMotorController:
    """
    Simulation des moteurs sans GPIO.
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


def create_camera():
    return Camera(
        camera_index=0,
        width=640,
        height=480
    )


def create_navigation(camera, detector, motors):
    return Navigation(
        camera=camera,
        line_detector=detector,
        motor_controller=motors,
        base_speed=35,
        min_speed=30,
        max_speed=45,
        kp=0.5,
        tolerance=0.15,
        lost_limit=5,
        correction_time=0.06
    )


# ==================================================
# MODE 1 : SIMULATION
# ==================================================

def test_simulation():
    print("\n" + "=" * 50)
    print("TEST 1 : SIMULATION")
    print("=" * 50)

    camera = create_camera()
    detector = LineDetector(min_area=500)
    motors = MockMotorController()

    navigation = create_navigation(
        camera,
        detector,
        motors
    )

    try:
        camera.start()

        print("[INFO] Simulation démarrée")
        print("[INFO] Appuyer sur Q pour quitter")

        while True:
            frame = camera.read()

            if frame is None or frame.size == 0:
                direction = navigation.navigate(None)

                if navigation.safety_locked:
                    break

                continue

            error, mask = detector.detect(frame)

            direction = navigation.navigate(error)

            debug_frame = navigation.draw_debug(
                frame.copy(),
                error,
                direction
            )

            cv2.putText(
                debug_frame,
                f"Vitesse: {motors.last_speed:.1f}%",
                (15, 160),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2
            )

            cv2.putText(
                debug_frame,
                "MODE SIMULATION",
                (15, 190),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            cv2.imshow(
                "TEST - Simulation",
                debug_frame
            )

            if mask is not None:
                cv2.imshow(
                    "TEST - Masque",
                    mask
                )

            print(
                f"\rErreur: {str(error):>7} | "
                f"Direction: {direction:<10} | "
                f"Moteurs: {motors.last_action:<8}",
                end="",
                flush=True
            )

            if navigation.safety_locked:
                print("\n[SECURITE] Simulation arrêtée")
                break

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\n[INFO] Interruption")

    finally:
        navigation.stop()
        motors.cleanup()
        print("\n[TEST] Simulation terminée")


# ==================================================
# MODE 2 : NAVIGATION REELLE
# ==================================================

def test_real_navigation():
    print("\n" + "=" * 50)
    print("TEST 2 : NAVIGATION REELLE")
    print("=" * 50)

    print("[ATTENTION] Les moteurs vont être activés !")
    print("[ATTENTION] Utiliser une zone sécurisée.")
    print("[ATTENTION] Prévoir un arrêt d'urgence.")

    confirmation = input(
        "Activer les moteurs ? (oui/non) : "
    ).strip().lower()

    if confirmation != "oui":
        print("[INFO] Test annulé")
        return

    camera = create_camera()
    detector = LineDetector(min_area=500)

    motors = None
    navigation = None

    try:
        motors = MotorController()

        navigation = create_navigation(
            camera,
            detector,
            motors
        )

        print("[INFO] Navigation réelle démarrée")

        navigation.run(show_debug=True)

    except KeyboardInterrupt:
        print("\n[INFO] Arrêt demandé")

    finally:
        if motors is not None:
            motors.stop()

            try:
                motors.cleanup()
            except Exception as error:
                print(f"[ERREUR] Nettoyage: {error}")

        camera.stop()
        cv2.destroyAllWindows()

        print("[TEST] Navigation réelle terminée")


# ==================================================
# MODE 3 : DETECTION UNIQUEMENT
# ==================================================

def test_line_detection():
    print("\n" + "=" * 50)
    print("TEST 3 : DETECTION DE LIGNE")
    print("=" * 50)

    camera = create_camera()
    detector = LineDetector(min_area=500)

    try:
        camera.start()

        print("[INFO] Détection démarrée")
        print("[INFO] Aucun moteur activé")

        while True:
            frame = camera.read()

            if frame is None or frame.size == 0:
                print("[CAMERA] Image indisponible")
                break

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

                message = f"Erreur: {error:+.3f}"
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

            if mask is not None:
                cv2.imshow(
                    "TEST - Masque",
                    mask
                )

            print(
                f"\r{message:<40}",
                end="",
                flush=True
            )

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
