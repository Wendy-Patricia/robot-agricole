import time
from robot.navigation.motors import MotorController


def executar_testes():
    print("=" * 40)
    print("DÉMARRAGE DES TESTS AUTOMATIQUES DU ROBOT")
    print("=" * 40)

    velocidade_teste = 40
    duracao = 2

    motor = None

    testes = [
        ("AVANT", "forward"),
        ("ARRIÈRE", "backward"),
        ("DROITE", "turn_right"),
        ("GAUCHE", "turn_left"),
    ]

    try:
        motor = MotorController()

        for indice, (nome, metodo) in enumerate(testes, start=1):
            print(
                f"\n[Test {indice}/5] "
                f"Test en cours : {nome} à {velocidade_teste}%"
            )

            funcao = getattr(motor, metodo)

            # Exécuter le mouvement
            velocidade_esquerda, velocidade_direita = funcao(
                velocidade_teste
            )

            print(
                f"PWM commandé : "
                f"gauche={velocidade_esquerda}%, "
                f"droit={velocidade_direita}%"
            )

            # Maintenir le mouvement pendant 2 secondes
            time.sleep(duracao)

            # Arrêter à l'aide du contrôleur
            motor.stop()
            print(f"Test {indice} terminé.")

            # Pause avant le mouvement suivant
            time.sleep(1)

        print("\n[Test 5/5] Test en cours : ARRÊT")

        motor.stop()
        time.sleep(1)

        print("Test d'arrêt terminé.")

        print("\n" + "=" * 40)
        print("TOUS LES TESTS ONT ÉTÉ EXÉCUTÉS")
        print("=" * 40)

    except KeyboardInterrupt:
        print("\nTests interrompus par l'utilisateur.")

    except Exception as erro:
        print(f"\nErreur pendant les tests : {erro}")
        raise

    finally:
        if motor is not None:
            motor.cleanup()

        print("Système nettoyé et désactivé.")


if __name__ == "__main__":
    executar_testes()