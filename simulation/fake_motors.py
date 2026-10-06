class FakeMotorController:

    def forward(self, speed):
        print(f"[MOTEURS] Avancer - vitesse: {speed}")

    def backward(self, speed):
        print(f"[MOTEURS] Reculer - vitesse: {speed}")

    def turn_left(self, speed):
        print(f"[MOTEURS] Tourner à gauche - vitesse: {speed}")

    def turn_right(self, speed):
        print(f"[MOTEURS] Tourner à droite - vitesse: {speed}")

    def stop(self):
        print("[MOTEURS] Stop")