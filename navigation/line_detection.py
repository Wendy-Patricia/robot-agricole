import cv2
import numpy as np


class LineDetector:
    def __init__(self, min_area=500):
        self.min_area = min_area

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

        # Définir la couleur recherchée
        # Ici, on recherche une ligne noire ou très sombre
        lower = np.array([0, 0, 0])
        upper = np.array([180, 255, 80])

        # Créer un masque contenant uniquement la couleur recherchée
        mask = cv2.inRange(hsv, lower, upper)

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