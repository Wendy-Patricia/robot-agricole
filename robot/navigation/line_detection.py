
import cv2
import numpy as np


class LineDetector:
    """
    Détection d'une ligne sombre avec
    seuillage adaptatif.

    Adapté aux variations d'éclairage.
    """

    def __init__(self, min_area=500):
        self.min_area = min_area

    def detect(self, frame):
        """
        Returns:
            error: position normalisée [-1, 1]
            mask: masque binaire
        """

        if frame is None or frame.size == 0:
            return None, None

        height, width = frame.shape[:2]

        # Région inférieure de l'image
        y_start = int(height * 0.50)
        y_end = int(height * 0.95)

        roi = frame[y_start:y_end, :]

        # Conversion en niveaux de gris
        gray = cv2.cvtColor(
            roi,
            cv2.COLOR_BGR2GRAY
        )

        # Réduction du bruit
        blurred = cv2.GaussianBlur(
            gray, (5, 5), 0
        )

        # Seuil adaptatif :
        # détecte les zones sombres par rapport
        # à leur environnement immédiat
        mask = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            51,
            9
        )

        # Réunir les segments de la ligne
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (3, 7)
        )

        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_CLOSE,
            kernel
        )

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        candidates = []

        for contour in contours:
            area = cv2.contourArea(contour)

            if area < self.min_area:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            # Éviter les régions très larges
            # qui ne ressemblent pas à une ligne
            if w > width * 0.35:
                continue

            # Privilégier une structure allongée
            if h < w:
                continue

            candidates.append(contour)

        if not candidates:
            return None, mask

        # Plus grande ligne candidate
        largest = max(
            candidates,
            key=cv2.contourArea
        )

        moments = cv2.moments(largest)

        if moments["m00"] == 0:
            return None, mask

        cx = moments["m10"] / moments["m00"]

        # Erreur horizontale normalisée
        error = (cx - width / 2) / (width / 2)

        error = float(np.clip(error, -1.0, 1.0))

        return error, mask
