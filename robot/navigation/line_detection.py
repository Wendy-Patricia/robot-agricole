"""Détection inspirée du line-follower.py de Gregory Mueth (2017)."""

import cv2


def detect_line_center(frame, threshold=100):
    """Renvoie le centre horizontal en pixels et le masque de la zone analysée."""
    height, width = frame.shape[:2]
    roi = frame[height // 2:, :]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY_INV)

    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    min_area = max(10, roi.shape[0] * width * 0.003)
    candidates = [
        contour for contour in contours
        if cv2.contourArea(contour) >= min_area
        and cv2.boundingRect(contour)[2] < width * 0.85
    ]
    if not candidates:
        return None, mask

    largest = max(candidates, key=cv2.contourArea)
    moments = cv2.moments(largest)
    if moments["m00"] == 0:
        return None, mask

    return moments["m10"] / moments["m00"], mask
