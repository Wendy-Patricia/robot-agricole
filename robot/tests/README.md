# Ensaios manuais no robo

O programa `test_navigation.py` usa a camera real. Nao e um teste unitario.
Assume uma linha **preta num fundo claro**, camera virada para o chao,
imagem sem espelhamento, motor A a esquerda e motor B a direita.
Requer Python 3, OpenCV, NumPy e, com motores, RPi.GPIO no Raspberry Pi.

Executar a partir da pasta `robot`:

```bash
# Ver a detecao e ajustar a camera, sem ativar motores (ecra local):
python3 tests/test_navigation.py --display

# Seguir a linha com motores, incluindo curvas (funciona por SSH):
python3 tests/test_navigation.py --drive

# Motores e visualizacao, com ecra local:
python3 tests/test_navigation.py --drive --display
```

Parar com **Ctrl+C**, ou **Q / Esc** na janela. A perda da linha para os
motores; quando a linha reaparece, o seguimento retoma automaticamente.
Uma falha na camera ou no processamento termina o programa e liberta os GPIO.

## Ajustes no terreno

1. Comecar sem `--drive`. A mascara deve mostrar a linha em branco e o fundo
   em preto. Os pontos verdes devem acompanhar a linha da parte proxima
   ate a parte distante da imagem.
2. Ajustar `--threshold 80`: aumentar se a linha preta nao aparecer;
   diminuir se sombras e fundo forem confundidos com a linha.
   `--min-area 500` elimina manchas pequenas; reduzir se a linha for fina.
3. Ensaiar primeiro com as rodas levantadas: linha a direita deve produzir
   uma velocidade maior na roda esquerda; linha a esquerda, o inverso.
   Confirmar que ambas as rodas rodam para a frente.
4. Experimentar uma reta, curvas suaves e curvas mais apertadas a baixa
   velocidade. Por exemplo:

   ```bash
   python3 tests/test_navigation.py --drive --speed 24 --min-speed 14 --max-speed 45
   ```

5. Se corrigir pouco, aumentar `--kp`. Se oscilar, reduzir a velocidade e
   `--kp`; ajustar `--kd` gradualmente para amortecer as correcoes.
   `--min-speed` limita a velocidade de avanco nas curvas; a roda interior
   pode parar para apertar a curva. Os valores PWM dependem dos motores,
   bateria e aderencia e precisam de afinacao no robo.
6. Retirar a linha da imagem para verificar a paragem; voltar a coloca-la
   para verificar a retoma. Verificar tambem a paragem por Ctrl+C.

O detetor mede tres faixas da mesma linha, antecipa a direcao da curva e
reduz a velocidade quando a curva ou o desvio aumentam. Nao escolhe caminhos
em cruzamentos e nao procura a linha rodando quando ela sai da imagem.
Curvas que saiam do campo de visao exigem ajustar a camera e a velocidade.

Nao foram criados nem executados testes unitarios para esta alteracao.
