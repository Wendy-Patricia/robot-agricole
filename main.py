from navigation.camera import Camera
from navigation.line_detection import LineDetector
from navigation.motors import MotorController
from navigation.navigation import Navigation


def main():
    camera = Camera(camera_index=0, width=640, height=480)
    line_detector = LineDetector(color="black")
    motors = MotorController()
    navigation = Navigation(motors=motors, line_detector=line_detector)

    try:
        camera.start()
        navigation.start()

        while True:
            navigation.process_frame(camera.read())
    except KeyboardInterrupt:
        pass
    finally:
        navigation.stop()
        camera.stop()
        motors.cleanup()


if __name__ == "__main__":
    main()