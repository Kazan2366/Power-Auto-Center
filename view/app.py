"""Aplicação CustomTkinter — orquestra login → janela principal.

Mantém uma única instância de :class:`backend.Backend` (uma conexão) durante
toda a sessão e a fecha ao encerrar.
"""
from tkinter import messagebox

import customtkinter as ctk

from backend import Backend
from view import theme
from view.login_view import LoginView
from view.main_window import MainWindow


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        theme.aplicar_tema()
        theme.estilizar_treeview()

        self.title(theme.APP_NAME)
        self.geometry("1180x720")
        self.minsize(960, 600)
        self.configure(fg_color=theme.COR_FUNDO)

        try:
            self.backend = Backend()
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Erro ao iniciar", f"Falha ao abrir o banco:\n{exc}")
            self.destroy()
            raise

        self._tela = None
        self.protocol("WM_DELETE_WINDOW", self._encerrar)
        self._mostrar_login()

    # ---- troca de telas ------------------------------------------------
    def _trocar(self, fabrica):
        if self._tela is not None:
            self._tela.destroy()
        self._tela = fabrica()
        self._tela.pack(fill="both", expand=True)

    def _mostrar_login(self):
        self._trocar(lambda: LoginView(self, self.backend, self._ao_logar))

    def _ao_logar(self, sessao):
        self._trocar(lambda: MainWindow(self, self.backend, sessao, self._mostrar_login))

    def _encerrar(self):
        try:
            self.backend.fechar()
        except Exception:
            pass
        self.destroy()


def run():
    """Inicia a aplicação gráfica."""
    app = App()
    app.mainloop()
