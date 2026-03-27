import tkinter as tk
from tkinter import filedialog, messagebox

import cv2
from PIL import Image, ImageTk

from filtros import aplicar_filtro

BG = "#0c0c14"
PANEL = "#13131f"
CARD = "#1a1a2e"
BORDER = "#252542"
ACCENT = "#818cf8"
SUCCESS = "#34d399"
TEXT = "#e2e8f0"
MUTED = "#4b5563"


class JanelaPrincipal:
    FILTROS = ["Cinza", "Sobel", "Prewitt", "Laplaciano"]

    def __init__(self, janela_raiz):
        self.janela = janela_raiz
        self.janela.title("PixelEdge")
        self.janela.configure(bg=BG)
        self.janela.minsize(1100, 680)

        self.imagem_original = None
        self.imagem_resultado = None
        self.foto_original = None
        self.foto_resultado = None
        self.filtro_selecionado = tk.StringVar(value="Cinza")
        self.fator_amplificacao = tk.DoubleVar(value=1.0)
        self._botoes_filtro = {}
        self._redesenho_agendado = None

        self._criar_cabecalho()
        self._criar_area_principal()
        self._criar_barra_status()

    def _criar_cabecalho(self):
        header = tk.Frame(self.janela, bg=PANEL)
        header.pack(fill="x")

        tk.Frame(header, bg=ACCENT, height=3).pack(fill="x")

        inner = tk.Frame(header, bg=PANEL, pady=16)
        inner.pack(fill="x")

        logo = tk.Frame(inner, bg=PANEL)
        logo.pack(side="left", padx=24)
        tk.Label(logo, text="Pixel", font=("Segoe UI", 22, "bold"), fg=TEXT, bg=PANEL).pack(side="left")
        tk.Label(logo, text="Edge", font=("Segoe UI", 22, "bold"), fg=ACCENT, bg=PANEL).pack(side="left")

    def _criar_area_principal(self):
        area = tk.Frame(self.janela, bg=BG)
        area.pack(fill="both", expand=True, padx=20, pady=16)

        painel_esq = tk.Frame(area, bg=PANEL, width=230, highlightthickness=1, highlightbackground=BORDER)
        painel_esq.pack(side="left", fill="y", padx=(0, 16))
        painel_esq.pack_propagate(False)
        self._criar_controles(painel_esq)

        painel_dir = tk.Frame(area, bg=BG)
        painel_dir.pack(side="left", fill="both", expand=True)
        self._criar_area_imagens(painel_dir)

    def _criar_controles(self, painel):
        tk.Label(painel, text="IMAGEM", font=("Segoe UI", 8, "bold"), fg=MUTED, bg=PANEL).pack(
            anchor="w", padx=20, pady=(20, 6)
        )

        tk.Button(
            painel,
            text="  Abrir Imagem",
            command=self.acao_abrir_imagem,
            bg=ACCENT,
            fg="#ffffff",
            font=("Segoe UI", 10, "bold"),
            activebackground="#6366f1",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            pady=10,
            anchor="w",
            padx=14,
        ).pack(fill="x", padx=16)

        tk.Frame(painel, bg=BORDER, height=1).pack(fill="x", padx=16, pady=20)

        tk.Label(painel, text="FILTRO", font=("Segoe UI", 8, "bold"), fg=MUTED, bg=PANEL).pack(
            anchor="w", padx=20, pady=(0, 8)
        )

        for nome in self.FILTROS:
            self._criar_botao_filtro(painel, nome)

        tk.Frame(painel, bg=BORDER, height=1).pack(fill="x", padx=16, pady=20)

        tk.Label(painel, text="AMPLIFICACAO", font=("Segoe UI", 8, "bold"), fg=MUTED, bg=PANEL).pack(
            anchor="w", padx=20, pady=(0, 4)
        )

        self._label_fator = tk.Label(painel, text="Fator: 1.0", font=("Segoe UI", 9), fg=TEXT, bg=PANEL)
        self._label_fator.pack(anchor="w", padx=20)

        tk.Scale(
            painel,
            variable=self.fator_amplificacao,
            from_=1.0,
            to=20.0,
            resolution=0.5,
            orient="horizontal",
            bg=PANEL,
            fg=TEXT,
            troughcolor=BORDER,
            highlightthickness=0,
            bd=0,
            activebackground=ACCENT,
            sliderrelief="flat",
            command=self._ao_mover_slider,
        ).pack(fill="x", padx=16)

        tk.Frame(painel, bg=BORDER, height=1).pack(fill="x", padx=16, pady=20)

        tk.Button(
            painel,
            text="  Salvar Resultado",
            command=self.acao_salvar_resultado,
            bg=SUCCESS,
            fg="#0a0a14",
            font=("Segoe UI", 10, "bold"),
            activebackground="#10b981",
            activeforeground="#0a0a14",
            relief="flat",
            cursor="hand2",
            pady=10,
            anchor="w",
            padx=14,
        ).pack(fill="x", padx=16)

    def _criar_botao_filtro(self, painel, nome):
        frame = tk.Frame(painel, bg=PANEL, cursor="hand2")
        frame.pack(fill="x", padx=16, pady=2)

        indicador = tk.Frame(frame, bg=PANEL, width=4)
        indicador.pack(side="left", fill="y")

        label = tk.Label(frame, text=nome, font=("Segoe UI", 10), fg=TEXT, bg=PANEL, pady=9, padx=12, anchor="w")
        label.pack(side="left", fill="x", expand=True)

        self._botoes_filtro[nome] = (frame, indicador, label)

        def selecionar(n=nome):
            self.filtro_selecionado.set(n)
            self._atualizar_selecao_filtros()
            self.acao_aplicar_filtro()

        for widget in (frame, indicador, label):
            widget.bind("<Button-1>", lambda e, n=nome: selecionar(n))

        self._atualizar_selecao_filtros()

    def _atualizar_selecao_filtros(self):
        atual = self.filtro_selecionado.get()
        for nome, (frame, indicador, label) in self._botoes_filtro.items():
            if nome == atual:
                frame.configure(bg=CARD)
                indicador.configure(bg=ACCENT)
                label.configure(bg=CARD, fg=ACCENT, font=("Segoe UI", 10, "bold"))
            else:
                frame.configure(bg=PANEL)
                indicador.configure(bg=PANEL)
                label.configure(bg=PANEL, fg=TEXT, font=("Segoe UI", 10))

    def _criar_area_imagens(self, painel):
        titulos = tk.Frame(painel, bg=BG)
        titulos.pack(fill="x", pady=(0, 10))
        tk.Label(titulos, text="ORIGINAL", font=("Segoe UI", 8, "bold"), fg=MUTED, bg=BG).pack(
            side="left", expand=True
        )
        tk.Label(titulos, text="RESULTADO", font=("Segoe UI", 8, "bold"), fg=MUTED, bg=BG).pack(
            side="left", expand=True
        )

        frame_canvas = tk.Frame(painel, bg=BG)
        frame_canvas.pack(fill="both", expand=True)

        self.canvas_original = tk.Canvas(frame_canvas, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        self.canvas_original.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.canvas_resultado = tk.Canvas(frame_canvas, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        self.canvas_resultado.pack(side="left", fill="both", expand=True, padx=(8, 0))

        self.canvas_original.bind("<Configure>", self._ao_redimensionar_canvas)
        self.canvas_resultado.bind("<Configure>", self._ao_redimensionar_canvas)

        self._mensagem_canvas(self.canvas_original, "Abra uma imagem\npara comecar")
        self._mensagem_canvas(self.canvas_resultado, "O resultado\naparece aqui")

    def _criar_barra_status(self):
        barra = tk.Frame(self.janela, bg=PANEL)
        barra.pack(fill="x", side="bottom")
        tk.Frame(barra, bg=BORDER, height=1).pack(fill="x")
        self.texto_status = tk.StringVar(value="  Pronto.")
        tk.Label(barra, textvariable=self.texto_status, font=("Segoe UI", 9), fg=MUTED, bg=PANEL, anchor="w").pack(
            padx=20, pady=8, fill="x"
        )

    def acao_abrir_imagem(self):
        caminho = filedialog.askopenfilename(
            title="Escolha uma imagem",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return

        img = cv2.imread(caminho)
        if img is None:
            messagebox.showerror("Erro", "Nao foi possivel abrir essa imagem.")
            return

        self.imagem_original = img
        self._exibir_no_canvas(self.canvas_original, img, colorida=True)
        self.acao_aplicar_filtro()
        nome = caminho.split("/")[-1].split("\\")[-1]
        h, w = img.shape[:2]
        self.texto_status.set(f"  {nome}  -  {w} x {h} px")

    def _ao_mover_slider(self, valor):
        self._label_fator.configure(text=f"Fator: {float(valor):.1f}")
        self.acao_aplicar_filtro()

    def acao_aplicar_filtro(self):
        if self.imagem_original is None:
            return

        self.imagem_resultado = aplicar_filtro(
            self.imagem_original,
            self.filtro_selecionado.get(),
            fator=self.fator_amplificacao.get(),
        )
        self._exibir_no_canvas(self.canvas_resultado, self.imagem_resultado, colorida=False)

    def acao_salvar_resultado(self):
        if self.imagem_resultado is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro.")
            return

        caminho = filedialog.asksaveasfilename(
            title="Salvar resultado",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")],
        )
        if not caminho:
            return

        cv2.imwrite(caminho, self.imagem_resultado)
        messagebox.showinfo("Salvo!", f"Imagem salva em:\n{caminho}")

    def _ao_redimensionar_canvas(self, event):
        if self._redesenho_agendado is not None:
            self.janela.after_cancel(self._redesenho_agendado)
        self._redesenho_agendado = self.janela.after(60, self._redesenhar_imagens)

    def _redesenhar_imagens(self):
        self._redesenho_agendado = None

        if self.imagem_original is not None:
            self._exibir_no_canvas(self.canvas_original, self.imagem_original, colorida=True)
        else:
            self._mensagem_canvas(self.canvas_original, "Abra uma imagem\npara comecar")

        if self.imagem_resultado is not None:
            self._exibir_no_canvas(self.canvas_resultado, self.imagem_resultado, colorida=False)
        else:
            self._mensagem_canvas(self.canvas_resultado, "O resultado\naparece aqui")

    def _exibir_no_canvas(self, canvas, imagem, colorida):
        canvas.update_idletasks()
        cw = canvas.winfo_width() or 450
        ch = canvas.winfo_height() or 450
        ih, iw = imagem.shape[:2]
        escala = min(cw / iw, ch / ih, 1.0)
        imagem_redim = cv2.resize(imagem, (int(iw * escala), int(ih * escala)), interpolation=cv2.INTER_AREA)

        if colorida:
            pil = Image.fromarray(cv2.cvtColor(imagem_redim, cv2.COLOR_BGR2RGB))
        else:
            pil = Image.fromarray(imagem_redim)

        foto = ImageTk.PhotoImage(pil)
        canvas.delete("all")
        canvas.create_image(cw // 2, ch // 2, anchor="center", image=foto)
        if colorida:
            self.foto_original = foto
        else:
            self.foto_resultado = foto

    def _mensagem_canvas(self, canvas, mensagem):
        canvas.update_idletasks()
        w = canvas.winfo_width() or 450
        h = canvas.winfo_height() or 450
        canvas.delete("all")
        canvas.create_text(w // 2, h // 2, text=mensagem, fill=MUTED, font=("Segoe UI", 13), justify="center")


if __name__ == "__main__":
    janela_raiz = tk.Tk()
    JanelaPrincipal(janela_raiz)
    janela_raiz.mainloop()
