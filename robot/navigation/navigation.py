class Navigation:
    """
    Navigation autonome fluide avec contrôleur PID.
    """

    def __init__(
        self,
        camera,
        line_detector,
        motor_controller,
        base_speed=38.0,
        min_speed=25.0,
        max_speed=55.0,
        kp=18.0,      # Ganho Proporcional (força da curva)
        ki=0.05,      # Ganho Integral (corrige desvio acumulado)
        kd=6.5,       # Ganho Derivativo (amortece e evita o tremor)
        lost_limit=8
    ):
        self.camera = camera
        self.line_detector = line_detector
        self.motors = motor_controller

        self.base_speed = base_speed
        self.min_speed = min_speed
        self.max_speed = max_speed

        # Parâmetros PID
        self.kp = kp
        self.ki = ki
        self.kd = kd

        # Estados do PID
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = None

        # Filtragem leve para suavizar ruído da câmera
        self.filtered_error = None
        self.alpha = 0.5  # Maior resposta que 0.35 para o D funcionar bem

        # Segurança
        self.lost_limit = max(1, lost_limit)
        self.lost_frames = 0
        self.safety_locked = False
        self.running = False
        self.motors_stopped = True

    def _reset_pid(self):
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = None
        self.filtered_error = None

    def _stop_motors(self):
        if not self.motors_stopped:
            self.motors.stop()
            self.motors_stopped = True

    def handle_lost_line(self):
        self.lost_frames += 1
        self._reset_pid()
        self._stop_motors()

        if self.lost_frames >= self.lost_limit:
            if not self.safety_locked:
                print("[SECURITE] Ligne perdue. Navigation verrouillée.")
            self.safety_locked = True

        return "LOST"

    def navigate(self, error):
        """
        Calcula o ajuste PID e envia velocidades contínuas para os motores.
        error < 0 : linha à esquerda -> desacelera esquerda, acelera direita
        error > 0 : linha à direita  -> acelera esquerda, desacelera direita
        """
        if self.safety_locked:
            self._stop_motors()
            return "SAFE_STOP"

        if error is None or not math.isfinite(float(error)) or abs(error) > 1.0:
            return self.handle_lost_line()

        self.lost_frames = 0
        error = float(error)

        # Filtro passa-baixa leve
        if self.filtered_error is None:
            self.filtered_error = error
        else:
            self.filtered_error = (
                self.alpha * error + (1.0 - self.alpha) * self.filtered_error
            )

        # Cálculo do delta de tempo (dt) entre frames
        now = time.monotonic()
        if self.last_time is None:
            dt = 0.033  # ~30 FPS inicial
        else:
            dt = max(1e-3, now - self.last_time)
        self.last_time = now

        # Termo P (Proporcional)
        p_term = self.kp * self.filtered_error

        # Termo I (Integral com Anti-Windup para não acumular demais)
        self.integral += self.filtered_error * dt
        self.integral = max(-1.5, min(1.5, self.integral))
        i_term = self.ki * self.integral

        # Termo D (Derivativo - freia a oscilação)
        derivative = (self.filtered_error - self.last_error) / dt
        d_term = self.kd * derivative

        self.last_error = self.filtered_error

        # Correção final (em unidades de duty cycle PWM)
        correction = p_term + i_term + d_term

        # Reduz levemente a velocidade base em curvas muito fechadas
        current_base = self.base_speed * (1.0 - 0.25 * min(abs(self.filtered_error), 1.0))

        # Direção diferencial: uma roda acelera, a outra reduz
        left_speed = current_base + correction
        right_speed = current_base - correction

        # Limita dentro da faixa segura dos motores
        left_speed = max(self.min_speed, min(self.max_speed, left_speed))
        right_speed = max(self.min_speed, min(self.max_speed, right_speed))

        self.motors.drive(left_speed, right_speed)
        self.motors_stopped = False

        if abs(self.filtered_error) < 0.08:
            return "FORWARD"
        return "LEFT" if self.filtered_error < 0 else "RIGHT"

    def draw_debug(self, frame, error, direction):
        height, width = frame.shape[:2]
        center_x = width // 2
        reference_y = int(height * 0.75)

        cv2.line(frame, (center_x, 0), (center_x, height), (255, 0, 0), 2)

        if error is not None and math.isfinite(float(error)):
            line_x = int(center_x + error * center_x)
            line_x = max(0, min(width - 1, line_x))
            cv2.circle(frame, (line_x, reference_y), 8, (0, 255, 0), -1)
            error_text = f"Erreur brute: {error:+.3f}"
        else:
            error_text = "Ligne non detectee"

        filtered_text = (
            f"Erreur PID: {self.filtered_error:+.3f}"
            if self.filtered_error is not None
            else "Erreur PID: N/A"
        )

        cv2.putText(frame, error_text, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, filtered_text, (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Direction: {direction}", (15, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        if self.safety_locked:
            cv2.putText(frame, "ARRET SECURITE", (15, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return frame

    def run(self, show_debug=True):
        self.running = True
        try:
            self.camera.start()
            print("[NAVIGATION] Démarrage avec contrôleur PID")

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