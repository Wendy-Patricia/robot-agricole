"""Ensaio manual no robo. Nao e um teste unitario nem ativa GPIO ao importar."""

import argparse
from pathlib import Path
import sys
import time

import cv2

# Permitir executar diretamente a partir de qualquer pasta no Raspberry Pi.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from navigation.camera import Camera
from navigation.line_detection import LineDetector
from navigation.navigation import Navigator


class PreviewMotors:
    """Modo de ajuste da camera sem ativar os motores."""

    def drive(self, left, right):
        pass

    def stop(self):
        pass

    def cleanup(self):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--drive", action="store_true", help="Ativar motores reais")
    parser.add_argument("--display", action="store_true", help="Mostrar camera e mascara (ecra local)")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--speed", type=float, default=30)
    parser.add_argument("--min-speed", type=float, default=16)
    parser.add_argument("--max-speed", type=float, default=60)
    parser.add_argument("--kp", type=float, default=40)
    parser.add_argument("--kd", type=float, default=1.5)
    parser.add_argument("--threshold", type=int, default=80, help="Limiar de preto: 0 a 255")
    parser.add_argument("--min-area", type=float, default=500)
    args = parser.parse_args()

    camera = Camera(camera_index=args.camera)
    motors = PreviewMotors()
    navigator = Navigator(
        camera, motors, LineDetector(args.min_area, args.threshold),
        base_speed=args.speed, min_speed=args.min_speed, max_speed=args.max_speed,
        kp=args.kp, kd=args.kd,
    )
    try:
        camera.start()
        if args.drive:
            from navigation.motors import MotorController
            motors = MotorController()
            navigator.motors = motors
        print("MOTORES ATIVOS" if args.drive else "PREVISAO: motores desativados")
        print("Ctrl+C para parar. Com janela: Q ou Esc para sair.")
        last_log = 0.0
        while True:
            error = navigator.step()
            left, right = navigator.last_speeds
            status = "LINHA PERDIDA - PARADO" if error is None else f"erro={error:+.3f}"
            if time.monotonic() - last_log >= 0.2:
                print(f"\r{status:<30} esquerda={left:5.1f}% direita={right:5.1f}%", end="", flush=True)
                last_log = time.monotonic()
            if args.display:
                frame = navigator.last_frame.copy()
                height, width = frame.shape[:2]
                cv2.line(frame, (width // 2, height // 2), (width // 2, height), (255, 0, 0), 2)
                points = navigator.detector.points
                for index, point in enumerate(points):
                    cv2.circle(frame, point, 6, (0, 255, 0), -1)
                    if index:
                        cv2.line(frame, points[index - 1], point, (0, 255, 255), 2)
                cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.imshow("Seguimento de linha", frame)
                cv2.imshow("Mascara", navigator.last_mask)
                if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                    break
    except KeyboardInterrupt:
        print("\nParagem pedida.")
    finally:
        try:
            motors.cleanup()
        finally:
            camera.stop()
            if args.display:
                cv2.destroyAllWindows()
            print()


if __name__ == "__main__":
    main()
