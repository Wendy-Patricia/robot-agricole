import argparse
from contextlib import ExitStack
from time import monotonic

import cv2

from .camera import open_camera
from .line_detection import detect_line_center
from .motors import open_motors


def wheel_speeds(center, width, base_speed):
    if center is None:
        return 0.0, 0.0

    midpoint = (width - 1) / 2
    error = (center - midpoint) / midpoint
    correction = base_speed * error
    return (
        max(0.0, min(1.0, base_speed + correction)),
        max(0.0, min(1.0, base_speed - correction)),
    )


def main():
    parser = argparse.ArgumentParser(description="Suivi d'une ligne noire.")
    parser.add_argument("--camera", choices=("csi", "usb"), default="csi")
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--threshold", type=int, default=100)
    parser.add_argument("--speed", type=float, default=0.25)
    parser.add_argument("--drive", action="store_true", help="Active les moteurs.")
    parser.add_argument("--preview", action="store_true", help="Affiche le masque.")
    args = parser.parse_args()
    if not 0 <= args.threshold <= 255:
        parser.error("--threshold doit être compris entre 0 et 255.")
    if not 0 < args.speed <= 1:
        parser.error("--speed doit être supérieur à 0 et inférieur ou égal à 1.")

    try:
        with ExitStack() as resources:
            read = resources.enter_context(open_camera(args.camera, args.camera_index))
            if args.preview:
                resources.callback(cv2.destroyAllWindows)
            drive = resources.enter_context(open_motors()) if args.drive else None
            next_log = 0.0

            while True:
                frame = read()
                center, mask = detect_line_center(frame, args.threshold)
                left, right = wheel_speeds(center, frame.shape[1], args.speed)
                if drive is not None:
                    drive(left, right)

                now = monotonic()
                if now >= next_log:
                    position = "ligne perdue" if center is None else f"x={center:.1f}"
                    print(f"{position} | gauche={left:.0%} droite={right:.0%}", flush=True)
                    next_log = now + 0.5

                if args.preview:
                    cv2.imshow("Masque de la ligne", mask)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
