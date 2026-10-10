from navigation.interfaces import MotorDriver


class FakeMotorController(MotorDriver):
    def __init__(self):
        self.commands = []

    def forward(self, speed: float) -> None:
        self.commands.append(("forward", speed))

    def turn_left(self, speed: float) -> None:
        self.commands.append(("turn_left", speed))

    def turn_right(self, speed: float) -> None:
        self.commands.append(("turn_right", speed))

    def stop(self) -> None:
        self.commands.append(("stop", None))