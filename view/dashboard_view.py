"""Dashboard — visão executiva orientada ao perfil do usuário.

Cada perfil vê apenas os indicadores e gráficos relevantes à sua rotina, com
4 KPIs em destaque e 2 gráficos (rosca + barras), evitando excesso de informação.
"""
from collections import Counter
from tkinter import messagebox

import customtkinter as ctk

from view import theme
from view.widgets import StatCard
from view.charts import DonutChart, BarChart
from utils.helpers import format_currency

_VERDE = theme.COR_SUCESSO
_AZUL = theme.COR_PRIMARIA
_LARANJA = theme.COR_LARANJA
_ROXO = theme.COR_ROXO
_VERMELHO = theme.COR_PERIGO
_CIANO = theme.COR_CIANO


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, backend, role=None):
        super().__init__(master, fg_color="transparent")
        self.backend = backend
        self.role = (role or "").lower()

        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", pady=(0, 14))
        col = ctk.CTkFrame(topo, fg_color="transparent")
        col.pack(side="left")
        ctk.CTkLabel(col, text="Dashboard", font=theme.fonte_titulo()).pack(anchor="w")
        ctk.CTkLabel(col, text=self._subtitulo(), text_color=theme.COR_TEXTO_FRACO,
                     font=theme.fonte_padrao()).pack(anchor="w")
        ctk.CTkButton(topo, text="↻ Atualizar", width=110, fg_color=theme.COR_PAINEL,
                      hover_color=theme.COR_CARD, command=self.recarregar).pack(side="right")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        self.lbl_status = ctk.CTkLabel(self, text="", text_color=theme.COR_TEXTO_FRACO)
        self.lbl_status.pack(anchor="w", pady=(6, 0))
        self.recarregar()

    def _subtitulo(self):
        nomes = {"cadastro": "Visão de cadastros e inventário",
                 "vendas": "Visão comercial e financeira",
                 "mecanico": "Visão da oficina e serviços",
                 "admin": "Visão geral do negócio"}
        return nomes.get(self.role, "Visão geral do negócio")

    # ---- coleta de dados ----------------------------------------------
    def _coletar(self):
        b = self.backend
        dados = {"resumo": {}, "fin": {}, "vendas": [], "ordens": []}
        try:
            dados["resumo"] = b.dashboard.resumo()
            dados["fin"] = b.financeiro.resumo()
            dados["vendas"] = b.vendas.listar()
            dados["ordens"] = b.ordens_servico.listar()
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Erro ao carregar dashboard", str(exc))
        return dados

    # ---- montagem ------------------------------------------------------
    def recarregar(self):
        self._set_busy("Carregando dashboard...")
        for w in self.container.winfo_children():
            w.destroy()
        try:
            d = self._coletar()
            construtor = {
                "cadastro": self._montar_cadastro,
                "vendas": self._montar_vendas,
                "mecanico": self._montar_mecanico,
            }.get(self.role, self._montar_admin)
            kpis, graf1, graf2 = construtor(d)
            self._render(kpis, graf1, graf2)
        finally:
            self._set_busy("")

    def _set_busy(self, text):
        self.lbl_status.configure(text=text)
        self.update_idletasks()

    def _render(self, kpis, graf1, graf2):
        c = self.container
        for i in range(4):
            c.grid_columnconfigure(i, weight=1, uniform="kpi")
        c.grid_rowconfigure(1, weight=1)

        for i, (titulo, valor, cor, icone) in enumerate(kpis):
            StatCard(c, titulo, valor, cor=cor, icone=icone).grid(
                row=0, column=i, padx=6, pady=(0, 12), sticky="ew")

        graf1.grid(row=1, column=0, columnspan=2, padx=(0, 6), sticky="nsew")
        graf2.grid(row=1, column=2, columnspan=2, padx=(6, 0), sticky="nsew")

    # ---- por perfil ----------------------------------------------------
    def _montar_cadastro(self, d):
        r = d["resumo"]
        kpis = [
            ("Clientes", r.get("total_clientes", 0), _AZUL, "👥"),
            ("Veículos (catálogo)", r.get("total_veiculos", 0), _CIANO, "🚗"),
            ("Peças", r.get("total_pecas", 0), _LARANJA, "🔧"),
            ("Veículos em estoque", r.get("veiculos_em_estoque", 0), _VERDE, "📦"),
        ]
        barras = BarChart(self.container, "Cadastros por entidade")
        barras.set_data([
            ("Clientes", r.get("total_clientes", 0), _AZUL),
            ("Funcion.", r.get("total_funcionarios", 0), _ROXO),
            ("Marcas", r.get("total_marcas", 0), _CIANO),
            ("Veículos", r.get("total_veiculos", 0), _VERDE),
            ("Peças", r.get("total_pecas", 0), _LARANJA),
        ])
        donut = DonutChart(self.container, "Itens em estoque")
        donut.set_data([
            ("Veículos", r.get("veiculos_em_estoque", 0), _AZUL),
            ("Peças", r.get("pecas_em_estoque", 0), _LARANJA),
        ])
        return kpis, barras, donut

    def _montar_vendas(self, d):
        r, fin = d["resumo"], d["fin"]
        qtd = r.get("qtd_vendas", 0) or 0
        total = r.get("total_vendas", 0) or 0
        ticket = total / qtd if qtd else 0
        kpis = [
            ("Total vendido", format_currency(total), _VERDE, "💰"),
            ("Qtd. de vendas", qtd, _AZUL, "🧾"),
            ("Ticket médio", format_currency(ticket), _CIANO, "📊"),
            ("Saldo", format_currency(fin.get("saldo", 0)), _ROXO, "📈"),
        ]
        donut = DonutChart(self.container, "Receita por origem", fmt=format_currency)
        donut.set_data([
            ("Vendas", fin.get("receita_vendas", 0), _VERDE),
            ("Serviços", fin.get("receita_servicos", 0), _AZUL),
        ])
        cont = Counter(v.get("tipo", "?") for v in d["vendas"])
        barras = BarChart(self.container, "Vendas por tipo")
        barras.set_data([
            ("Veículo", cont.get("veiculo", 0), _AZUL),
            ("Peça", cont.get("peca", 0), _LARANJA),
            ("Mista", cont.get("mista", 0), _ROXO),
        ])
        return kpis, donut, barras

    def _montar_mecanico(self, d):
        r = d["resumo"]
        abertas = r.get("os_abertas", 0) or 0
        total = r.get("os_total", 0) or 0
        kpis = [
            ("OS abertas", abertas, _LARANJA, "🛠️"),
            ("OS totais", total, _AZUL, "📋"),
            ("Peças em estoque", r.get("pecas_em_estoque", 0), _VERDE, "🔧"),
            ("Veíc. de clientes", len({o.get("veiculo_cliente_id") for o in d["ordens"]}), _CIANO, "🚙"),
        ]
        donut = DonutChart(self.container, "Status das ordens de serviço")
        donut.set_data([
            ("Abertas", abertas, _LARANJA),
            ("Fechadas", max(total - abertas, 0), _VERDE),
        ])
        mao = sum(o.get("valor_mao_de_obra") or 0 for o in d["ordens"])
        peca = sum(o.get("valor_peca") or 0 for o in d["ordens"])
        barras = BarChart(self.container, "Faturamento de serviços", fmt=format_currency)
        barras.set_data([("Mão de obra", mao, _AZUL), ("Peças", peca, _LARANJA)])
        return kpis, donut, barras

    def _montar_admin(self, d):
        r, fin = d["resumo"], d["fin"]
        kpis = [
            ("Saldo", format_currency(fin.get("saldo", 0)), _ROXO, "📈"),
            ("Receita total", format_currency(fin.get("receita_total", 0)), _VERDE, "💰"),
            ("Qtd. de vendas", r.get("qtd_vendas", 0), _AZUL, "🧾"),
            ("OS abertas", r.get("os_abertas", 0), _LARANJA, "🛠️"),
        ]
        barras = BarChart(self.container, "Resumo financeiro", fmt=format_currency)
        barras.set_data([
            ("Rec. vendas", fin.get("receita_vendas", 0), _VERDE),
            ("Rec. serviços", fin.get("receita_servicos", 0), _AZUL),
            ("Salários", fin.get("despesa_salarios", 0), _VERMELHO),
            ("Saldo", fin.get("saldo", 0), _ROXO),
        ])
        donut = DonutChart(self.container, "Receita por origem", fmt=format_currency)
        donut.set_data([
            ("Vendas", fin.get("receita_vendas", 0), _VERDE),
            ("Serviços", fin.get("receita_servicos", 0), _AZUL),
        ])
        return kpis, barras, donut
