import cv2
import numpy as np


def filtro_sobel(imagem_cinza, fator=1):
    # Sobel calcula a variacao de intensidade (gradiente) em duas direcoes.
    # Usa kernels 3x3 com peso duplo no centro para dar mais precisao.
    #
    #   Kernel X (bordas verticais):   Kernel Y (bordas horizontais):
    #   [-1   0  +1]                   [-1  -2  -1]
    #   [-2   0  +2]                   [ 0   0   0]
    #   [-1   0  +1]                   [+1  +2  +1]
    #
    # Assim como no Prewitt, definimos os kernels manualmente e aplicamos
    # a convolucao sobre a imagem em ponto flutuante.
    kernel_horizontal = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    kernel_vertical = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64)

    imagem_float = imagem_cinza.astype(np.float64)

    # gradiente_horizontal: detecta bordas verticais (variacao da esquerda pra direita)
    gradiente_horizontal = cv2.filter2D(imagem_float, -1, kernel_horizontal)

    # gradiente_vertical: detecta bordas horizontais (variacao de cima pra baixo)
    gradiente_vertical = cv2.filter2D(imagem_float, -1, kernel_vertical)

    # A magnitude combina os dois gradientes: sqrt(gh^2 + gv^2)
    # Quanto maior a variacao entre pixels vizinhos, mais forte a borda.
    magnitude = np.sqrt(gradiente_horizontal**2 + gradiente_vertical**2)

    # Amplifica a magnitude por um fator fixo e corta em 255.
    # Diferente do NORM_MINMAX (que normaliza cada imagem individualmente),
    # isso preserva as diferencas naturais de intensidade entre os filtros.
    return np.clip(magnitude * fator, 0, 255).astype(np.uint8)


def filtro_prewitt(imagem_cinza, fator=1):
    # Prewitt funciona igual ao Sobel, mas com pesos uniformes (sem peso duplo).
    # E mais simples e mais sensivel a ruido.
    #
    #   Kernel X:        Kernel Y:
    #   [-1  0  +1]      [-1  -1  -1]
    #   [-1  0  +1]      [ 0   0   0]
    #   [-1  0  +1]      [+1  +1  +1]
    #
    # O kernel e uma matriz 3x3 que e deslizada sobre cada pixel da imagem.
    # Para cada pixel, multiplica os 8 vizinhos pelos valores do kernel e soma tudo.
    # Se os pixels vizinhos forem muito diferentes entre si, a soma sera alta e isso indica borda.
    # Se a regiao for uniforme (pixels iguais), a soma sera zero e nao ha borda.

    kernel_horizontal = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float64)
    kernel_vertical = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float64)

    # filter2D aplica a convolucao: desliza o kernel sobre cada pixel da imagem
    # e calcula a soma ponderada dos vizinhos.
    imagem_float = imagem_cinza.astype(np.float64)
    gradiente_horizontal = cv2.filter2D(imagem_float, -1, kernel_horizontal)
    gradiente_vertical = cv2.filter2D(imagem_float, -1, kernel_vertical)

    magnitude = np.sqrt(gradiente_horizontal**2 + gradiente_vertical**2)

    return np.clip(magnitude * fator, 0, 255).astype(np.uint8)


def filtro_laplaciano(imagem_cinza, fator=1):
    # Laplaciano usa a segunda derivada, ou seja, detecta onde a variacao
    # de intensidade muda de direcao e isso indica a presenca de uma borda.
    # Detecta bordas em todas as direcoes ao mesmo tempo.

    # Mascara classica 3x3 do Laplaciano (4-vizinhos).
    # Centro positivo e vizinhos negativos:
    #
    #   [ 0  -1   0]
    #   [-1   4  -1]
    #   [ 0  -1   0]
    #
    # Se o pixel central for muito diferente dos vizinhos, a resposta em modulo
    # sera alta, indicando borda. Em regioes uniformes, o resultado tende a zero.
    kernel_laplace = np.array([
        [0, -1, 0],
        [-1, 4, -1],
        [0, -1, 0]
    ], dtype=np.float64)

    imagem_float = imagem_cinza.astype(np.float64)
    resultado = cv2.filter2D(imagem_float, -1, kernel_laplace)

    # A segunda derivada pode gerar valores positivos ou negativos.
    # Para visualizar forca de borda, usamos o valor absoluto.
    resultado = np.abs(resultado)

    return np.clip(resultado * fator, 0, 255).astype(np.uint8)


def aplicar_filtro(imagem_original, nome_filtro, fator=1):
    # Todo filtro de borda trabalha em escala de cinza (1 canal).
    # A imagem colorida e convertida antes de qualquer processamento.
    imagem_cinza = cv2.cvtColor(imagem_original, cv2.COLOR_BGR2GRAY)

    if nome_filtro == "Sobel":
        return filtro_sobel(imagem_cinza, fator)
    elif nome_filtro == "Prewitt":
        return filtro_prewitt(imagem_cinza, fator)
    elif nome_filtro == "Laplaciano":
        return filtro_laplaciano(imagem_cinza, fator)

    # Se o filtro for "Cinza", retorna a imagem so convertida, sem bordas.
    return imagem_cinza
