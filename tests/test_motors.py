
import time
from navigation.motors import MotorController


def executar_testes():
    print("=" * 40)
    print("INICIANDO TESTES AUTOMÁTICOS DO ROBÔ")
    print("=" * 40)

    velocidade_teste = 90
    duracao = 2

    motor = None

    testes = [
        ("FRENTE", "forward"),
        ("TRÁS", "backward"),
        ("DIREITA", "turn_right"),
        ("ESQUERDA", "turn_left"),
    ]

    try:
        motor = MotorController()

        for indice, (nome, metodo) in enumerate(testes, start=1):
            print(
                f"\n[Teste {indice}/5] "
                f"A testar: {nome} a {velocidade_teste}%"
            )

            funcao = getattr(motor, metodo)

            # Executar movimento
            velocidade_esquerda, velocidade_direita = funcao(
                velocidade_teste
            )

            print(
                f"PWM comandado: "
                f"esquerdo={velocidade_esquerda}%, "
                f"direito={velocidade_direita}%"
            )

            # Manter o movimento durante 2 segundos
            time.sleep(duracao)

            # Parar usando o controlador
            motor.stop()
            print(f"Teste {indice} concluído.")

            # Pausa antes do movimento seguinte
            time.sleep(1)

        print("\n[Teste 5/5] A testar: PARAGEM")

        motor.stop()
        time.sleep(1)

        print("Teste de paragem concluído.")

        print("\n" + "=" * 40)
        print("TODOS OS TESTES FORAM EXECUTADOS")
        print("=" * 40)

    except KeyboardInterrupt:
        print("\nTestes interrompidos pelo utilizador.")

    except Exception as erro:
        print(f"\nErro durante os testes: {erro}")
        raise

    finally:
        if motor is not None:
            motor.cleanup()

        print("Sistema limpo e desligado.")


if __name__ == "__main__":
    executar_testes()

