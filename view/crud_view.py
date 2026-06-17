"""Tela CRUD genérica, dirigida por especificação (spec).

Uma única classe atende a todas as entidades de cadastro: a tela é montada a
partir de um dicionário ``spec`` (ver :mod:`view.specs`) que descreve colunas da
tabela, campos do formulário e as funções de criar/atualizar/excluir/listar.
"""
import sqlite3
from tkinter import messagebox

import customtkinter as ctk

from view import theme
from view.widgets import DataTable


class CrudView(ctk.CTkFrame):
    def __init__(self, master, backend, spec):
        super().__init__(master, fg_color="transparent")
        self.backend = backend
        self.spec = spec
        self.controller = getattr(backend, spec["attr"])
        self.id_key = spec.get("id_key", "id")
        self._campos = {}      # key -> widget
        self._selects = {}     # key -> {label: id}
        self._id_atual = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Cabeçalho
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ctk.CTkLabel(topo, text=spec["titulo"], font=theme.fonte_titulo()).pack(side="left")
        ctk.CTkButton(topo, text="↻ Atualizar", width=110, fg_color=theme.COR_PAINEL,
                      hover_color=theme.COR_CARD, command=self.recarregar).pack(side="right")

        # Tabela
        colunas = spec["colunas"]
        self.tabela = DataTable(self, colunas, on_select=self._ao_selecionar_linha)
        self.tabela.grid(row=1, column=0, sticky="nsew", padx=(0, 12))

        # Formulário lateral
        self._montar_formulario()

        self.recarregar()

    # ---- Formulário ----------------------------------------------------
    def _montar_formulario(self):
        painel = ctk.CTkScrollableFrame(self, fg_color=theme.COR_CARD, corner_radius=10,
                                         width=340, label_text="",
                                         scrollbar_fg_color="transparent",
                                         scrollbar_button_color=theme.COR_SCROLL,
                                         scrollbar_button_hover_color=theme.COR_SCROLL_HOVER)
        painel.grid(row=1, column=1, sticky="nsew")

        ctk.CTkLabel(painel, text="Dados do registro", font=theme.fonte_subtitulo()).pack(
            anchor="w", padx=14, pady=(10, 6))

        for campo in self.spec["campos"]:
            ctk.CTkLabel(painel, text=campo["label"], anchor="w",
                         text_color=theme.COR_TEXTO_FRACO).pack(anchor="w", padx=14, pady=(8, 0))
            tipo = campo.get("tipo", "text")
            if tipo == "select":
                widget = self._criar_select(painel, campo)
            else:
                show = "•" if tipo == "password" else ""
                widget = ctk.CTkEntry(painel, height=36, show=show)
                widget.pack(fill="x", padx=14)
            self._campos[campo["key"]] = widget

        # Botões de ação
        acoes = ctk.CTkFrame(painel, fg_color="transparent")
        acoes.pack(fill="x", padx=14, pady=(18, 8))
        ctk.CTkButton(acoes, text="Salvar", fg_color=theme.COR_SUCESSO,
                      hover_color=theme.COR_SUCESSO_HOVER, command=self._criar).pack(
            fill="x", pady=4)
        self.btn_atualizar = ctk.CTkButton(acoes, text="Atualizar", fg_color=theme.COR_PRIMARIA,
                                           hover_color=theme.COR_PRIMARIA_HOVER,
                                           command=self._atualizar, state="disabled")
        self.btn_atualizar.pack(fill="x", pady=4)
        ctk.CTkButton(acoes, text="Novo / Limpar", fg_color=theme.COR_PAINEL,
                      hover_color=theme.COR_BORDA, command=self.limpar).pack(fill="x", pady=4)
        self.btn_excluir = ctk.CTkButton(acoes, text="Excluir", fg_color=theme.COR_PERIGO,
                                         hover_color=theme.COR_PERIGO_HOVER, command=self._excluir,
                                         state="disabled")
        self.btn_excluir.pack(fill="x", pady=4)

        # Ações extras opcionais (ex.: "Fechar OS")
        for label, fn in self.spec.get("acoes_extras", []):
            ctk.CTkButton(acoes, text=label, fg_color=theme.COR_PRIMARIA,
                          hover_color=theme.COR_PRIMARIA_HOVER,
                          command=lambda f=fn: self._acao_extra(f)).pack(fill="x", pady=4)

    def _criar_select(self, painel, campo):
        combo = ctk.CTkComboBox(painel, height=36, values=["—"], state="readonly")
        combo.pack(fill="x", padx=14)
        return combo

    def _atualizar_selects(self):
        """Recarrega as opções dos campos do tipo ``select`` a partir da fonte."""
        for campo in self.spec["campos"]:
            if campo.get("tipo") != "select":
                continue
            opcional = campo.get("opcional", False)
            mapa = {}
            if opcional:
                mapa["—"] = None
            for ident, rotulo in campo["fonte"](self.backend):
                mapa[rotulo] = ident
            self._selects[campo["key"]] = mapa
            self._campos[campo["key"]].configure(values=list(mapa.keys()) or ["—"])

    # ---- Dados ---------------------------------------------------------
    def recarregar(self):
        self._atualizar_selects()
        try:
            linhas = self.spec["listar"](self.controller)
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Erro ao listar", str(exc))
            return
        self.tabela.carregar(linhas)
        self.limpar()

    def _ao_selecionar_linha(self, linha):
        if not linha:
            return
        self._id_atual = linha.get(self.id_key)
        self.btn_excluir.configure(state="normal")
        self.btn_atualizar.configure(state="normal")
        for campo in self.spec["campos"]:
            key = campo["key"]
            widget = self._campos[key]
            valor = linha.get(key)
            if campo.get("tipo") == "select":
                mapa = self._selects.get(key, {})
                rotulo = next((r for r, i in mapa.items() if i == valor), None)
                widget.set(rotulo or next(iter(mapa), "—"))
            else:
                widget.delete(0, "end")
                if valor is not None:
                    widget.insert(0, self._fmt_campo(valor))

    @staticmethod
    def _fmt_campo(valor):
        if isinstance(valor, float):
            return f"{valor:.2f}"
        return str(valor)

    def limpar(self):
        self._id_atual = None
        self.btn_excluir.configure(state="disabled")
        self.btn_atualizar.configure(state="disabled")
        self.tabela.limpar_selecao()
        for campo in self.spec["campos"]:
            widget = self._campos[campo["key"]]
            if campo.get("tipo") == "select":
                mapa = self._selects.get(campo["key"], {})
                widget.set(next(iter(mapa), "—"))
            else:
                widget.delete(0, "end")

    def _coletar_valores(self):
        valores = {}
        for campo in self.spec["campos"]:
            key = campo["key"]
            tipo = campo.get("tipo", "text")
            widget = self._campos[key]
            if tipo == "select":
                valores[key] = self._selects.get(key, {}).get(widget.get())
                continue
            bruto = widget.get().strip()
            if tipo in ("int", "float") and bruto == "":
                valores[key] = None
            elif tipo == "int":
                valores[key] = int(float(bruto.replace(",", ".")))
            elif tipo == "float":
                valores[key] = float(bruto.replace(",", "."))
            else:
                valores[key] = bruto or None
        return valores

    # ---- Ações ---------------------------------------------------------
    def _criar(self):
        """Cadastra um novo registro (botão Salvar)."""
        self._persistir(modo="criar")

    def _atualizar(self):
        """Atualiza o registro selecionado (botão Atualizar)."""
        if self._id_atual is None:
            messagebox.showinfo("Atenção", "Selecione um registro na tabela para atualizar.")
            return
        self._persistir(modo="atualizar")

    def _persistir(self, modo):
        try:
            valores = self._coletar_valores()
        except ValueError:
            messagebox.showwarning("Dados inválidos", "Verifique os campos numéricos.")
            return
        try:
            if modo == "criar":
                self.spec["criar"](self.controller, valores)
                msg = "Registro cadastrado com sucesso."
            else:
                self.spec["atualizar"](self.controller, self._id_atual, valores)
                msg = "Registro atualizado com sucesso."
        except ValueError as exc:
            messagebox.showwarning("Validação", str(exc))
            return
        except sqlite3.IntegrityError:
            messagebox.showwarning("Duplicidade", "Já existe um registro com esse valor único.")
            return
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Erro ao salvar", str(exc))
            return
        self.recarregar()
        messagebox.showinfo(self.spec["titulo"], msg)

    def _excluir(self):
        if self._id_atual is None:
            return
        if not messagebox.askyesno("Confirmar exclusão", "Deseja realmente excluir este registro?"):
            return
        try:
            self.spec["excluir"](self.controller, self._id_atual)
        except Exception as exc:
            messagebox.showerror("Erro ao excluir", str(exc))
            return
        self.recarregar()

    def _acao_extra(self, fn):
        if self._id_atual is None:
            messagebox.showinfo("Atenção", "Selecione um registro primeiro.")
            return
        try:
            fn(self.controller, self._id_atual)
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))
            return
        self.recarregar()
