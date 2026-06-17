"""Tela de login — autentica via ``backend.auth``."""
import customtkinter as ctk

from view import theme


class LoginView(ctk.CTkFrame):
    def __init__(self, master, backend, on_sucesso):
        super().__init__(master, fg_color=theme.COR_FUNDO)
        self.backend = backend
        self.on_sucesso = on_sucesso

        cartao = ctk.CTkFrame(self, fg_color=theme.COR_CARD, corner_radius=16,
                              border_width=1, border_color=theme.COR_BORDA)
        cartao.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(cartao, text="🚗", font=ctk.CTkFont(size=44)).pack(pady=(28, 0))
        ctk.CTkLabel(cartao, text=theme.APP_NAME, font=theme.fonte_titulo()).pack(padx=48, pady=(4, 0))
        ctk.CTkLabel(cartao, text="Acesse com seu usuário", text_color=theme.COR_TEXTO_FRACO,
                     font=theme.fonte_padrao()).pack(pady=(2, 18))

        self.ent_user = ctk.CTkEntry(cartao, width=280, height=40, placeholder_text="Usuário")
        self.ent_user.pack(padx=48, pady=6)
        self.ent_user.focus()

        self.ent_pass = ctk.CTkEntry(cartao, width=280, height=40, placeholder_text="Senha", show="•")
        self.ent_pass.pack(padx=48, pady=6)

        self.lbl_erro = ctk.CTkLabel(cartao, text="", text_color=theme.COR_PERIGO,
                                     font=theme.fonte_padrao())
        self.lbl_erro.pack(pady=(4, 0))

        ctk.CTkButton(cartao, text="Entrar", width=280, height=42,
                      font=theme.fonte_subtitulo(), fg_color=theme.COR_PRIMARIA,
                      hover_color=theme.COR_PRIMARIA_HOVER, command=self._entrar).pack(padx=48, pady=(8, 6))

        dica = ("Usuários (senha: senha123):\n"
                "operador.admin · operador.cadastro · operador.vendas · operador.mecanico")
        ctk.CTkLabel(cartao, text=dica, text_color=theme.COR_TEXTO_FRACO, justify="center",
                     font=ctk.CTkFont(size=11), wraplength=300).pack(padx=24, pady=(2, 24))

        self.ent_pass.bind("<Return>", lambda _e: self._entrar())
        self.ent_user.bind("<Return>", lambda _e: self.ent_pass.focus())

    def _entrar(self):
        usuario = self.ent_user.get().strip()
        senha = self.ent_pass.get().strip()
        if not usuario or not senha:
            self.lbl_erro.configure(text="Informe usuário e senha.")
            return
        try:
            resultado = self.backend.auth.authenticate(usuario, senha)
        except Exception as exc:  # pragma: no cover - proteção de UI
            self.lbl_erro.configure(text=f"Erro: {exc}")
            return
        if resultado.get("success"):
            self.on_sucesso(resultado)
        else:
            self.lbl_erro.configure(text=resultado.get("message", "Credenciais inválidas."))
            self.ent_pass.delete(0, "end")
