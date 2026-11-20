"""Detecao de uma linha preta sobre fundo claro, incluindo curvas."""

import cv2
import numpy as np


class LineDetector:
    def __init__(self, min_area=500, black_threshold=80):
        if min_area <= 0 or not 0 <= black_threshold <= 255:
            raise ValueError("min_area deve ser positivo e o limiar entre 0 e 255")
        self.min_area = min_area
        self.black_threshold = black_threshold
        self.points = []
        self.curvature = 0.0

    def detect(self, frame):
        """Devolve (erro normalizado, mascara da metade inferior).

        O erro e negativo a esquerda e positivo a direita. As faixas
        proximas corrigem a posicao; as distantes antecipam as curvas.
        points guarda coordenadas na imagem original para visualizacao.
        """
        self.points = []
        self.curvature = 0.0
        if frame is None or frame.size == 0:
            raise ValueError("Imagem da camera indisponivel")
        height, width = frame.shape[:2]
        if height < 8 or width < 2:
            raise ValueError("Imagem demasiado pequena")
        offset_y = height // 2
        roi = frame[offset_y:, :]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (0, 0, 0), (180, 255, self.black_threshold))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        largest = max(contours, key=cv2.contourArea, default=None)
        if largest is None or cv2.contourArea(largest) < self.min_area:
            return None, mask

        # Medir a mesma linha em todas as faixas, sem misturar outras manchas.
        component = np.zeros_like(mask)
        cv2.drawContours(component, [largest], -1, 255, cv2.FILLED)
        component = cv2.bitwise_and(component, mask)
        center_x = (width - 1) / 2
        roi_height = roi.shape[0]
        measurements = []
        # De baixo (perto do robo) para cima (antecipacao).
        for lower, upper, weight in ((0.66, 1.0, 0.55),
                                     (0.33, 0.66, 0.30),
                                     (0.0, 0.33, 0.15)):
            y0, y1 = int(roi_height * lower), int(roi_height * upper)
            moments = cv2.moments(component[y0:y1], binaryImage=True)
            if moments["m00"] < max(5, self.min_area * 0.03):
                continue
            x = moments["m10"] / moments["m00"]
            y = offset_y + y0 + moments["m01"] / moments["m00"]
            self.points.append((int(round(x)), int(round(y))))
            measurements.append(((x - center_x) / center_x, weight))

        if not measurements:
            return None, mask
        self.curvature = measurements[-1][0] - measurements[0][0]
        position = sum(error * weight for error, weight in measurements)
        position /= sum(weight for _, weight in measurements)
        error = position + 0.35 * self.curvature
        return max(-1.0, min(1.0, error)), mask
