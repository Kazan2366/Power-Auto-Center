"""Relatórios — geração e exportação CSV (``backend.relatorios``)."""
from tkinter import messagebox

import customtkinter as ctk

from view import theme
from view.widgets import DataTable, PageHeader, chamar_backend


class RelatoriosView(ctk.CTkFrame):
    def __init__(self, master, backend):
        super().__init__(master, fg_color="transparent")
        self.backend = backend
        self._tabela = None

        PageHeader(self, "Relatórios").pack(fill="x", pady=(0, 12))

        barra = ctk.CTkFrame(self, fg_color=theme.COR_CARD, corner_radius=10)
        barra.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(barra, text="Relatório:").pack(side="left", padx=(14, 6), pady=12)
        disponiveis = chamar_backend(backend.relatorios.listar_disponiveis, "Erro ao listar relatórios") or []
        self.combo = ctk.CTkComboBox(barra, values=disponiveis or ["—"], width=240, state="readonly")
        self.combo.pack(side="left", pady=12)
        if disponiveis:
            self.combo.set(disponiveis[0])
        self.btn_gerar = ctk.CTkButton(barra, text="Gerar", fg_color=theme.COR_PRIMARIA,
                                       hover_color=theme.COR_PRIMARIA_HOVER, command=self.gerar)
        self.btn_gerar.pack(
            side="left", padx=8, pady=12)
        self.btn_exportar = ctk.CTkButton(barra, text="Exportar CSV", fg_color=theme.COR_SUCESSO,
                                          hover_color=theme.COR_SUCESSO_HOVER, command=self.exportar)
        self.btn_exportar.pack(
            side="left", padx=4, pady=12)
        self.lbl_status = ctk.CTkLabel(self, text="", text_color=theme.COR_TEXTO_FRACO)
        self.lbl_status.pack(anchor="w", pady=(0, 6))

        self.area = ctk.CTkFrame(self, fg_color="transparent")
        self.area.pack(fill="both", expand=True)

    def gerar(self):
        nome = self.combo.get()
        self._set_busy(True, "Gerando relatorio...")
        rel = chamar_backend(lambda: self.backend.relatorios.gerar(nome), "Erro ao gerar")
        self._set_busy(False)
        if rel is None:
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
        self._set_busy(True, "Exportando CSV...")
        caminho = chamar_backend(lambda: self.backend.relatorios.exportar_csv(nome), "Erro ao exportar")
        self._set_busy(False)
        if caminho is None:
            return
        messagebox.showinfo("Exportado", f"CSV gerado em:\n{caminho}")

    def _set_busy(self, busy, text=""):
        state = "disabled" if busy else "normal"
        self.btn_gerar.configure(state=state)
        self.btn_exportar.configure(state=state)
        self.lbl_status.configure(text=text)
        self.update_idletasks()
