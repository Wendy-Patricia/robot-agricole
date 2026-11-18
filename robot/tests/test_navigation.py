from contextlib import ExitStack

import cv2

from robot.navigation.camera import Camera
from robot.navigation.line_detection import LineDetector
from robot.navigation.motors import MotorController
from robot.navigation.navigation import Navigation


def executar_teste_manual():
    """Teste le suivi de ligne avec la caméra et les moteurs physiques."""
    vitesse = 30
    seuil = 0.2

    # Les rappels sont exécutés en ordre inverse, même en cas d'erreur.
    with ExitStack() as resources:
        resources.callback(cv2.destroyAllWindows)
        camera = Camera(camera_index=0, width=640, height=480)
        resources.callback(camera.stop)
        camera.start()

        detector = LineDetector()
        motors = MotorController()
        resources.callback(motors.cleanup)

        navigation = Navigation(
            motors=motors,
            line_detector=detector,
            threshold=seuil,
            speed=vitesse,
        )
        resources.callback(navigation.stop)

        print(f"Test de navigation : vitesse {vitesse}%, seuil {seuil}.")
        print("Suivi de la ligne noire. ESC ou Ctrl+C pour arrêter.")
        navigation.start()

        try:
            while True:
                frame = camera.read()
                error = navigation.process_frame(frame)

                if error is None:
                    status = "Ligne perdue : arret"
                elif error < -seuil:
                    status = f"Gauche | erreur : {error:.2f}"
                elif error > seuil:
                    status = f"Droite | erreur : {error:.2f}"
                else:
                    status = f"Avant | erreur : {error:.2f}"

                height, width = frame.shape[:2]
                center = width // 2
                left = int(width * (1 - seuil) / 2)
                right = int(width * (1 + seuil) / 2)
                cv2.line(
                    frame, (center, height // 2), (center, height - 1),
                    (0, 255, 0), 2,
                )
                for x in (left, right):
                    cv2.line(
                        frame, (x, height // 2), (x, height - 1),
                        (0, 255, 255), 1,
                    )
                cv2.putText(
                    frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 0, 255), 2,
                )
                cv2.imshow("Navigation - ESC pour arreter", frame)

                if cv2.waitKey(1) & 0xFF == 27:
                    break
        except KeyboardInterrupt:
            print("Test interrompu par l'utilisateur.")


if __name__ == "__main__":
    executar_teste_manual()
