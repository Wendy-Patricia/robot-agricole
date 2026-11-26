from ultralytics import YOLO

# Chargement du modèle YOLOv8 pré-entraîné
modele = YOLO("yolov8n.pt")

# Analyse d'une image de test
resultats = modele.predict(
    source="https://ultralytics.com/images/bus.jpg",
    conf=0.25,
    device="cpu"
)

# Affichage des objets détectés
for resultat in resultats:
    for boite in resultat.boxes:
        classe = int(boite.cls[0])
        confiance = float(boite.conf[0])

        print(
            f"Objet : {modele.names[classe]} | "
            f"Confiance : {confiance:.2f}"
        )

# Enregistrement des résultats avec les bounding boxes
for resultat in resultats:
    resultat.save(filename="tests/images/resultat_yolo.jpg")

print("Test YOLOv8 terminé.")