"""Backup — cria e lista cópias datadas do banco (``backend.backup``)."""
from tkinter import messagebox

import customtkinter as ctk

from view import theme
from view.widgets import DataTable


class BackupView(ctk.CTkFrame):
    def __init__(self, master, backend):
        super().__init__(master, fg_color="transparent")
        self.backend = backend

        ctk.CTkLabel(self, text="Backup", font=theme.fonte_titulo()).pack(anchor="w", pady=(0, 12))

        barra = ctk.CTkFrame(self, fg_color=theme.COR_CARD, corner_radius=10)
        barra.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(barra, text="Gere uma cópia de segurança datada do banco de dados.").pack(
            side="left", padx=14, pady=12)
        ctk.CTkButton(barra, text="Criar backup agora", fg_color=theme.COR_SUCESSO,
                      hover_color=theme.COR_SUCESSO_HOVER, command=self.criar).pack(
            side="right", padx=14, pady=12)

        ctk.CTkLabel(self, text="Backups existentes", font=theme.fonte_subtitulo(), anchor="w").pack(
            fill="x", pady=(4, 6))
        self.tabela = DataTable(self, [("arquivo", "Arquivo", 600)])
        self.tabela.pack(fill="both", expand=True)
        self.recarregar()

    def criar(self):
        try:
            caminho = self.backend.backup.criar_backup()
        except Exception as exc:
            messagebox.showerror("Erro no backup", str(exc))
            return
        messagebox.showinfo("Backup criado", f"Arquivo gerado:\n{caminho}")
        self.recarregar()

    def recarregar(self):
        try:
            arquivos = self.backend.backup.listar_backups()
        except Exception:
            arquivos = []
        self.tabela.carregar([{"arquivo": a} for a in arquivos])
