"""Janela principal: sidebar de navegação + área de conteúdo.

O menu exibido depende do perfil (``role``) autenticado.
"""
import customtkinter as ctk

from view import theme
from view.crud_view import CrudView
from view.specs import construir_specs
from view.dashboard_view import DashboardView
from view.financeiro_view import FinanceiroView
from view.relatorios_view import RelatoriosView
from view.backup_view import BackupView
from view.estoque_view import EstoqueView
from view.vendas_view import VendasView

# Ordem e rótulos do menu (key, rótulo, ícone)
MENU = [
    ("dashboard", "Dashboard", "📊"),
    ("clientes", "Clientes", "🧑"),
    ("funcionarios", "Funcionários", "👔"),
    ("usuarios", "Usuários", "🔑"),
    ("marcas", "Marcas", "🏷️"),
    ("categorias", "Categorias", "📂"),
    ("modelos", "Modelos", "📋"),
    ("veiculos", "Veículos", "🚗"),
    ("veiculos_cliente", "Veíc. Clientes", "🚙"),
    ("pecas", "Peças", "🔧"),
    ("estoque", "Estoque", "📦"),
    ("vendas", "Vendas", "💰"),
    ("ordens_servico", "Ordens Serviço", "🛠️"),
    ("financeiro", "Financeiro", "📈"),
    ("relatorios", "Relatórios", "📄"),
    ("backup", "Backup", "💾"),
]

# Perfil → chaves liberadas (admin/desconhecido = tudo)
PERMISSOES = {
    "cadastro": {"dashboard", "clientes", "funcionarios", "usuarios", "marcas", "categorias",
                 "modelos", "veiculos", "pecas", "estoque", "relatorios", "backup"},
    "vendas": {"dashboard", "clientes", "veiculos", "estoque", "vendas", "financeiro", "relatorios"},
    "mecanico": {"dashboard", "clientes", "veiculos_cliente", "ordens_servico", "pecas", "estoque"},
}


class _NavItem(ctk.CTkFrame):
    """Item da sidebar: apenas o rótulo, alinhado à esquerda.

    Sem ícones/emojis (que tinham larguras inconsistentes e desalinhavam os
    rótulos), todos os textos começam na mesma posição.
    """

    def __init__(self, master, rotulo, command):
        super().__init__(master, fg_color="transparent", corner_radius=6)
        self.command = command
        self._ativo = False
        self.grid_columnconfigure(0, weight=1)

        self.lbl_texto = ctk.CTkLabel(self, text=rotulo, anchor="w",
                                      font=theme.fonte_padrao())
        self.lbl_texto.grid(row=0, column=0, sticky="w", padx=14, pady=9)

        for alvo in (self, self.lbl_texto):
            alvo.bind("<Button-1>", lambda _e: self.command())
            alvo.bind("<Enter>", self._ao_entrar)
            alvo.bind("<Leave>", self._ao_sair)

    def _ao_entrar(self, _evento):
        if not self._ativo:
            self.configure(fg_color=theme.COR_PAINEL)

    def _ao_sair(self, _evento):
        if not self._ativo:
            self.configure(fg_color="transparent")

    def set_ativo(self, ativo):
        self._ativo = ativo
        self.configure(fg_color=theme.COR_PRIMARIA if ativo else "transparent")


class MainWindow(ctk.CTkFrame):
    def __init__(self, master, backend, sessao, on_logout):
        super().__init__(master, fg_color=theme.COR_FUNDO)
        self.backend = backend
        self.sessao = sessao
        self.on_logout = on_logout
        self.specs = construir_specs()
        self._conteudo_atual = None
        self._botoes = {}

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._montar_sidebar()

        self.area = ctk.CTkFrame(self, fg_color=theme.COR_PAINEL, corner_radius=0)
        self.area.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        self.area.grid_columnconfigure(0, weight=1)
        self.area.grid_rowconfigure(0, weight=1)

        chaves = self._chaves_permitidas()
        if chaves:
            self.navegar(chaves[0])

    # ---- sidebar -------------------------------------------------------
    def _chaves_permitidas(self):
        role = (self.sessao.get("role") or "").lower()
        permitido = PERMISSOES.get(role)
        return [k for k, _l, _i in MENU if permitido is None or k in permitido]

    def _montar_sidebar(self):
        role = (self.sessao.get("role") or "").lower()
        cor = theme.COR_PERFIL.get(role, theme.COR_PRIMARIA)

        bar = ctk.CTkFrame(self, fg_color=theme.COR_SIDEBAR, corner_radius=0, width=220)
        bar.grid(row=0, column=0, sticky="nsew")
        bar.grid_propagate(False)
        bar.grid_rowconfigure(2, weight=1)

        # cabeçalho
        topo = ctk.CTkFrame(bar, fg_color="transparent")
        topo.grid(row=0, column=0, sticky="ew", padx=16, pady=(20, 4))
        ctk.CTkLabel(topo, text="🚗 Concessionária", font=theme.fonte_subtitulo()).pack(anchor="w")
        ctk.CTkLabel(topo, text=self.sessao.get("username", ""), text_color=theme.COR_TEXTO_FRACO,
                     font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkLabel(topo, text=f"Perfil: {role or '—'}", text_color=cor,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 6))

        # botões de navegação (com rolagem para perfis com muitos itens)
        nav = ctk.CTkScrollableFrame(
            bar, fg_color="transparent",
            scrollbar_fg_color="transparent",
            scrollbar_button_color=theme.COR_SCROLL,
            scrollbar_button_hover_color=theme.COR_SCROLL_HOVER,
        )
        nav.grid(row=2, column=0, sticky="nsew", padx=8)
        permitido = PERMISSOES.get(role)
        for key, rotulo, _icone in MENU:
            if permitido is not None and key not in permitido:
                continue
            item = _NavItem(nav, rotulo, command=lambda k=key: self.navegar(k))
            item.pack(fill="x", pady=2)
            self._botoes[key] = item

        ctk.CTkButton(bar, text="⎋  Sair", height=40, fg_color=theme.COR_PERIGO,
                      hover_color=theme.COR_PERIGO_HOVER, command=self.on_logout).grid(
            row=3, column=0, sticky="ew", padx=16, pady=16)

    # ---- navegação -----------------------------------------------------
    def navegar(self, key):
        for k, item in self._botoes.items():
            item.set_ativo(k == key)
        if self._conteudo_atual is not None:
            self._conteudo_atual.destroy()
        self._conteudo_atual = self._criar_view(key)
        self._conteudo_atual.grid(row=0, column=0, sticky="nsew")

    def _criar_view(self, key):
        if key == "dashboard":
            return DashboardView(self.area, self.backend, role=self.sessao.get("role"))
        if key == "financeiro":
            return FinanceiroView(self.area, self.backend, role=self.sessao.get("role"))
        if key == "relatorios":
            return RelatoriosView(self.area, self.backend)
        if key == "backup":
            return BackupView(self.area, self.backend)
        if key == "estoque":
            return EstoqueView(self.area, self.backend)
        if key == "vendas":
            return VendasView(self.area, self.backend)
        return CrudView(self.area, self.backend, self.specs[key])
