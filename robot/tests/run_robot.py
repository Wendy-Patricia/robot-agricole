import argparse
import sys
import time
import cv2

# Ajuste os imports para os nomes exatos dos seus arquivos:
from robot.navigation.motors import MotorController
from robot.navigation.line_detection import LineDetector
from robot.navigation.navigation import Navigation


class PiCameraWrapper:
    """
    Wrapper compatível com câmera USB (OpenCV) ou Picamera2 (libcamera).
    """
    def __init__(self, width=320, height=240, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        self.cap = None
        self.picam2 = None

    def start(self):
        # Tenta usar Picamera2 primeiro (padrão no Raspberry Pi OS moderno)
        try:
            from picamera2 import Picamera2
            self.picam2 = Picamera2()
            config = self.picam2.create_preview_configuration(
                main={"size": (self.width, self.height), "format": "RGB888"}
            )
            self.picam2.configure(config)
            self.picam2.start()
            time.sleep(0.5)  # Aguarda estabilização do balanço de branco
            print("[CAMERA] Picamera2 iniciada.")
            return
        except Exception:
            self.picam2 = None

        # Fallback para câmera USB / V4L2 via OpenCV
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)

        if not self.cap.isOpened():
            raise RuntimeError("Não foi possível abrir nenhuma câmera na Raspberry Pi.")
        print("[CAMERA] Câmera OpenCV iniciada.")

    def read(self):
        if self.picam2 is not None:
            frame = self.picam2.capture_array()
            return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        ret, frame = self.cap.read()
        return frame if ret else None

    def stop(self):
        if self.picam2 is not None:
            self.picam2.stop()
        if self.cap is not None:
            self.cap.release()
        print("[CAMERA] Câmera encerrada.")


class DryRunMotors:
    """Simula os motores no terminal para teste seguro em bancada."""
    def drive(self, left, right):
        print(f"[SIMULADO] Esq: {left:5.1f}% | Dir: {right:5.1f}%")
        return left, right

    def stop(self):
        print("[SIMULADO] Motores parados")

    def cleanup(self):
        pass


def main():
    parser = argparse.ArgumentParser(description="Teste do robô seguidor de linha na Raspberry Pi")
    parser.add_argument("--dry-run", action="store_true", help="Testa câmera e PID sem ligar os motores")
    parser.add_argument("--gui", action="store_true", help="Abre janelas do OpenCV (use apenas com monitor conectado)")
    parser.add_argument("--speed", type=float, default=35.0, help="Velocidade base (0 a 100)")
    parser.add_argument("--kp", type=float, default=18.0, help="Ganho Proporcional (P)")
    parser.add_argument("--ki", type=float, default=0.0, help="Ganho Integral (I)")
    parser.add_argument("--kd", type=float, default=6.0, help="Ganho Derivativo (D)")
    args = parser.parse_args()

    motors = None
    try:
        camera = PiCameraWrapper(width=320, height=240, fps=30)
        detector = LineDetector(min_area=400)

        if args.dry_run:
            print("=== MODO BANCADA (MOTORES DESATIVADOS) ===")
            motors = DryRunMotors()
        else:
            print("=== MODO PISTA (MOTORES ATIVOS) ===")
            motors = MotorController()

        nav = Navigation(
            camera=camera,
            line_detector=detector,
            motor_controller=motors,
            base_speed=args.speed,
            min_speed=20.0,
            max_speed=60.0,
            kp=args.kp,
            ki=args.ki,
            kd=args.kd,
            lost_limit=10
        )

        # show_debug=False por padrão para não travar se você estiver rodando via SSH
        nav.run(show_debug=args.gui)

    except KeyboardInterrupt:
        print("\nParada solicitada pelo usuário.")
    finally:
        if motors is not None:
            motors.cleanup()


if __name__ == "__main__":
    main()