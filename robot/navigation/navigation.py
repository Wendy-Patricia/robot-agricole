
import cv2
import time


class Navigation:
    """
    Navigation autonome d'un robot agricole.

    Fonctionnalités :
    - Suivi d'une ligne noire
    - Correction proportionnelle de la direction
    - Adaptation de la vitesse
    - Arrêt de sécurité si la ligne est perdue
    - Visualisation du traitement vidéo
    """

    def __init__(
        self,
        camera,
        line_detector,
        motor_controller,
        base_speed=65,
        min_speed=40,
        max_speed=85,
        kp=0.8,
        tolerance=0.12,
        lost_limit=5,
        correction_time=0.08
    ):
        self.camera = camera
        self.line_detector = line_detector
        self.motors = motor_controller

        # Paramètres de vitesse
        self.base_speed = base_speed
        self.min_speed = min_speed
        self.max_speed = max_speed

        # Contrôleur proportionnel
        self.kp = kp
        self.tolerance = tolerance

        # Sécurité
        self.lost_limit = lost_limit
        self.lost_frames = 0

        # Durée maximale d'une correction
        self.correction_time = correction_time

        self.running = False
        self.last_error = 0.0

    # --------------------------------------------------
    # Calcul de la vitesse
    # --------------------------------------------------

    def calculate_speed(self, error):
        """
        Réduit la vitesse lorsque la ligne
        est éloignée du centre de l'image.
        """

        intensity = min(abs(error), 1.0)

        speed = self.base_speed * (1 - 0.4 * intensity)

        return max(
            self.min_speed,
            min(self.max_speed, speed)
        )

    # --------------------------------------------------
    # Correction de direction
    # --------------------------------------------------

    def navigate(self, error):
        """
        Commande les moteurs à partir de
        l'erreur normalisée entre -1 et 1.

        error < 0 : ligne à gauche
        error > 0 : ligne à droite
        """

        if error is None:
            self.handle_lost_line()
            return "LOST"

        self.lost_frames = 0
        self.last_error = error

        speed = self.calculate_speed(error)

        # Ligne suffisamment centrée
        if abs(error) <= self.tolerance:
            self.motors.forward(speed)
            return "FORWARD"

        # Calcul proportionnel de la correction
        correction = min(
            abs(error) * self.kp,
            1.0
        )

        duration = self.correction_time * correction

        # Ligne à gauche
        if error < 0:
            self.motors.turn_left(speed)
            direction = "LEFT"

        # Ligne à droite
        else:
            self.motors.turn_right(speed)
            direction = "RIGHT"

        # Appliquer une courte rotation
        time.sleep(duration)

        # Reprendre le mouvement en avant
        self.motors.forward(speed)

        return direction

    # --------------------------------------------------
    # Gestion de la perte de ligne
    # --------------------------------------------------

    def handle_lost_line(self):
        """
        Arrête immédiatement le robot
        si la ligne n'est plus visible.
        """

        self.lost_frames += 1
        self.motors.stop()

        if self.lost_frames >= self.lost_limit:
            print(
                "[SECURITE] Ligne perdue. "
                "Robot arrêté."
            )

    # --------------------------------------------------
    # Visualisation
    # --------------------------------------------------

    def draw_debug(self, frame, error, direction):
        """
        Affiche les informations de navigation.
        """

        height, width = frame.shape[:2]
        center_x = width // 2

        # Axe central du robot
        cv2.line(
            frame,
            (center_x, 0),
            (center_x, height),
            (255, 0, 0),
            2
        )

        if error is not None:
            line_x = int(
                center_x + error * center_x
            )

            # Position détectée de la ligne
            cv2.circle(
                frame,
                (line_x, int(height * 0.75)),
                8,
                (0, 255, 0),
                -1
            )

            cv2.line(
                frame,
                (center_x, int(height * 0.75)),
                (line_x, int(height * 0.75)),
                (0, 0, 255),
                2
            )

            error_text = f"Erreur: {error:.2f}"

        else:
            error_text = "Erreur: ligne perdue"

        cv2.putText(
            frame,
            error_text,
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Direction: {direction}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        return frame

    # --------------------------------------------------
    # Boucle principale de navigation
    # --------------------------------------------------

    def run(self, show_debug=True):
        """
        Démarre le suivi autonome de ligne.

        Appuyer sur Q pour arrêter.
        """

        self.running = True

        try:
            self.camera.start()

            print("[NAVIGATION] Démarrage")
            print("[NAVIGATION] Suivi de ligne actif")

            while self.running:

                # Capture de l'image
                frame = self.camera.read()

                # Détection de la ligne noire
                error, mask = self.line_detector.detect(
                    frame
                )

                # Décision de navigation
                direction = self.navigate(error)

                # Affichage
                if show_debug:
                    debug_frame = self.draw_debug(
                        frame.copy(),
                        error,
                        direction
                    )

                    cv2.imshow(
                        "Robot - Navigation",
                        debug_frame
                    )

                    cv2.imshow(
                        "Robot - Masque",
                        mask
                    )

                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

        except KeyboardInterrupt:
            print("[NAVIGATION] Interruption utilisateur")

        except Exception as error:
            print(f"[ERREUR] Navigation: {error}")
            raise

        finally:
            self.stop()

    # --------------------------------------------------
    # Arrêt du système
    # --------------------------------------------------

    def stop(self):
        """
        Arrête proprement la navigation.
        """

        self.running = False

        self.motors.stop()
        self.camera.stop()
        cv2.destroyAllWindows()

        print("[NAVIGATION] Robot arrêté")
