import cv2


class CameraRobot:
    """
    Gère la capture d'images depuis la caméra USB du robot.
    """

    def __init__(self, index_camera=0, largeur=640, hauteur=480):
        self.index_camera = index_camera
        self.largeur = largeur
        self.hauteur = hauteur
        self.capture = None

    def ouvrir(self):
        """Ouvre la caméra du robot."""

        self.capture = cv2.VideoCapture(
            self.index_camera,
            cv2.CAP_V4L2
        )

        if not self.capture.isOpened():
            raise RuntimeError(
                "Impossible d'ouvrir la caméra du robot."
            )

        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.largeur)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.hauteur)

    def capturer_image(self):
        """Capture une image depuis la caméra."""

        if self.capture is None or not self.capture.isOpened():
            raise RuntimeError("La caméra n'est pas ouverte.")

        succes, image = self.capture.read()

        if not succes or image is None:
            raise RuntimeError("Échec de la capture d'image.")

        return image

    def liberer(self):
        """Libère les ressources de la caméra."""

        if self.capture is not None:
            self.capture.release()
            self.capture = None