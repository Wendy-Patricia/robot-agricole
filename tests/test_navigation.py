import cv2

from navigation.camera import Camera
from navigation.line_detection import LineDetector
from navigation.navigation import Navigation
from simulation.fake_motors import FakeMotorController


camera = Camera(
    camera_index=0,
    width=640,
    height=480
)

motors = FakeMotorController()
line_detector = LineDetector()

navigation = Navigation(
    motors=motors,
    line_detector=line_detector,
    threshold=0.2,
    speed=50
)

camera.start()
navigation.start()

try:

    while True:

        frame = camera.read()

        error = navigation.process_frame(frame)

        if error is None:
            print("Ligne non détectée")
        else:
            print(f"Erreur: {error:.2f}")

        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) == 27:
            break

finally:

    navigation.stop()
    camera.stop()
    cv2.destroyAllWindows()