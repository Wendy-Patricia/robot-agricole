import cv2
import numpy as np


class LineDetector:
    """
    Détection et suivi d'une ligne noire avec seuillage d'Otsu et filtrage de contraste.
    """

    def __init__(
        self,
        min_area=800,
        max_distance_ratio=0.35,
        dark_threshold=110
    ):
        self.min_area = min_area
        self.max_distance_ratio = max_distance_ratio
        self.dark_threshold = dark_threshold

        self.last_cx = None
        self.lost_count = 0

    def reset(self):
        self.last_cx = None
        self.lost_count = 0

    def _line_lost(self, mask):
        self.lost_count += 1
        if self.lost_count >= 5:
            self.last_cx = None
        return None, mask

    def detect(self, frame):
        if frame is None or frame.size == 0:
            return self._line_lost(None)

        height, width = frame.shape[:2]

        # Focar no terço inferior (mais próximo das rodas, menos distorção)
        y_start = int(height * 0.60)
        y_end = int(height * 0.95)
        roi = frame[y_start:y_end, :]

        if roi.size == 0:
            return self._line_lost(None)

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)

        # Verificar se há contraste real (evita detectar sombras quando não há linha)
        min_val, max_val, _, _ = cv2.minMaxLoc(blurred)
        if (max_val - min_val) < 40:
            return self._line_lost(np.zeros_like(blurred))

        # Seuillage d'Otsu (muito mais estável que adaptiveThreshold para linha preta)
        _, mask = cv2.threshold(
            blurred,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )

        # Limpeza morfológica
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

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
            # Exclui apenas manchas gigantes que ocupam quase a tela toda
            if w > width * 0.65:
                continue

            moments = cv2.moments(contour)
            if moments["m00"] == 0:
                continue

            cx = moments["m10"] / moments["m00"]
            candidates.append((contour, cx, area))

        if not candidates:
            return self._line_lost(mask)

        if self.last_cx is None:
            # Pega o maior contorno próximo ao centro
            selected = max(candidates, key=lambda item: item[2])
        else:
            selected = min(
                candidates,
                key=lambda item: abs(item[1] - self.last_cx)
            )
            if abs(selected[1] - self.last_cx) > (width * self.max_distance_ratio):
                return self._line_lost(mask)

        cx = selected[1]
        self.last_cx = cx
        self.lost_count = 0

        error = (cx - width / 2) / (width / 2)
        error = float(np.clip(error, -1.0, 1.0))

        return error, mask