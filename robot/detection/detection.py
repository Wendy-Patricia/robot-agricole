import cv2
import numpy as np


class DetecteurMenace:
    """
    Gère la détection et la localisation des menaces dans une image.
    """

    def detecter(self, image):
        """
        Détecte une menace simulée représentée en rouge.

        Retourne un dictionnaire contenant l'état de la détection,
        le type de menace et sa position dans l'image.
        """

        if image is None:
            return self._aucune_menace()

        # Conversion de l'image de BGR vers HSV
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Définition des deux intervalles correspondant au rouge en HSV
        masque_1 = cv2.inRange(
            image_hsv,
            np.array([0, 100, 100]),
            np.array([10, 255, 255])
        )

        masque_2 = cv2.inRange(
            image_hsv,
            np.array([170, 100, 100]),
            np.array([180, 255, 255])
        )

        masque = cv2.bitwise_or(masque_1, masque_2)

        # Recherche des objets présents dans le masque
        contours, _ = cv2.findContours(
            masque,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return self._aucune_menace()

        # Sélection du plus grand objet détecté
        contour = max(contours, key=cv2.contourArea)

        moments = cv2.moments(contour)

        if moments["m00"] == 0:
            return self._aucune_menace()

        # Calcul du centre de la menace
        position_x = int(moments["m10"] / moments["m00"])
        position_y = int(moments["m01"] / moments["m00"])

        return {
            "detectee": True,
            "type": "menace_simulee",
            "x": position_x,
            "y": position_y
        }

    def _aucune_menace(self):
        """Retourne le résultat correspondant à l'absence de menace."""

        return {
            "detectee": False,
            "type": None,
            "x": None,
            "y": None
        }