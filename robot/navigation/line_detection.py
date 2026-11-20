
import cv2
import numpy as np


class LineDetector:
    """
    Détection et suivi d'une ligne sombre.

    - Seuillage adaptatif
    - Région d'intérêt
    - Filtrage des contours
    - Suivi temporel de la ligne
    - Rejet des changements brusques
    """

    def __init__(
        self,
        min_area=500,
        max_distance_ratio=0.20
    ):
        self.min_area = min_area
        self.max_distance_ratio = max_distance_ratio

        self.last_cx = None
        self.lost_count = 0

    def reset(self):
        """
        Réinitialise le suivi de la ligne.
        """

        self.last_cx = None
        self.lost_count = 0

    def _line_lost(self, mask):
        """
        Gère une image sans ligne valide.
        """

        self.lost_count += 1

        # Après plusieurs images sans détection,
        # oublier la dernière position.
        if self.lost_count >= 3:
            self.last_cx = None

        return None, mask

    def detect(self, frame):
        """
        Détecte la position horizontale de la ligne.

        Returns:
            error: valeur entre -1 et 1, ou None
            mask: masque binaire
        """

        if frame is None or frame.size == 0:
            return self._line_lost(None)

        height, width = frame.shape[:2]

        # Partie inférieure de l'image
        y_start = int(height * 0.50)
        y_end = int(height * 0.95)

        roi = frame[y_start:y_end, :]

        if roi.size == 0:
            return self._line_lost(None)

        # Conversion en niveaux de gris
        gray = cv2.cvtColor(
            roi,
            cv2.COLOR_BGR2GRAY
        )

        # Réduction du bruit
        blurred = cv2.GaussianBlur(
            gray,
            (5, 5),
            0
        )

        # Détection des régions sombres
        mask = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            51,
            9
        )

        # Réunir les fragments de la ligne
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (3, 7)
        )

        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_CLOSE,
            kernel
        )

        # Supprimer de petites régions isolées
        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_OPEN,
            cv2.getStructuringElement(
                cv2.MORPH_RECT,
                (3, 3)
            )
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

            x, y, w, h = cv2.boundingRect(
                contour
            )

            # Exclure les régions trop larges
            if w > width * 0.35:
                continue

            # Privilégier une forme allongée
            if h < w:
                continue

            moments = cv2.moments(contour)

            if moments["m00"] == 0:
                continue

            cx = (
                moments["m10"] / moments["m00"]
            )

            candidates.append(
                (contour, cx, area)
            )

        if not candidates:
            return self._line_lost(mask)

        # Première détection :
        # privilégier une ligne près du centre.
        if self.last_cx is None:
            selected = min(
                candidates,
                key=lambda item: (
                    abs(item[1] - width / 2),
                    -item[2]
                )
            )

        # Détections suivantes :
        # privilégier la continuité.
        else:
            selected = min(
                candidates,
                key=lambda item: abs(
                    item[1] - self.last_cx
                )
            )

            distance = abs(
                selected[1] - self.last_cx
            )

            max_distance = (
                width * self.max_distance_ratio
            )

            if distance > max_distance:
                return self._line_lost(mask)

        cx = selected[1]

        self.last_cx = cx
        self.lost_count = 0

        # Erreur normalisée
        error = (
            (cx - width / 2) / (width / 2)
        )

        error = float(
            np.clip(error, -1.0, 1.0)
        )

        return error, mask
