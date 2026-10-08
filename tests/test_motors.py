import time
from navigation.motors import MotorController

def executar_testes():
    print("="*40)
    print("TESTE MANUAL DOS MOTORES")
    print("="*40)

    confirmacao = input(
        "Confirma que o robô está seguro e com as rodas suspensas? (SIM): "
    )
    if confirmacao.strip().upper() != "SIM":
        print("Teste cancelado.")
        return

    motor = MotorController()
    velocidade_teste = 90  # Velocidade padrão a 90%

    try:
        # 1. Testar FRENTE (forward)
        print("\n[Teste 1/5] A testar: FRENTE (forward) a 90%")
        motor.forward(velocidade_teste)
        time.sleep(3)  # Mantém por 3 segundos
        motor.stop()
        time.sleep(1)   

        # 2. Testar TRÁS (backward)
        print("\n[Teste 2/5] A testar: TRÁS (backward) a 90%")
        motor.backward(90)
        time.sleep(3)
        motor.stop()
        time.sleep(1)

        # 3. Testar VIRAR À DIREITA (turn_right)
        print("\n[Teste 3/5] A testar: DIREITA (turn_right) a 90%")
        motor.turn_right(velocidade_teste)
        time.sleep(2)  # Mantém por 2 segundos
        motor.stop()
        time.sleep(1)

        # 4. Testar VIRAR À ESQUERDA (turn_left)
        print("\n[Teste 4/5] A testar: ESQUERDA (turn_left) a 90%")
        motor.turn_left(velocidade_teste)
        time.sleep(2)
        motor.stop()
        time.sleep(1)

        # 5. Testar PARAGEM E DESATIVAÇÃO (stop / disable)
        print("\n[Teste 5/5] A testar: PARAGEM TOTAL E DESATIVAÇÃO")
        motor.stop()
        time.sleep(1)
        
        print("\n O teste manual dos motores foi concluído com sucesso!")

    except KeyboardInterrupt:
        print("\n[AVISO] Teste interrompido manualmente pelo utilizador.")

    finally:
        # Limpa todos os pinos GPIO de forma segura
        motor.cleanup()
        print(" Sistema limpo e desligado.")

if __name__ == "__main__":
    executar_testes()