import cv2

from navigation.camera import Camera


def executar_teste_manual():
    camera = Camera(camera_index=0, width=640, height=480)

    try:
        camera.start()

        while True:
            frame = camera.read()
            cv2.imshow("Camera", frame)

            # ESC para sair
            if cv2.waitKey(1) == 27:
                break
    finally:
        camera.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    executar_teste_manual()