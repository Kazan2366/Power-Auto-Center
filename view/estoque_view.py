"""Estoque — define a quantidade de veículos e peças (``backend.estoque``)."""
from tkinter import messagebox

import customtkinter as ctk

from view import theme
from view.widgets import DataTable


class EstoqueView(ctk.CTkFrame):
    def __init__(self, master, backend):
        super().__init__(master, fg_color="transparent")
        self.backend = backend

        ctk.CTkLabel(self, text="Estoque", font=theme.fonte_titulo()).pack(anchor="w", pady=(0, 12))

        self.tabs = ctk.CTkTabview(self, fg_color=theme.COR_PAINEL)
        self.tabs.pack(fill="both", expand=True)
        self.tabs.add("Veículos")
        self.tabs.add("Peças")

        self.tabela_v = self._montar_aba(
            self.tabs.tab("Veículos"), "veículo",
            [("veiculo_id", "ID", 60), ("marca", "Marca", 140), ("chassi", "Chassi", 200),
             ("quantidade", "Qtd.", 80)],
            self._fonte_veiculos, lambda pid, q: self.backend.estoque.definir_veiculo(pid, q),
            self.backend.estoque.listar_veiculos)
        self.tabela_p = self._montar_aba(
            self.tabs.tab("Peças"), "peça",
            [("peca_id", "ID", 60), ("nome", "Nome", 240), ("quantidade", "Qtd.", 80)],
            self._fonte_pecas, lambda pid, q: self.backend.estoque.definir_peca(pid, q),
            self.backend.estoque.listar_pecas)

        self.recarregar()

    def _montar_aba(self, aba, rotulo, colunas, fonte, definir, listar):
        barra = ctk.CTkFrame(aba, fg_color=theme.COR_CARD, corner_radius=10)
        barra.pack(fill="x", pady=(4, 10))
        ctk.CTkLabel(barra, text=f"{rotulo.title()}:").pack(side="left", padx=(12, 4), pady=10)
        combo = ctk.CTkComboBox(barra, values=["—"], width=260, state="readonly")
        combo.pack(side="left", pady=10)
        ctk.CTkLabel(barra, text="Qtd.:").pack(side="left", padx=(12, 4))
        ent_qtd = ctk.CTkEntry(barra, width=80)
        ent_qtd.pack(side="left", pady=10)

        tabela = DataTable(aba, colunas)
        tabela.pack(fill="both", expand=True)

        def aplicar():
            mapa = combo._mapa if hasattr(combo, "_mapa") else {}
            pid = mapa.get(combo.get())
            if pid is None:
                messagebox.showinfo("Atenção", f"Selecione um(a) {rotulo}.")
                return
            try:
                qtd = int(ent_qtd.get().strip() or "0")
                definir(pid, qtd)
            except ValueError as exc:
                messagebox.showwarning("Validação", str(exc) or "Quantidade inválida.")
                return
            except Exception as exc:
                messagebox.showerror("Erro", str(exc))
                return
            ent_qtd.delete(0, "end")
            self.recarregar()

        ctk.CTkButton(barra, text="Definir quantidade", fg_color=theme.COR_SUCESSO,
                      hover_color=theme.COR_SUCESSO_HOVER, command=aplicar).pack(
            side="left", padx=12, pady=10)

        # guarda referências para recarga
        combo._fonte = fonte
        combo._listar = listar
        combo._tabela = tabela
        return combo

    def _fonte_veiculos(self):
        return [(v["id"], f'{v.get("marca_nome") or "?"} — {v["chassi"]}')
                for v in self.backend.veiculos.listar()]

    def _fonte_pecas(self):
        return [(p["id"], p["nome"]) for p in self.backend.pecas.listar()]

    def recarregar(self):
        for combo in (self.tabela_v, self.tabela_p):
            mapa = {rotulo: ident for ident, rotulo in combo._fonte()}
            combo._mapa = mapa
            combo.configure(values=list(mapa.keys()) or ["—"])
            if mapa:
                combo.set(next(iter(mapa)))
            try:
                combo._tabela.carregar(combo._listar())
            except Exception as exc:  # pragma: no cover
                messagebox.showerror("Erro", str(exc))
