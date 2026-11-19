
import cv2
from pathlib import Path

from robot.navigation.camera import Camera
from robot.navigation.line_detection import LineDetector


def main():
    camera = Camera(camera_index=0, width=640, height=480)
    detector = LineDetector(min_area=500)

    output = Path("debug_navigation")
    output.mkdir(exist_ok=True)

    try:
        camera.start()

        frame = camera.read()
        error, mask = detector.detect(frame)

        height, width = frame.shape[:2]
        roi_y = int(height * 0.5)

        # Imagem original
        cv2.imwrite(str(output / "camera.jpg"), frame)

        # Máscara da deteção
        cv2.imwrite(str(output / "mask.jpg"), mask)

        # Imagem com diagnóstico
        debug = frame.copy()

        # Limite da região analisada
        cv2.line(
            debug,
            (0, roi_y),
            (width, roi_y),
            (0, 255, 255),
            2
        )

        # Centro da imagem
        cv2.line(
            debug,
            (width // 2, 0),
            (width // 2, height),
            (255, 0, 0),
            2
        )

        if error is not None:
            cx = int((error + 1) * width / 2)

            cv2.circle(
                debug,
                (cx, int(height * 0.75)),
                10,
                (0, 0, 255),
                -1
            )

            print(f"Ligne détectée : erreur = {error:+.3f}")
            print(f"Position horizontale : {cx}/{width}")

        else:
            print("Aucune ligne détectée")

        cv2.imwrite(
            str(output / "camera_debug.jpg"),
            debug
        )

        print("Images enregistrées dans debug_navigation/")

    finally:
        camera.stop()


if __name__ == "__main__":
    main()
