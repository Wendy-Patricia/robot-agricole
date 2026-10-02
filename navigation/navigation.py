from line_detection import LineDetector


class Navigation:
    def __init__(
        self,
        motors,
        line_detector=None,
        threshold=0.2,
        speed=50
    ):
        self.motors = motors

        if line_detector is None:
            self.line_detector = LineDetector()
        else:
            self.line_detector = line_detector

        self.threshold = threshold
        self.speed = speed

        self.running = False

    def start(self):
        """Démarre la navigation autonome."""
        self.running = True

    def stop(self):
        """Arrête la navigation autonome."""
        self.running = False
        self.motors.stop()

    def process_frame(self, frame):
        """
        Analyse une image et décide du déplacement du robot.

        Returns:
            error: erreur de position de la ligne
        """

        # Détecter la ligne dans l'image
        error, _ = self.line_detector.detect(frame)

        # Si aucune ligne n'est détectée, arrêter le robot
        if error is None:
            self.motors.stop()
            return None

        # Vérifier si la navigation est active
        if not self.running:
            self.motors.stop()
            return error

        # La ligne est trop à gauche
        if error < -self.threshold:
            self.motors.turn_left(self.speed)

        # La ligne est suffisamment centrée
        elif error <= self.threshold:
            self.motors.forward(self.speed)

        # La ligne est trop à droite
        else:
            self.motors.turn_right(self.speed)

        return error