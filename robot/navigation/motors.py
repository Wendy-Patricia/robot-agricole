from contextlib import ExitStack, contextmanager


@contextmanager
def open_motors():
    from gpiozero import DigitalOutputDevice, Motor
    from gpiozero.pins.lgpio import LGPIOFactory

    with ExitStack() as resources:
        factory = LGPIOFactory()
        resources.callback(factory.close)
        enable = resources.enter_context(
            DigitalOutputDevice(17, initial_value=False, pin_factory=factory)
        )
        left = resources.enter_context(
            Motor(forward=22, backward=23, pin_factory=factory)
        )
        right = resources.enter_context(
            Motor(forward=27, backward=18, pin_factory=factory)
        )

        def drive(left_speed, right_speed):
            left.forward(left_speed)
            right.forward(right_speed)

        enable.on()
        try:
            yield drive
        finally:
            enable.off()
