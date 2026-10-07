import sys
import termios
import tty
import time
from navigation.motors import MotorController

def get_key():
    """Captura uma única tecla do teclado instantaneamente (sem precisar de Enter)."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    motor = MotorController()
    
    velocidade = 50  # Velocidade padrão (0 a 100)
    
    # Variáveis para guardar os PWMs ativos no momento
    pwm_left = None
    pwm_right = None

    def limpar_pwms():
        nonlocal pwm_left, pwm_right
        if pwm_left:
            try: pwm_left.stop()
            except: pass
        if pwm_right:
            try: pwm_right.stop()
            except: pass
        pwm_left, pwm_right = None, None

    print("\n" + "="*40)
    print("CONTROLE MANUAL DO ROBÔ VIA TECLADO")
    print("="*40)
    print("  [1] -> Ir para FRENTE")
    print("  [2] -> Ir para TRÁS")
    print("  [3] -> Virar à ESQUERDA")
    print("  [4] -> Virar à DIREITA")
    print("  [0] -> PARAR")
    print("  [q] -> SAIR")
    print(f"Velocidade atual: {velocidade}%")
    print("="*40)
    print("Pressione uma tecla...")

    try:
        while True:
            tecla = get_key()

            if tecla == '1':
                limpar_pwms()
                pwm_left, pwm_right = motor.forward(velocidade)
                print(f"\r[COMANDO] FRENTE (Vel: {velocidade}%)     ", end="", flush=True)

            elif tecla == '2':
                limpar_pwms()
                pwm_left, pwm_right = motor.backward(velocidade)
                print(f"\r[COMANDO] TRÁS (Vel: {velocidade}%)       ", end="", flush=True)

            elif tecla == '3':
                limpar_pwms()
                pwm_left, pwm_right = motor.turn_left(velocidade)
                print(f"\r[COMANDO] ESQUERDA (Vel: {velocidade}%) ", end="", flush=True)

            elif tecla == '4':
                limpar_pwms()
                pwm_left, pwm_right = motor.turn_right(velocidade)
                print(f"\r[COMANDO] DIREITA (Vel: {velocidade}%)  ", end="", flush=True)

            elif tecla == '0':
                limpar_pwms()
                motor.stop()
                print(f"\r[COMANDO] PARADO                      ", end="", flush=True)

            elif tecla == 'q' or tecla == 'Q':
                print("\nSaindo do programa...")
                break

    except KeyboardInterrupt:
        print("\nInterrompido pelo utilizador.")

    finally:
        limpar_pwms()
        motor.cleanup()
        print("Programa encerrado com segurança.")

if __name__ == "__main__":
    main()