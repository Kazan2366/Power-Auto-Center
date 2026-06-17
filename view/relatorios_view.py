"""Relatórios — geração e exportação CSV (``backend.relatorios``)."""
from tkinter import messagebox

import customtkinter as ctk

from view import theme
from view.widgets import DataTable


class RelatoriosView(ctk.CTkFrame):
    def __init__(self, master, backend):
        super().__init__(master, fg_color="transparent")
        self.backend = backend
        self._tabela = None

        ctk.CTkLabel(self, text="Relatórios", font=theme.fonte_titulo()).pack(anchor="w", pady=(0, 12))

        barra = ctk.CTkFrame(self, fg_color=theme.COR_CARD, corner_radius=10)
        barra.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(barra, text="Relatório:").pack(side="left", padx=(14, 6), pady=12)
        try:
            disponiveis = backend.relatorios.listar_disponiveis()
        except Exception:
            disponiveis = []
        self.combo = ctk.CTkComboBox(barra, values=disponiveis or ["—"], width=240, state="readonly")
        self.combo.pack(side="left", pady=12)
        if disponiveis:
            self.combo.set(disponiveis[0])
        ctk.CTkButton(barra, text="Gerar", fg_color=theme.COR_PRIMARIA,
                      hover_color=theme.COR_PRIMARIA_HOVER, command=self.gerar).pack(
            side="left", padx=8, pady=12)
        ctk.CTkButton(barra, text="Exportar CSV", fg_color=theme.COR_SUCESSO,
                      hover_color=theme.COR_SUCESSO_HOVER, command=self.exportar).pack(
            side="left", padx=4, pady=12)

        self.area = ctk.CTkFrame(self, fg_color="transparent")
        self.area.pack(fill="both", expand=True)

    def gerar(self):
        nome = self.combo.get()
        try:
            rel = self.backend.relatorios.gerar(nome)
        except Exception as exc:
            messagebox.showerror("Erro ao gerar", str(exc))
            return
        headers = rel.get("headers", [])
        linhas = rel.get("linhas", [])
        colunas = [(h, h.replace("_", " ").title(), max(80, 600 // max(len(headers), 1)))
                   for h in headers]
        if self._tabela is not None:
            self._tabela.destroy()
        self._tabela = DataTable(self.area, colunas)
        self._tabela.pack(fill="both", expand=True)
        self._tabela.carregar(linhas)

    def exportar(self):
        nome = self.combo.get()
        try:
            caminho = self.backend.relatorios.exportar_csv(nome)
        except Exception as exc:
            messagebox.showerror("Erro ao exportar", str(exc))
            return
        messagebox.showinfo("Exportado", f"CSV gerado em:\n{caminho}")
