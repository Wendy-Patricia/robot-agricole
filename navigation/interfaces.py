from typing import Protocol


class MotorDriver(Protocol):
    def forward(self, speed: float) -> None:
        ...

    def turn_left(self, speed: float) -> None:
        ...

    def turn_right(self, speed: float) -> None:
        ...

    def stop(self) -> None:
        ...


class LineDetectorProtocol(Protocol):
    def detect(self, frame: object) -> tuple[float | None, object]:
        ...