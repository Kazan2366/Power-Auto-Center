"""Estoque - define a quantidade de veículos e peças (``backend.estoque``)."""
from dataclasses import dataclass, field
from tkinter import messagebox

import customtkinter as ctk

from view import theme
from view.widgets import DataTable


@dataclass
class AbaEstoque:
    combo: ctk.CTkComboBox
    tabela: DataTable
    fonte: callable
    definir: callable
    listar: callable
    mapa: dict = field(default_factory=dict)


class EstoqueView(ctk.CTkFrame):
    def __init__(self, master, backend):
        super().__init__(master, fg_color="transparent")
        self.backend = backend

        ctk.CTkLabel(self, text="Estoque", font=theme.fonte_titulo()).pack(anchor="w", pady=(0, 12))

        self.tabs = ctk.CTkTabview(self, fg_color=theme.COR_PAINEL)
        self.tabs.pack(fill="both", expand=True)
        self.tabs.add("Veículos")
        self.tabs.add("Peças")

        self.aba_veiculos = self._montar_aba(
            self.tabs.tab("Veículos"), "veículo",
            [("modelo_id", "ID", 60), ("marca", "Marca", 140), ("modelo", "Modelo", 200),
             ("quantidade", "Qtd.", 80)],
            self._fonte_veiculos,
            lambda pid, q: self.backend.estoque.definir_veiculo(pid, q),
            self.backend.estoque.listar_veiculos,
        )
        self.aba_pecas = self._montar_aba(
            self.tabs.tab("Peças"), "peça",
            [("peca_id", "ID", 60), ("nome", "Nome", 240), ("quantidade", "Qtd.", 80)],
            self._fonte_pecas,
            lambda pid, q: self.backend.estoque.definir_peca(pid, q),
            self.backend.estoque.listar_pecas,
        )

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
        aba_estoque = AbaEstoque(combo, tabela, fonte, definir, listar)

        def aplicar():
            self._aplicar_quantidade(aba_estoque, ent_qtd, rotulo)

        ent_qtd.bind("<Return>", lambda _e: aplicar())
        ctk.CTkButton(
            barra,
            text="Definir quantidade",
            fg_color=theme.COR_SUCESSO,
            hover_color=theme.COR_SUCESSO_HOVER,
            command=aplicar,
        ).pack(side="left", padx=12, pady=10)

        ent_qtd.focus()
        return aba_estoque

    def _aplicar_quantidade(self, aba, ent_qtd, rotulo):
        pid = aba.mapa.get(aba.combo.get())
        if pid is None:
            messagebox.showinfo("Atenção", f"Selecione um(a) {rotulo}.")
            return
        try:
            qtd = int(ent_qtd.get().strip() or "0")
        except ValueError:
            messagebox.showwarning("Validação", "Quantidade deve ser um número inteiro.")
            return
        try:
            aba.definir(pid, qtd)
        except ValueError as exc:
            messagebox.showwarning("Validação", str(exc))
            return
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))
            return
        ent_qtd.delete(0, "end")
        self.recarregar()

    def _fonte_veiculos(self):
        return [(m["id"], f'{m.get("marca_nome") or "?"} — {m["nome"]}')
                for m in self.backend.modelos.listar()]

    def _fonte_pecas(self):
        return [(p["id"], p["nome"]) for p in self.backend.pecas.listar()]

    def recarregar(self):
        for aba in (self.aba_veiculos, self.aba_pecas):
            aba.mapa = {rotulo: ident for ident, rotulo in aba.fonte()}
            aba.combo.configure(values=list(aba.mapa.keys()) or ["—"])
            if aba.mapa:
                aba.combo.set(next(iter(aba.mapa)))
            try:
                aba.tabela.carregar(aba.listar())
            except Exception as exc:  # pragma: no cover
                messagebox.showerror("Erro", str(exc))
