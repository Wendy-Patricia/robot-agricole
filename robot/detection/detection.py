class DetecteurMenace:
    """
    Gère la détection et la localisation des menaces.
    """

    def detecter(self, image):
        """
        Analyse une image afin de rechercher une menace.

        Paramètres :
            image : image à analyser.

        Retourne :
            Un dictionnaire contenant le résultat de la détection :
            - detectee : indique si une menace a été détectée
            - type : type de menace détectée
            - x : position horizontale de la menace dans l'image
            - y : position verticale de la menace dans l'image
        """

        return {
            "detectee": False,
            "type": None,
            "x": None,
            "y": None
        }