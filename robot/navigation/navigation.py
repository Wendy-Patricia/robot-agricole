
import cv2
import math
import time


class Navigation:
    """
    Navigation autonome du robot agricole.

    - Suivi d'une ligne noire
    - Filtrage des erreurs de détection
    - Corrections courtes
    - Nouvelle observation après chaque correction
    - Arrêt de sécurité en cas de perte de ligne
    """

    def __init__(
        self,
        camera,
        line_detector,
        motor_controller,
        base_speed=35,
        min_speed=30,
        max_speed=45,
        kp=0.5,
        tolerance=0.15,
        lost_limit=5,
        correction_time=0.06
    ):
        self.camera = camera
        self.line_detector = line_detector
        self.motors = motor_controller

        self.min_speed = min_speed
        self.max_speed = max_speed
        self.base_speed = base_speed

        self.kp = kp
        self.tolerance = tolerance
        self.correction_time = correction_time

        self.lost_limit = max(1, lost_limit)
        self.lost_frames = 0

        self.filtered_error = None
        self.last_error = 0.0

        # Filtrage temporel
        self.alpha = 0.35
        self.max_error_jump = 0.65

        # Récupération après une perte
        self.recovery_frames = 3
        self.valid_frames = 0

        # Sécurité
        self.safety_locked = False
        self.running = False
        self.motors_stopped = True

        self.last_direction = "STOP"

    def calculate_speed(self, error):
        """
        Réduit la vitesse lorsque l'erreur augmente.
        """

        intensity = min(abs(error), 1.0)

        speed = self.base_speed * (
            1.0 - 0.4 * intensity
        )

        return max(
            self.min_speed,
            min(self.max_speed, speed)
        )

    def _stop_motors(self):
        if not self.motors_stopped:
            self.motors.stop()
            self.motors_stopped = True

    def _move_forward(self, speed):
        self.motors.forward(speed)
        self.motors_stopped = False

    def _turn(self, direction, speed, duration):
        """
        Effectue une courte rotation, puis s'arrête.

        Une nouvelle image doit être analysée avant
        toute autre commande de mouvement.
        """

        turn_speed = min(speed, 35)

        try:
            if direction == "LEFT":
                self.motors.turn_left(turn_speed)
            else:
                self.motors.turn_right(turn_speed)

            self.motors_stopped = False

            time.sleep(duration)

        finally:
            self._stop_motors()

    def handle_lost_line(self):
        """
        Arrête les moteurs immédiatement lorsque
        la ligne n'est plus détectée.
        """

        self.lost_frames += 1
        self.valid_frames = 0
        self.filtered_error = None

        self._stop_motors()

        if self.lost_frames >= self.lost_limit:
            if not self.safety_locked:
                print(
                    "[SECURITE] Ligne perdue. "
                    "Navigation verrouillée."
                )

            self.safety_locked = True

        self.last_direction = "LOST"

        return "LOST"

    def navigate(self, error):
        """
        Prend une décision à partir de l'erreur.

        error < 0 : ligne à gauche
        error > 0 : ligne à droite
        """

        if self.safety_locked:
            self._stop_motors()
            return "SAFE_STOP"

        if error is None:
            return self.handle_lost_line()

        error = float(error)

        if not math.isfinite(error):
            return self.handle_lost_line()

        if abs(error) > 1.0:
            return self.handle_lost_line()

        # Rejeter les changements trop importants
        if self.filtered_error is not None:
            difference = abs(
                error - self.filtered_error
            )

            if difference > self.max_error_jump:
                return self.handle_lost_line()

        # Filtrage exponentiel
        if self.filtered_error is None:
            self.filtered_error = error
        else:
            self.filtered_error = (
                self.alpha * error
                + (1 - self.alpha) * self.filtered_error
            )

        # Attendre plusieurs images valides
        # après une perte de ligne
        if self.lost_frames > 0:
            self.valid_frames += 1

            if self.valid_frames < self.recovery_frames:
                self._stop_motors()
                return "RECOVERY"

            self.lost_frames = 0
            self.valid_frames = 0

        self.last_error = self.filtered_error

        speed = self.calculate_speed(
            self.filtered_error
        )

        # Ligne centrée
        if abs(self.filtered_error) <= self.tolerance:
            self._move_forward(speed)
            self.last_direction = "FORWARD"

            return "FORWARD"

        # Calcul de la correction
        correction = min(
            abs(self.filtered_error) * self.kp,
            1.0
        )

        duration = self.correction_time * correction
        duration = max(0.02, min(0.07, duration))

        if self.filtered_error < 0:
            direction = "LEFT"
        else:
            direction = "RIGHT"

        self._turn(direction, speed, duration)

        self.last_direction = direction

        return direction

    def draw_debug(self, frame, error, direction):
        """
        Affiche les informations de navigation.
        """

        height, width = frame.shape[:2]
        center_x = width // 2
        reference_y = int(height * 0.75)

        cv2.line(
            frame,
            (center_x, 0),
            (center_x, height),
            (255, 0, 0),
            2
        )

        if error is not None and math.isfinite(float(error)):
            line_x = int(
                center_x + error * center_x
            )

            line_x = max(
                0,
                min(width - 1, line_x)
            )

            cv2.circle(
                frame,
                (line_x, reference_y),
                8,
                (0, 255, 0),
                -1
            )

            error_text = f"Erreur brute: {error:+.3f}"
        else:
            error_text = "Ligne non detectee"

        if self.filtered_error is not None:
            filtered_text = (
                f"Erreur filtree: {self.filtered_error:+.3f}"
            )
        else:
            filtered_text = "Erreur filtree: N/A"

        cv2.putText(
            frame,
            error_text,
            (15, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            filtered_text,
            (15, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Direction: {direction}",
            (15, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

        if self.safety_locked:
            cv2.putText(
                frame,
                "ARRET SECURITE",
                (15, 125),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        return frame

    def run(self, show_debug=True):
        """
        Démarre la navigation autonome.
        """

        self.running = True

        try:
            self.camera.start()

            print("[NAVIGATION] Démarrage")
            print("[NAVIGATION] Suivi de ligne actif")

            while self.running:
                frame = self.camera.read()

                if frame is None or frame.size == 0:
                    self.navigate(None)

                    if self.safety_locked:
                        break

                    time.sleep(0.05)
                    continue

                error, mask = self.line_detector.detect(
                    frame
                )

                direction = self.navigate(error)

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

                    if mask is not None:
                        cv2.imshow(
                            "Robot - Masque",
                            mask
                        )

                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

                if self.safety_locked:
                    print(
                        "[NAVIGATION] Arrêt de sécurité. "
                        "Redémarrage nécessaire."
                    )
                    break

        except KeyboardInterrupt:
            print(
                "[NAVIGATION] Interruption utilisateur"
            )

        except Exception as error:
            print(f"[ERREUR] Navigation: {error}")
            raise

        finally:
            self.stop()

    def stop(self):
        """
        Arrêt de la navigation.
        """

        self.running = False
        self._stop_motors()
        self.camera.stop()
        cv2.destroyAllWindows()

        print("[NAVIGATION] Robot arrêté")
