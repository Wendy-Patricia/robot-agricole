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

    def __init__(self, min_area=500, color="black", hsv_ranges=None):
        self.min_area = min_area
        self.color = color.lower()
        if self.color not in self.COLOR_RANGES:
            available_colors = ", ".join(self.COLOR_RANGES)
            raise ValueError(
                f"Cor desconhecida: {color}. Cores disponíveis: {available_colors}"
            )
        selected_ranges = self.COLOR_RANGES[self.color] if hsv_ranges is None else hsv_ranges
        self.hsv_ranges = self._validate_hsv_ranges(selected_ranges)

    @staticmethod
    def _validate_hsv_ranges(hsv_ranges):
        channel_max = np.array([180, 255, 255])
        if len(hsv_ranges) == 0:
            raise ValueError("É necessário fornecer pelo menos um intervalo HSV")

        validated_ranges = []
        for bounds in hsv_ranges:
            if len(bounds) != 2:
                raise ValueError("Cada intervalo HSV deve conter limites inferior e superior")

            lower = np.asarray(bounds[0])
            upper = np.asarray(bounds[1])
            if lower.shape != (3,) or upper.shape != (3,):
                raise ValueError("Cada limite HSV deve conter exatamente 3 valores")
            if not np.issubdtype(lower.dtype, np.integer) or not np.issubdtype(
                upper.dtype, np.integer
            ):
                raise ValueError("Os limites HSV devem ser números inteiros")
            if (
                np.any(lower < 0)
                or np.any(lower > channel_max)
                or np.any(upper < 0)
                or np.any(upper > channel_max)
            ):
                raise ValueError("Os limites HSV estão fora do intervalo permitido")
            if np.any(lower > upper):
                raise ValueError("O limite inferior HSV não pode exceder o superior")

            validated_ranges.append((lower.astype(np.uint8), upper.astype(np.uint8)))

        return tuple(validated_ranges)

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
        for lower, upper in self.hsv_ranges:
            color_mask = cv2.inRange(
                hsv,
                lower,
                upper
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