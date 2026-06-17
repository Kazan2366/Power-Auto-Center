"""Gráficos leves desenhados em ``tkinter.Canvas`` (sem dependências externas).

Combinam com o tema escuro e redesenham ao redimensionar. Cada gráfico fica
dentro de um cartão (CTkFrame) com título.
"""
import tkinter as tk

import customtkinter as ctk

from view import theme

# Paleta de séries (cores agradáveis e contrastantes)
PALETA = ["#2563eb", "#16a34a", "#ea580c", "#7c3aed", "#0891b2", "#dc2626", "#ca8a04"]


def fmt_num(valor):
    """Formata número: inteiro quando exato (3.0 → '3'), senão 1 casa."""
    valor = float(valor)
    return str(int(round(valor))) if abs(valor - round(valor)) < 1e-9 else f"{valor:.1f}"


class _CartaoGrafico(ctk.CTkFrame):
    """Base: cartão com título + área de canvas que redesenha ao redimensionar."""

    def __init__(self, master, titulo, altura=240, **kwargs):
        super().__init__(master, fg_color=theme.COR_CARD, corner_radius=14,
                         border_width=1, border_color=theme.COR_BORDA, **kwargs)
        ctk.CTkLabel(self, text=titulo, font=theme.fonte_subtitulo(), anchor="w").pack(
            anchor="w", padx=16, pady=(12, 4))
        self.canvas = tk.Canvas(self, bg=theme.COR_CARD, highlightthickness=0, height=altura)
        self.canvas.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self._dados = []
        self.canvas.bind("<Configure>", lambda _e: self._desenhar())

    def set_data(self, dados):
        """dados: list[(rótulo, valor, cor?)] — cor opcional (usa a paleta)."""
        normal = []
        for i, item in enumerate(dados):
            rotulo, valor = item[0], item[1]
            cor = item[2] if len(item) > 2 else PALETA[i % len(PALETA)]
            normal.append((rotulo, float(valor or 0), cor))
        self._dados = normal
        self._desenhar()

    def _vazio(self, w, h):
        self.canvas.create_text(w / 2, h / 2, text="Sem dados", fill=theme.COR_TEXTO_FRACO,
                                font=("Segoe UI", 12))

    def _desenhar(self):  # pragma: no cover - implementado nas subclasses
        raise NotImplementedError


class DonutChart(_CartaoGrafico):
    """Gráfico de rosca com legenda lateral e total ao centro."""

    def __init__(self, master, titulo, fmt=fmt_num, **kwargs):
        self._fmt = fmt
        super().__init__(master, titulo, **kwargs)

    def _desenhar(self):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width() or 360
        h = c.winfo_height() or 220
        total = sum(v for _r, v, _c in self._dados)
        # área do donut (esquerda) e legenda (direita)
        tam = min(h, w * 0.55) - 16
        cx, cy = 16 + tam / 2, h / 2
        x0, y0, x1, y1 = cx - tam / 2, cy - tam / 2, cx + tam / 2, cy + tam / 2

        if total <= 0:
            c.create_oval(x0, y0, x1, y1, outline=theme.COR_BORDA, width=2)
            self._vazio(w, h)
            return

        nao_zero = [(r, v, cor) for r, v, cor in self._dados if v > 0]
        if len(nao_zero) == 1:
            # segmento único (100%): create_arc com 360° não renderiza → usa oval
            c.create_oval(x0, y0, x1, y1, fill=nao_zero[0][2], outline=theme.COR_CARD, width=2)
        else:
            inicio = 90.0
            for _rotulo, valor, cor in self._dados:
                extensao = -360.0 * valor / total
                if valor > 0:
                    c.create_arc(x0, y0, x1, y1, start=inicio, extent=extensao,
                                 fill=cor, outline=theme.COR_CARD, width=2, style="pieslice")
                inicio += extensao
        # furo central → donut
        furo = tam * 0.55
        c.create_oval(cx - furo / 2, cy - furo / 2, cx + furo / 2, cy + furo / 2,
                      fill=theme.COR_CARD, outline=theme.COR_CARD)
        c.create_text(cx, cy - 8, text=self._fmt(total), fill=theme.COR_TEXTO,
                      font=("Segoe UI", 15, "bold"))
        c.create_text(cx, cy + 12, text="Total", fill=theme.COR_TEXTO_FRACO,
                      font=("Segoe UI", 9))

        # legenda (rótulo + %; valor absoluto abaixo, em fonte menor)
        lx = x1 + 24
        ly = cy - (len(self._dados) * 30) / 2
        for rotulo, valor, cor in self._dados:
            pct = 100 * valor / total
            c.create_rectangle(lx, ly + 2, lx + 12, ly + 14, fill=cor, outline=cor)
            c.create_text(lx + 20, ly + 8, anchor="w", fill=theme.COR_TEXTO,
                          font=("Segoe UI", 10, "bold"), text=f"{rotulo}  {pct:.0f}%")
            c.create_text(lx + 20, ly + 22, anchor="w", fill=theme.COR_TEXTO_FRACO,
                          font=("Segoe UI", 9), text=self._fmt(valor))
            ly += 32


class BarChart(_CartaoGrafico):
    """Gráfico de barras verticais com rótulo de valor sobre cada barra."""

    def __init__(self, master, titulo, fmt=fmt_num, **kwargs):
        self._fmt = fmt
        super().__init__(master, titulo, **kwargs)

    def _desenhar(self):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width() or 360
        h = c.winfo_height() or 220
        if not self._dados or all(v == 0 for _r, v, _c in self._dados):
            self._vazio(w, h)
            return

        margem_b, margem_t, margem_l, margem_r = 34, 26, 12, 12
        area_h = h - margem_b - margem_t
        area_w = w - margem_l - margem_r
        n = len(self._dados)
        maximo = max(v for _r, v, _c in self._dados) or 1
        slot = area_w / n
        largura = min(slot * 0.55, 70)

        # linha de base
        base_y = h - margem_b
        c.create_line(margem_l, base_y, w - margem_r, base_y, fill=theme.COR_BORDA)

        for i, (rotulo, valor, cor) in enumerate(self._dados):
            cx = margem_l + slot * i + slot / 2
            altura = (valor / maximo) * area_h
            x0, x1 = cx - largura / 2, cx + largura / 2
            y0 = base_y - altura
            c.create_rectangle(x0, y0, x1, base_y, fill=cor, outline=cor)
            c.create_text(cx, y0 - 10, text=self._fmt(valor), fill=theme.COR_TEXTO,
                          font=("Segoe UI", 10, "bold"))
            texto = rotulo if len(rotulo) <= 12 else rotulo[:11] + "…"
            c.create_text(cx, base_y + 14, text=texto, fill=theme.COR_TEXTO_FRACO,
                          font=("Segoe UI", 9))
