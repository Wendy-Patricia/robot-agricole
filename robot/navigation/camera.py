from contextlib import contextmanager

import cv2


@contextmanager
def open_camera(kind, index=0):
    if kind == "usb":
        camera = cv2.VideoCapture(index)
        try:
            if not camera.isOpened():
                raise RuntimeError(f"Impossible d'ouvrir la caméra USB {index}.")

            def read():
                success, frame = camera.read()
                if not success:
                    raise RuntimeError("Impossible de lire une image USB.")
                return frame

            yield read
        finally:
            camera.release()
    else:
        from picamera2 import Picamera2

        camera = Picamera2(index)
        try:
            # RGB888 de Picamera2 fournit les octets dans l'ordre BGR.
            configuration = camera.create_preview_configuration(
                main={"size": (320, 240), "format": "RGB888"}
            )
            camera.configure(configuration)
            camera.start()
            yield camera.capture_array
        finally:
            camera.close()
