import cv2
import numpy as np


def filtro_sobel(imagem_cinza, fator=4):
    # Sobel calcula a variação de intensidade (gradiente) em duas direções.
    # Usa kernels 3x3 com peso duplo no centro para dar mais precisão.
    #
    #   Kernel X (bordas verticais):   Kernel Y (bordas horizontais):
    #   [-1   0  +1]                   [-1  -2  -1]
    #   [-2   0  +2]                   [ 0   0   0]
    #   [-1   0  +1]                   [+1  +2  +1]
    #
    # CV_64F usa ponto flutuante para não perder valores negativos no cálculo.

    # gradiente_horizontal: detecta bordas verticais (variação da esquerda pra direita)
    gradiente_horizontal = cv2.Sobel(imagem_cinza, cv2.CV_64F, 1, 0, ksize=3)

    # gradiente_vertical: detecta bordas horizontais (variação de cima pra baixo)
    gradiente_vertical = cv2.Sobel(imagem_cinza, cv2.CV_64F, 0, 1, ksize=3)

    # A magnitude combina os dois gradientes: sqrt(gh² + gv²)
    # Quanto maior a variação entre pixels vizinhos, mais forte a borda.
    magnitude = np.sqrt(gradiente_horizontal**2 + gradiente_vertical**2)

    # Amplifica a magnitude por um fator fixo e corta em 255.
    # Diferente do NORM_MINMAX (que normaliza cada imagem individualmente),
    # isso preserva as diferenças naturais de intensidade entre os filtros.
    return np.clip(magnitude * fator, 0, 255).astype(np.uint8)


def filtro_prewitt(imagem_cinza, fator=4):
    # Prewitt funciona igual ao Sobel, mas com pesos uniformes (sem peso duplo).
    # É mais simples e mais sensível a ruído.
    #
    #   Kernel X:        Kernel Y:
    #   [-1  0  +1]      [-1  -1  -1]
    #   [-1  0  +1]      [ 0   0   0]
    #   [-1  0  +1]      [+1  +1  +1]
    #
    # O kernel é uma matriz 3x3 que é deslizada sobre cada pixel da imagem.
    # Para cada pixel, multiplica os 8 vizinhos pelos valores do kernel e soma tudo.
    # Se os pixels vizinhos forem muito diferentes entre si, a soma será alta — isso indica borda.
    # Se a região for uniforme (pixels iguais), a soma será zero — sem borda.

    kernel_horizontal = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float64)
    kernel_vertical   = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float64)

    # filter2D aplica a convolução: desliza o kernel sobre cada pixel da imagem
    # e calcula a soma ponderada dos vizinhos.
    imagem_float      = imagem_cinza.astype(np.float64)
    gradiente_horizontal = cv2.filter2D(imagem_float, -1, kernel_horizontal)
    gradiente_vertical   = cv2.filter2D(imagem_float, -1, kernel_vertical)

    magnitude = np.sqrt(gradiente_horizontal**2 + gradiente_vertical**2)

    return np.clip(magnitude * fator, 0, 255).astype(np.uint8)


def filtro_laplaciano(imagem_cinza, fator=4):
    # Laplaciano usa a segunda derivada, ou seja, detecta onde a variação
    # de intensidade muda de direção — isso indica a presença de uma borda.
    # Detecta bordas em todas as direções ao mesmo tempo.

    # Antes de aplicar, suaviza a imagem com filtro Gaussiano para reduzir ruído,
    # pois o Laplaciano é muito sensível a variações pequenas.
    imagem_suavizada = cv2.GaussianBlur(imagem_cinza, (3, 3), sigmaX=1)

    # Aplica o Laplaciano. O resultado pode ter valores negativos,
    # por isso usa CV_64F e depois pega o valor absoluto.
    resultado = np.abs(cv2.Laplacian(imagem_suavizada, cv2.CV_64F, ksize=3))

    return np.clip(resultado * fator, 0, 255).astype(np.uint8)


def aplicar_filtro(imagem_original, nome_filtro, fator=4):
    # Todo filtro de borda trabalha em escala de cinza (1 canal).
    # A imagem colorida é convertida antes de qualquer processamento.
    imagem_cinza = cv2.cvtColor(imagem_original, cv2.COLOR_BGR2GRAY)

    if nome_filtro == "Sobel":
        return filtro_sobel(imagem_cinza, fator)
    elif nome_filtro == "Prewitt":
        return filtro_prewitt(imagem_cinza, fator)
    elif nome_filtro == "Laplaciano":
        return filtro_laplaciano(imagem_cinza, fator)

    # Se o filtro for "Cinza", retorna a imagem só convertida, sem bordas.
    return imagem_cinza
