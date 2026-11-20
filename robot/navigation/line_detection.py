"""Détection d'une ligne noire sur un fond clair."""

import cv2


class LineDetector:
    def __init__(self, min_area=500, black_threshold=80):
        self.min_area = min_area
        self.black_threshold = black_threshold

    def detect(self, frame):
        """Renvoie (erreur, masque) pour la moitié basse d'une image BGR.

        L'erreur est négative à gauche, positive à droite, et vaut None
        si aucun contour suffisamment grand n'est détecté.
        """
        height, width = frame.shape[:2]
        roi = frame[height // 2:, :]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (0, 0, 0), (180, 255, self.black_threshold))
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        largest = max(contours, key=cv2.contourArea, default=None)
        if largest is None or cv2.contourArea(largest) < self.min_area:
            return None, mask

        moments = cv2.moments(largest)
        if moments["m00"] == 0:
            return None, mask

        center_x = (width - 1) / 2
        line_x = moments["m10"] / moments["m00"]
        error = (line_x - center_x) / center_x
        return error, mask
