import cv2
import numpy as np


class LineDetector:
    # Intervalle HSV réservé à la couleur noire (V faible, jusqu'à 80)
    BLACK_LOWER = np.array([0, 0, 0], dtype=np.uint8)
    BLACK_UPPER = np.array([180, 255, 80], dtype=np.uint8)

    def __init__(self, min_area=500):
        self.min_area = min_area

    def detect(self, frame):
        """
        Détecte la ligne noire présente dans l'image.

        Returns:
            error: position normalisée de la ligne entre -1 et 1
            mask: image binaire utilisée pour la détection
        """
        height, width = frame.shape[:2]

        # Sélectionner uniquement la partie inférieure de l'image
        roi = frame[int(height * 0.5):height, :]

        # Convertir l'image de BGR en HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Créer un masque directement pour le noir
        mask = cv2.inRange(hsv, self.BLACK_LOWER, self.BLACK_UPPER)

        # Créer un noyau et appliquer des opérations morphologiques pour éliminer le bruit
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Rechercher les contours dans le masque
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return None, mask

        # Sélectionner le plus grand contour
        largest_contour = max(contours, key=cv2.contourArea)

        # Ignorer les contours trop petits
        if cv2.contourArea(largest_contour) < self.min_area:
            return None, mask

        # Calculer les moments pour trouver le centroïde
        moments = cv2.moments(largest_contour)
        if moments["m00"] == 0:
            return None, mask

        cx = int(moments["m10"] / moments["m00"])

        # Convertir la position horizontale en une erreur normalisée entre -1 et 1
        roi_width = roi.shape[1]
        error = (cx - roi_width / 2) / (roi_width / 2)
        error = max(-1.0, min(1.0, error))

        return error, mask