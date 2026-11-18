import cv2


class Camera:
    def __init__(self, camera_index=0, width=640, height=480):
        self.camera_index = camera_index
        self.width = width
        self.height = height

        self.cap = None

    def start(self):
        """Initialise la caméra."""
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            raise RuntimeError("Impossible d'ouvrir la caméra")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def read(self):
        """
        Capture une image.

        Returns:
            frame: image capturée par la caméra
        """
        if self.cap is None:
            raise RuntimeError("La caméra n'est pas démarrée")

        success, frame = self.cap.read()

        if not success:
            raise RuntimeError("Impossible de lire une image depuis la caméra")

        return frame

    def stop(self):
        """Libère la caméra."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def is_opened(self):
        """Indique si la caméra est actuellement ouverte."""
        return self.cap is not None and self.cap.isOpened()