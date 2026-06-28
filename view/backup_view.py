"""Backup — cria e lista cópias datadas do banco (``backend.backup``)."""
from tkinter import messagebox

import customtkinter as ctk

from view import theme
from view.widgets import DataTable, PageHeader, chamar_backend


class BackupView(ctk.CTkFrame):
    def __init__(self, master, backend):
        super().__init__(master, fg_color="transparent")
        self.backend = backend

        PageHeader(self, "Backup").pack(fill="x", pady=(0, 12))

        barra = ctk.CTkFrame(self, fg_color=theme.COR_CARD, corner_radius=10)
        barra.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(barra, text="Gere uma cópia de segurança datada do banco de dados.").pack(
            side="left", padx=14, pady=12)
        self.btn_backup = ctk.CTkButton(barra, text="Criar backup agora", fg_color=theme.COR_SUCESSO,
                                        hover_color=theme.COR_SUCESSO_HOVER, command=self.criar)
        self.btn_backup.pack(
            side="right", padx=14, pady=12)
        self.lbl_status = ctk.CTkLabel(self, text="", text_color=theme.COR_TEXTO_FRACO)
        self.lbl_status.pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(self, text="Backups existentes", font=theme.fonte_subtitulo(), anchor="w").pack(
            fill="x", pady=(4, 6))
        self.tabela = DataTable(self, [("arquivo", "Arquivo", 600)])
        self.tabela.pack(fill="both", expand=True)
        self.recarregar()

    def criar(self):
        self._set_busy(True, "Criando backup...")
        caminho = chamar_backend(self.backend.backup.criar_backup, "Erro no backup")
        self._set_busy(False)
        if caminho is None:
            return
        messagebox.showinfo("Backup criado", f"Arquivo gerado:\n{caminho}")
        self.recarregar()

    def _set_busy(self, busy, text=""):
        self.btn_backup.configure(state="disabled" if busy else "normal")
        self.lbl_status.configure(text=text)
        self.update_idletasks()

    def recarregar(self):
        arquivos = chamar_backend(self.backend.backup.listar_backups, "Erro ao listar backups")
        if arquivos is None:
            return
        self.tabela.carregar([{"arquivo": a} for a in arquivos])
