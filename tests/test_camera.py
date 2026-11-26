import cv2

from robot.detection.camera import CameraRobot


def main():
    camera = CameraRobot()

    try:
        camera.ouvrir()

        image = camera.capturer_image()

        cv2.imwrite("photo_python.jpg", image)

        print("Image capturée avec succès.")

    finally:
        camera.liberer()


if __name__ == "__main__":
    main()