"""Componentes reutilizáveis da camada de view."""
import customtkinter as ctk
from tkinter import ttk

from view import theme


class DataTable(ctk.CTkFrame):
    """Tabela (ttk.Treeview) estilizada com rolagem, embutida num CTkFrame."""

    def __init__(self, master, colunas, on_select=None, **kwargs):
        super().__init__(master, fg_color=theme.COR_CARD, corner_radius=10, **kwargs)
        self.colunas = colunas  # list[(key, label, width)]
        self.on_select = on_select

        ids = [c[0] for c in colunas]
        self.tree = ttk.Treeview(
            self, columns=ids, show="headings", style="Conc.Treeview", selectmode="browse"
        )
        for key, label, largura in colunas:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=largura, anchor="w", stretch=True)

        vsb = ctk.CTkScrollbar(
            self, orientation="vertical", command=self.tree.yview,
            fg_color="transparent", button_color=theme.COR_SCROLL,
            button_hover_color=theme.COR_SCROLL_HOVER,
        )
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        vsb.grid(row=0, column=1, sticky="ns", pady=8, padx=(0, 8))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._dados = {}  # iid -> dict da linha
        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar)

    def carregar(self, linhas):
        """Substitui o conteúdo da tabela por ``linhas`` (list[dict])."""
        self.tree.delete(*self.tree.get_children())
        self._dados.clear()
        for linha in linhas:
            valores = [self._fmt(linha.get(c[0])) for c in self.colunas]
            iid = self.tree.insert("", "end", values=valores)
            self._dados[iid] = linha

    @staticmethod
    def _fmt(valor):
        if valor is None:
            return "—"
        if isinstance(valor, float):
            return f"{valor:.2f}"
        return str(valor)

    def linha_selecionada(self):
        sel = self.tree.selection()
        return self._dados.get(sel[0]) if sel else None

    def limpar_selecao(self):
        for iid in self.tree.selection():
            self.tree.selection_remove(iid)

    def _ao_selecionar(self, _evento):
        if self.on_select:
            self.on_select(self.linha_selecionada())


class StatCard(ctk.CTkFrame):
    """Cartão de indicador (ícone + rótulo + valor) usado no dashboard."""

    def __init__(self, master, titulo, valor="—", cor=theme.COR_PRIMARIA, icone="", **kwargs):
        super().__init__(master, fg_color=theme.COR_CARD, corner_radius=14, **kwargs)
        self.configure(border_width=1, border_color=theme.COR_BORDA)
        barra = ctk.CTkFrame(self, fg_color=cor, corner_radius=6, width=5)
        barra.pack(side="left", fill="y", padx=(8, 0), pady=14)

        corpo = ctk.CTkFrame(self, fg_color="transparent")
        corpo.pack(side="left", fill="both", expand=True, padx=13, pady=14)

        topo = ctk.CTkFrame(corpo, fg_color="transparent")
        topo.pack(anchor="w", fill="x")
        if icone:
            ctk.CTkLabel(topo, text=icone, text_color=cor,
                         font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(topo, text=titulo.upper(), text_color=theme.COR_TEXTO_FRACO,
                     font=ctk.CTkFont(size=11, weight="bold"), anchor="w").pack(side="left")

        self.lbl_valor = ctk.CTkLabel(
            corpo, text=str(valor), font=ctk.CTkFont(size=22, weight="bold"), anchor="w",
        )
        self.lbl_valor.pack(anchor="w", pady=(2, 0))

    def set_valor(self, valor):
        self.lbl_valor.configure(text=str(valor))
