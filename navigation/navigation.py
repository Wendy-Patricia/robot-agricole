from .line_detection import LineDetector


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
        self._last_command = None

    def start(self):
        """Démarre la navigation autonome."""
        self.running = True

    def stop(self):
        """Arrête la navigation autonome."""
        self.running = False
        self.motors.stop()
        self._last_command = ("stop", None)

    def _apply_command(self, action):
        speed = self.speed if action != "stop" else None
        command = (action, speed)
        if command == self._last_command:
            return

        if action == "stop":
            self.motors.stop()
        else:
            getattr(self.motors, action)(speed)

        self._last_command = command

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
            self._apply_command("stop")
            return None

        # Vérifier si la navigation est active
        if not self.running:
            self._apply_command("stop")
            return error

        # La ligne est trop à gauche
        if error < -self.threshold:
            self._apply_command("turn_left")

        # La ligne est suffisamment centrée
        elif error <= self.threshold:
            self._apply_command("forward")

        # La ligne est trop à droite
        else:
            self._apply_command("turn_right")

        return error