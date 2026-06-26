"""Vendas — registra vendas com itens (``backend.vendas``)."""
from tkinter import messagebox

import customtkinter as ctk

from view import theme
from view.widgets import DataTable
from utils.helpers import format_currency


class VendasView(ctk.CTkFrame):
    def __init__(self, master, backend):
        super().__init__(master, fg_color="transparent")
        self.backend = backend
        self._carrinho = []  # list[dict] de itens

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=1)

        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ctk.CTkLabel(topo, text="Vendas", font=theme.fonte_titulo()).pack(side="left")
        ctk.CTkButton(topo, text="↻ Atualizar", width=110, fg_color=theme.COR_PAINEL,
                      hover_color=theme.COR_CARD, command=self.recarregar).pack(side="right")
        ctk.CTkButton(topo, text="Excluir venda selecionada", width=190, fg_color=theme.COR_PERIGO,
                      hover_color=theme.COR_PERIGO_HOVER, command=self._excluir_venda).pack(
            side="right", padx=8)

        self.tabela = DataTable(self, [
            ("id", "ID", 60), ("data", "Data", 160), ("tipo", "Tipo", 120), ("total", "Total", 140),
        ], on_select=self._ao_selecionar)
        self.tabela.grid(row=1, column=0, sticky="nsew", padx=(0, 12))

        self._montar_painel_nova_venda()
        self.recarregar()

    def _montar_painel_nova_venda(self):
        painel = ctk.CTkFrame(self, fg_color=theme.COR_CARD, corner_radius=10, width=360)
        painel.grid(row=1, column=1, sticky="nsew")
        painel.grid_propagate(False)

        ctk.CTkLabel(painel, text="Nova venda", font=theme.fonte_subtitulo()).pack(
            anchor="w", padx=14, pady=(12, 6))

        ctk.CTkLabel(painel, text="Tipo de produto", text_color=theme.COR_TEXTO_FRACO,
                     anchor="w").pack(anchor="w", padx=14)
        self.combo_tipo = ctk.CTkComboBox(painel, values=["veiculo", "peca"], state="readonly",
                                          command=lambda _v: self._carregar_produtos())
        self.combo_tipo.pack(fill="x", padx=14, pady=(0, 6))

        ctk.CTkLabel(painel, text="Produto", text_color=theme.COR_TEXTO_FRACO,
                     anchor="w").pack(anchor="w", padx=14)
        self.combo_produto = ctk.CTkComboBox(painel, values=["—"], state="readonly",
                                             command=lambda _v: self._preencher_preco())
        self.combo_produto.pack(fill="x", padx=14, pady=(0, 6))

        linha = ctk.CTkFrame(painel, fg_color="transparent")
        linha.pack(fill="x", padx=14)
        ctk.CTkLabel(linha, text="Qtd.", text_color=theme.COR_TEXTO_FRACO).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(linha, text="Preço unit.", text_color=theme.COR_TEXTO_FRACO).grid(row=0, column=1, sticky="w", padx=(8, 0))
        self.ent_qtd = ctk.CTkEntry(linha, width=70)
        self.ent_qtd.insert(0, "1")
        self.ent_qtd.grid(row=1, column=0, sticky="w")
        self.ent_preco = ctk.CTkEntry(linha, width=120)
        self.ent_preco.grid(row=1, column=1, sticky="w", padx=(8, 0))

        ctk.CTkButton(painel, text="+ Adicionar item", fg_color=theme.COR_PRIMARIA,
                      hover_color=theme.COR_PRIMARIA_HOVER, command=self._adicionar_item).pack(
            fill="x", padx=14, pady=(10, 6))

        self.tabela_itens = DataTable(painel, [
            ("descricao", "Item", 150), ("quantidade", "Qtd", 50), ("subtotal", "Subtotal", 90),
        ])

        # Total e botões são ancorados ao rodapé (side="bottom") ANTES da tabela,
        # garantindo que fiquem sempre visíveis mesmo quando a janela é baixa.
        botoes = ctk.CTkFrame(painel, fg_color="transparent")
        botoes.pack(side="bottom", fill="x", padx=14, pady=(6, 12))
        ctk.CTkButton(botoes, text="Registrar venda", fg_color=theme.COR_SUCESSO,
                      hover_color=theme.COR_SUCESSO_HOVER, command=self._registrar).pack(fill="x", pady=3)
        ctk.CTkButton(botoes, text="Limpar carrinho", fg_color=theme.COR_PAINEL,
                      hover_color=theme.COR_BORDA, command=self._limpar_carrinho).pack(fill="x", pady=3)

        self.lbl_total = ctk.CTkLabel(painel, text="Total: R$ 0,00", font=theme.fonte_subtitulo())
        self.lbl_total.pack(side="bottom", anchor="e", padx=14)

        # A tabela preenche o espaço restante entre os campos e o rodapé.
        self.tabela_itens.pack(fill="both", expand=True, padx=14, pady=(0, 6))

        self.combo_tipo.set("veiculo")
        self._carregar_produtos()

    # ---- produtos / carrinho ------------------------------------------
    def _carregar_produtos(self):
        tipo = self.combo_tipo.get()
        if tipo == "veiculo":
            # Estoque é por modelo; preço representativo = 1º veículo do catálogo do modelo.
            precos = {}
            for v in self.backend.veiculos.listar():
                precos.setdefault(v.get("modelo_id"), v.get("preco") or 0)
            itens = [(m["id"], f'{m.get("marca_nome") or "?"} — {m["nome"]}', precos.get(m["id"], 0))
                     for m in self.backend.modelos.listar()]
        else:
            itens = [(p["id"], p["nome"], p.get("preco") or 0) for p in self.backend.pecas.listar()]
        self._produtos = {rotulo: (pid, preco) for pid, rotulo, preco in itens}
        self.combo_produto.configure(values=list(self._produtos.keys()) or ["—"])
        if self._produtos:
            self.combo_produto.set(next(iter(self._produtos)))
        else:
            self.combo_produto.set("—")
        self._preencher_preco()

    def _preencher_preco(self):
        info = self._produtos.get(self.combo_produto.get())
        self.ent_preco.delete(0, "end")
        if info:
            self.ent_preco.insert(0, f"{info[1]:.2f}")

    def _adicionar_item(self):
        info = self._produtos.get(self.combo_produto.get())
        if not info:
            messagebox.showinfo("Atenção", "Selecione um produto.")
            return
        try:
            qtd = int(self.ent_qtd.get().strip() or "0")
            preco = float(self.ent_preco.get().strip().replace(",", ".") or "0")
        except ValueError:
            messagebox.showwarning("Validação", "Quantidade ou preço inválido.")
            return
        if qtd <= 0:
            messagebox.showwarning("Validação", "Quantidade deve ser maior que zero.")
            return
        self._carrinho.append({
            "produto_id": info[0],
            "tipo_produto": self.combo_tipo.get(),
            "quantidade": qtd,
            "preco_unitario": preco,
            "descricao": self.combo_produto.get(),
        })
        self._render_carrinho()

    def _render_carrinho(self):
        linhas, total = [], 0.0
        for item in self._carrinho:
            sub = item["quantidade"] * item["preco_unitario"]
            total += sub
            linhas.append({"descricao": item["descricao"], "quantidade": item["quantidade"],
                           "subtotal": format_currency(sub)})
        self.tabela_itens.carregar(linhas)
        self.lbl_total.configure(text=f"Total: {format_currency(total)}")

    def _limpar_carrinho(self):
        self._carrinho = []
        self._render_carrinho()

    def _registrar(self):
        if not self._carrinho:
            messagebox.showinfo("Atenção", "Adicione ao menos um item.")
            return
        tipos = {i["tipo_produto"] for i in self._carrinho}
        tipo_venda = "mista" if len(tipos) > 1 else next(iter(tipos))
        itens = [{k: i[k] for k in ("produto_id", "tipo_produto", "quantidade", "preco_unitario")}
                 for i in self._carrinho]
        try:
            self.backend.vendas.registrar_venda(tipo_venda, itens)
        except ValueError as exc:
            messagebox.showwarning("Validação", str(exc))
            return
        except Exception as exc:
            messagebox.showerror("Erro ao registrar", str(exc))
            return
        self._limpar_carrinho()
        self.recarregar()
        messagebox.showinfo("Vendas", "Venda registrada com sucesso.")

    # ---- lista de vendas ----------------------------------------------
    def _ao_selecionar(self, linha):
        self._venda_sel = linha.get("id") if linha else None

    def _excluir_venda(self):
        venda_id = getattr(self, "_venda_sel", None)
        if venda_id is None:
            messagebox.showinfo("Atenção", "Selecione uma venda na tabela.")
            return
        if not messagebox.askyesno("Confirmar", "Excluir a venda selecionada?"):
            return
        try:
            self.backend.vendas.excluir(venda_id)
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))
            return
        self.recarregar()

    def recarregar(self):
        self._carregar_produtos()
        try:
            vendas = self.backend.vendas.listar()
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Erro", str(exc))
            return
        for v in vendas:
            v["total"] = format_currency(v.get("total"))
        self.tabela.carregar(vendas)
        self._venda_sel = None
