import time
from navigation.motors import MotorController

def main():
    print("A iniciar o teste do MotorController...")
    motor = MotorController()

    try:
        # 1. Teste para a FRENTE (velocidade 50%)
        print("\n--- Teste: FRENTE ---")
        pwm_a, pwm_b = motor.forward(90)
        time.sleep(3)
        pwm_a.stop()
        pwm_b.stop()
        motor.stop()
        time.sleep(1)

        # 2. Teste para TRÁS (velocidade 40%)
        print("\n--- Teste: TRÁS ---")
        pwm_a, pwm_b = motor.backward(90)
        time.sleep(3)
        pwm_a.stop()
        pwm_b.stop()
        motor.stop()
        time.sleep(1)

        # 3. Teste: Virar à DIREITA
        print("\n--- Teste: Virar à DIREITA ---")
        pwm_l, pwm_r = motor.turn_right(90)
        time.sleep(2)
        pwm_l.stop()
        pwm_r.stop()
        motor.stop()
        time.sleep(1)

        # 4. Teste: Virar à ESQUERDA
        print("\n--- Teste: Virar à ESQUERDA ---")
        pwm_l, pwm_r = motor.turn_left(90)
        time.sleep(2)
        pwm_l.stop()
        pwm_r.stop()
        motor.stop()

        print("\n--- Teste Concluído com Sucesso! ---")

    except KeyboardInterrupt:
        print("\nTeste interrompido manualmente pelo utilizador.")

    finally:
        # Limpa os pinos GPIO e desativa o driver com segurança
        motor.cleanup()

if __name__ == "__main__":
    main()