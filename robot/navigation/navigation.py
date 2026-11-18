import math


class Navigation:
    def __init__(
        self,
        motors,
        line_detector,
        threshold: float = 0.2,
        speed: float = 50
    ):
        self.motors = motors
        self.line_detector = line_detector

        threshold = float(threshold)
        speed = float(speed)
        if not math.isfinite(threshold) or threshold < 0:
            raise ValueError("Le seuil doit être un nombre fini positif ou nul.")
        if not math.isfinite(speed):
            raise ValueError("La vitesse doit être un nombre fini.")

        self.threshold = threshold
        self.speed = max(0.0, min(100.0, speed))

        self.running = False
        self._last_command = None

    def start(self):
        """Démarre la navigation autonome."""
        self.running = True

    def stop(self):
        """Arrête la navigation autonome."""
        self.running = False
        # Un arrêt explicite est toujours transmis aux moteurs.
        self._last_command = None
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

        try:
            return self._process_frame(frame)
        except Exception:
            # Une erreur de détection ou de commande interrompt la navigation.
            self.stop()
            raise

    def _process_frame(self, frame):
        error, _ = self.line_detector.detect(frame)

        # Si aucune ligne n'est détectée, arrêter le robot
        if error is None or not math.isfinite(error):
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
