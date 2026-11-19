
import cv2
import time

from robot.navigation.camera import Camera
from robot.navigation.line_detection import LineDetector


def main():
    camera = Camera(
        camera_index=0,
        width=640,
        height=480
    )

    detector = LineDetector(min_area=500)

    print("=" * 55)
    print("TEST DE DETECTION DE LIGNE - SSH")
    print("=" * 55)
    print("Appuyer sur CTRL+C pour arrêter\n")

    try:
        camera.start()

        while True:
            frame = camera.read()

            error, mask = detector.detect(frame)

            # Nombre de pixels noirs détectés
            detected_pixels = cv2.countNonZero(mask)

            if error is None:
                status = "NON DETECTEE"
                direction = "STOP"
                error_text = "N/A"

            else:
                status = "DETECTEE"
                error_text = f"{error:+.3f}"

                if error < -0.12:
                    direction = "GAUCHE"

                elif error > 0.12:
                    direction = "DROITE"

                else:
                    direction = "TOUT DROIT"

            print(
                f"\rLigne: {status:<12} | "
                f"Erreur: {error_text:<7} | "
                f"Direction: {direction:<11} | "
                f"Pixels masque: {detected_pixels:<7}",
                end="",
                flush=True
            )

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n\n[INFO] Test interrompu")

    finally:
        camera.stop()
        print("[INFO] Caméra libérée")


if __name__ == "__main__":
    main()
