import cv2

from navigation.camera import Camera
from navigation.line_detection import LineDetector


camera = Camera(
    camera_index=0,
    width=640,
    height=480
)

detector = LineDetector()

camera.start()

try:

    while True:

        frame = camera.read()

        error, mask = detector.detect(frame)

        if error is None:
            print("Ligne non détectée")
        else:
            print(f"Erreur: {error:.2f}")

        cv2.imshow("Camera", frame)
        cv2.imshow("Line Mask", mask)

        if cv2.waitKey(1) == 27:
            break

finally:

    camera.stop()
    cv2.destroyAllWindows()