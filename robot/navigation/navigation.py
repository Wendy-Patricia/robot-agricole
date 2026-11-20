import cv2
import math
import time


class Navigation:
    """
    Navigation autonome fluide (contrôle différentiel PD).
    """

    def __init__(
        self,
        camera,
        line_detector,
        motor_controller,
        base_speed=45,
        min_speed=20,
        max_speed=65,
        kp=28.0,
        kd=12.0,
        tolerance=0.08,
        lost_limit=10
    ):
        self.camera = camera
        self.line_detector = line_detector
        self.motors = motor_controller

        self.base_speed = base_speed
        self.min_speed = min_speed
        self.max_speed = max_speed

        # Ganhos PD em escala de PWM (0 a 100)
        self.kp = kp
        self.kd = kd
        self.tolerance = tolerance

        self.lost_limit = max(1, lost_limit)
        self.lost_frames = 0

        self.filtered_error = None
        self.last_error = 0.0
        self.alpha = 0.65  # Mais reativo (menos atraso)

        self.safety_locked = False
        self.running = False
        self.motors_stopped = True
        self.last_direction = "STOP"

    def _stop_motors(self):
        if not self.motors_stopped:
            self.motors.stop()
            self.motors_stopped = True

    def handle_lost_line(self):
        self.lost_frames += 1

        # Se perdeu há pouco tempo (1 a 4 frames), continua virando suavemente
        # para o último lado onde a linha foi vista antes de desistir
        if self.lost_frames < 5 and abs(self.last_error) > 0.15:
            if self.last_error < 0:
                self.motors.drive(self.min_speed, self.base_speed)
                self.last_direction = "SEARCH_LEFT"
            else:
                self.motors.drive(self.base_speed, self.min_speed)
                self.last_direction = "SEARCH_RIGHT"
            self.motors_stopped = False
            return self.last_direction

        self._stop_motors()
        self.filtered_error = None

        if self.lost_frames >= self.lost_limit:
            if not self.safety_locked:
                print("[SECURITE] Ligne perdue. Navigation verrouillée.")
            self.safety_locked = True

        self.last_direction = "LOST"
        return "LOST"

    def navigate(self, error):
        if self.safety_locked:
            self._stop_motors()
            return "SAFE_STOP"

        if error is None or not math.isfinite(float(error)) or abs(float(error)) > 1.0:
            return self.handle_lost_line()

        error = float(error)
        self.lost_frames = 0

        # Filtro suave sem atraso excessivo
        if self.filtered_error is None:
            self.filtered_error = error
        else:
            self.filtered_error = (
                self.alpha * error + (1.0 - self.alpha) * self.filtered_error
            )

        # Zona morta pequena para andar reto sem ziguezague
        if abs(self.filtered_error) <= self.tolerance:
            effective_error = 0.0
        else:
            effective_error = self.filtered_error

        # Cálculo PD (Proporcional + Derivativo para amortecer oscilações)
        derivative = effective_error - self.last_error
        steering = (self.kp * effective_error) + (self.kd * derivative)
        self.last_error = effective_error

        # Reduz ligeiramente a velocidade base em curvas fechadas
        current_base = self.base_speed * (1.0 - 0.25 * min(abs(effective_error), 1.0))

        # Se error < 0 (linha à esquerda) -> steering < 0 -> reduz roda esquerda, acelera direita
        # Se error > 0 (linha à direita)  -> steering > 0 -> acelera roda esquerda, reduz direita
        left_speed = current_base + steering
        right_speed = current_base - steering

        left_speed = max(0.0, min(self.max_speed, left_speed))
        right_speed = max(0.0, min(self.max_speed, right_speed))

        # Evita zona morta onde o motor apita mas não gira (exceto se for intencional 0)
        if 0 < left_speed < self.min_speed:
            left_speed = self.min_speed
        if 0 < right_speed < self.min_speed:
            right_speed = self.min_speed

        self.motors.drive(left_speed, right_speed)
        self.motors_stopped = False

        if effective_error == 0.0:
            self.last_direction = "FORWARD"
        elif effective_error < 0:
            self.last_direction = f"LEFT ({left_speed:.0f}/{right_speed:.0f})"
        else:
            self.last_direction = f"RIGHT ({left_speed:.0f}/{right_speed:.0f})"

        return self.last_direction

    def draw_debug(self, frame, error, direction):
        height, width = frame.shape[:2]
        center_x = width // 2
        reference_y = int(height * 0.78)

        cv2.line(frame, (center_x, 0), (center_x, height), (255, 0, 0), 2)

        if error is not None and math.isfinite(float(error)):
            line_x = max(0, min(width - 1, int(center_x + error * center_x)))
            cv2.circle(frame, (line_x, reference_y), 8, (0, 255, 0), -1)
            error_text = f"Erreur brute: {error:+.3f}"
        else:
            error_text = "Ligne non detectee"

        filtered_text = (
            f"Erreur filtree: {self.filtered_error:+.3f}"
            if self.filtered_error is not None
            else "Erreur filtree: N/A"
        )

        cv2.putText(frame, error_text, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, filtered_text, (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Action: {direction}", (15, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        if self.safety_locked:
            cv2.putText(frame, "ARRET SECURITE", (15, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return frame

    def run(self, show_debug=True):
        self.running = True
        try:
            self.camera.start()
            print("[NAVIGATION] Démarrage - Suivi différentiel actif")

            while self.running:
                frame = self.camera.read()
                if frame is None or frame.size == 0:
                    self.navigate(None)
                    if self.safety_locked:
                        break
                    time.sleep(0.02)
                    continue

                error, mask = self.line_detector.detect(frame)
                direction = self.navigate(error)

                if show_debug:
                    debug_frame = self.draw_debug(frame.copy(), error, direction)
                    cv2.imshow("Robot - Navigation", debug_frame)
                    if mask is not None:
                        cv2.imshow("Robot - Masque", mask)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

                if self.safety_locked:
                    print("[NAVIGATION] Arrêt de sécurité.")
                    break

        except KeyboardInterrupt:
            print("[NAVIGATION] Interruption utilisateur")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        self._stop_motors()
        self.camera.stop()
        cv2.destroyAllWindows()
        print("[NAVIGATION] Robot arrêté")