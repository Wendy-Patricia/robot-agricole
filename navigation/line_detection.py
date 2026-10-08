import cv2
import numpy as np


class LineDetector:
    COLOR_RANGES = {
        "black": [([0, 0, 0], [180, 255, 80])],
        "red": [([0, 100, 50], [10, 255, 255]), ([170, 100, 50], [180, 255, 255])],
        "orange": [([11, 100, 50], [20, 255, 255])],
        "yellow": [([21, 100, 50], [35, 255, 255])],
        "green": [([36, 80, 40], [85, 255, 255])],
        "blue": [([86, 80, 40], [130, 255, 255])],
        "purple": [([131, 80, 40], [169, 255, 255])],
    }

    def __init__(self, min_area=500, color="black"):
        self.min_area = min_area
        self.color = color.lower()
        if self.color not in self.COLOR_RANGES:
            available_colors = ", ".join(self.COLOR_RANGES)
            raise ValueError(
                f"Cor desconhecida: {color}. Cores disponíveis: {available_colors}"
            )

    def detect(self, frame):
        """
        Détecte la ligne présente dans l'image.

        Returns:
            error: position normalisée de la ligne entre -1 et 1
            mask: image binaire utilisée pour la détection
        """

        height, width = frame.shape[:2]

        # Sélectionner uniquement la partie inférieure de l'image
        roi = frame[int(height * 0.5):height, :]

        # Convertir l'image du format BGR vers HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Criar uma máscara para cada intervalo HSV da cor selecionada.
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in self.COLOR_RANGES[self.color]:
            color_mask = cv2.inRange(
                hsv,
                np.array(lower, dtype=np.uint8),
                np.array(upper, dtype=np.uint8)
            )
            mask = cv2.bitwise_or(mask, color_mask)

        # Créer un noyau pour supprimer les petits bruits
        kernel = np.ones((5, 5), np.uint8)

        # Supprimer les petits éléments isolés
        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_OPEN,
            kernel
        )

        # Fermer les petits trous dans la ligne
        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_CLOSE,
            kernel
        )

        # Rechercher les contours dans le masque
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Vérifier si aucun contour n'a été trouvé
        if not contours:
            return None, mask

        # Sélectionner le plus grand contour
        largest_contour = max(
            contours,
            key=cv2.contourArea
        )

        # Calculer la surface du contour
        area = cv2.contourArea(largest_contour)

        # Ignorer les contours trop petits
        if area < self.min_area:
            return None, mask

        # Calculer les moments du contour
        moments = cv2.moments(largest_contour)

        # Éviter une division par zéro
        if moments["m00"] == 0:
            return None, mask

        # Calculer la position horizontale du centre de la ligne
        cx = int(moments["m10"] / moments["m00"])

        # Récupérer la largeur de la zone analysée
        roi_width = roi.shape[1]

        # Convertir la position en une valeur comprise entre -1 et 1
        error = (cx - roi_width / 2) / (roi_width / 2)

        # Limiter la valeur entre -1 et 1
        error = max(-1.0, min(1.0, error))

        return error, mask