import cv2
import numpy as np


# Création d'une image noire de 640 x 480 pixels
image = np.zeros((480, 640, 3), dtype=np.uint8)

# Simulation d'une menace avec un cercle rouge
cv2.circle(image, (320, 240), 40, (0, 0, 255), -1)

# Enregistrement de l'image utilisée pour les tests
cv2.imwrite("tests/images/menace_simulee.jpg", image)

print("Image de test créée avec succès.")