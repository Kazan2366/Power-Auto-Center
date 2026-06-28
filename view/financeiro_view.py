"""Financeiro — resumo e movimentos (``backend.financeiro``)."""
from tkinter import messagebox

import customtkinter as ctk

from view import theme
from view.widgets import StatCard, DataTable
from utils.helpers import format_currency

_RESUMO = [
    ("receita_vendas", "Receita de vendas", theme.COR_SUCESSO),
    ("receita_servicos", "Receita de serviços", theme.COR_SUCESSO),
    ("receita_total", "Receita total", theme.COR_PRIMARIA),
    ("despesa_salarios", "Despesa com salários", theme.COR_PERIGO),
    ("saldo", "Saldo", theme.COR_ROXO),
]


class FinanceiroView(ctk.CTkFrame):
    def __init__(self, master, backend, role=None):
        super().__init__(master, fg_color="transparent")
        self.backend = backend
        self.role = (role or "").lower()

        # Perfil de vendas não enxerga a despesa com salários.
        resumo_itens = [
            item for item in _RESUMO
            if not (self.role == "vendas" and item[0] == "despesa_salarios")
        ]

        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(topo, text="Financeiro", font=theme.fonte_titulo()).pack(side="left")
        ctk.CTkButton(topo, text="↻ Atualizar", width=110, fg_color=theme.COR_PAINEL,
                      hover_color=theme.COR_CARD, command=self.recarregar).pack(side="right")

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", pady=(0, 12))
        self._cards = {}
        for i, (chave, rotulo, cor) in enumerate(resumo_itens):
            card = StatCard(cards, rotulo, "—", cor=cor)
            card.grid(row=0, column=i, padx=6, sticky="ew")
            cards.grid_columnconfigure(i, weight=1)
            self._cards[chave] = card

        ctk.CTkLabel(self, text="Movimentos", font=theme.fonte_subtitulo(), anchor="w").pack(
            fill="x", pady=(4, 6))
        self.tabela = DataTable(self, [
            ("data", "Data", 150), ("origem", "Origem", 130), ("tipo", "Tipo", 100),
            ("descricao", "Descrição", 300), ("valor", "Valor", 120),
        ])
        self.tabela.pack(fill="both", expand=True)

        self.recarregar()

    def recarregar(self):
        try:
            resumo = self.backend.financeiro.resumo()
            movimentos = self.backend.financeiro.movimentos()
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Erro", str(exc))
            return
        # Perfil de vendas não enxerga as saídas de salário.
        if self.role == "vendas":
            movimentos = [m for m in movimentos if m.get("origem") != "salario"]
        for chave, card in self._cards.items():
            card.set_valor(format_currency(resumo.get(chave, 0)))
        for m in movimentos:
            m["valor"] = format_currency(m.get("valor"))
        self.tabela.carregar(movimentos)
