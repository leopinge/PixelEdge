# PixelEdge

Aplicação desktop de processamento de imagens com interface gráfica, desenvolvida em Python.

## Sobre

PixelEdge permite carregar uma imagem e aplicar filtros de detecção de bordas em tempo real, exibindo o resultado lado a lado com a imagem original. Foi desenvolvido como projeto prático para a matéria de **Processamento de Imagens**.

## Filtros disponíveis

| Filtro | Descrição |
|---|---|
| **Cinza** | Converte a imagem para escala de cinza |
| **Sobel** | Detecta bordas usando gradiente com kernels 3×3 ponderados |
| **Prewitt** | Detecta bordas com kernels uniformes, mais simples que o Sobel |
| **Laplaciano** | Detecta bordas via segunda derivada, sensível a todas as direções |

Todos os filtros de borda operam em escala de cinza e permitem ajustar um **fator de amplificação** (1× a 20×) para controlar a intensidade do resultado.

## Tecnologias

- **Python 3**
- **Tkinter** — interface gráfica
- **OpenCV** — processamento de imagem
- **Pillow** — exibição das imagens na interface
- **NumPy** — operações matriciais nos kernels

## Como executar

1. Instale as dependências:
   ```bash
   pip install opencv-python pillow numpy
   ```

2. Execute a aplicação:
   ```bash
   python pixeledge.py
   ```

## Estrutura

```
PixelEdge/
├── pixeledge.py   # Interface gráfica (Tkinter)
├── filtros.py     # Implementação dos filtros de borda
└── imagens/       # Imagens de exemplo
```
