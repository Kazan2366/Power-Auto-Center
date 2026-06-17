"""Tema visual central da aplicação (cores, fontes e estilos ttk)."""
import customtkinter as ctk
from tkinter import ttk

APP_NAME = "Gestão Concessionária"

# Paleta (modo escuro)
COR_FUNDO = "#1a1d23"
COR_PAINEL = "#22262e"
COR_CARD = "#2b313b"
COR_SIDEBAR = "#15171c"
COR_PRIMARIA = "#2563eb"
COR_PRIMARIA_HOVER = "#1d4ed8"
COR_SUCESSO = "#16a34a"
COR_SUCESSO_HOVER = "#15803d"
COR_PERIGO = "#dc2626"
COR_PERIGO_HOVER = "#b91c1c"
COR_TEXTO = "#e5e7eb"
COR_TEXTO_FRACO = "#9ca3af"
COR_BORDA = "#374151"
# Scrollbars (alinhadas ao tema escuro)
COR_SCROLL = "#3a4150"
COR_SCROLL_HOVER = "#4b5563"

# Perfil → cor de destaque (apenas estética)
COR_PERFIL = {
    "cadastro": "#2563eb",
    "vendas": "#16a34a",
    "mecanico": "#ea580c",
    "admin": "#7c3aed",
}


def aplicar_tema():
    """Define aparência global do CustomTkinter."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


def estilizar_treeview():
    """Aplica o tema escuro às tabelas ttk.Treeview embutidas."""
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure(
        "Conc.Treeview",
        background=COR_CARD,
        fieldbackground=COR_CARD,
        foreground=COR_TEXTO,
        rowheight=30,
        borderwidth=0,
        relief="flat",
        bordercolor=COR_CARD,
        font=("Segoe UI", 11),
    )
    # Remove a moldura/borda padrão do tema clam (a "linha branca" ao redor da
    # tabela): mantém apenas a área das linhas.
    style.layout("Conc.Treeview", [("Conc.Treeview.treearea", {"sticky": "nsew"})])
    style.configure(
        "Conc.Treeview.Heading",
        background=COR_SIDEBAR,
        foreground=COR_TEXTO,
        relief="flat",
        font=("Segoe UI", 11, "bold"),
        padding=(8, 6),
    )
    style.map(
        "Conc.Treeview.Heading",
        background=[("active", COR_PAINEL)],
    )
    style.map(
        "Conc.Treeview",
        background=[("selected", COR_PRIMARIA)],
        foreground=[("selected", "#ffffff")],
    )


# Fontes utilitárias (criadas sob demanda para evitar tk root prematuro)
def fonte_titulo():
    return ctk.CTkFont(size=22, weight="bold")


def fonte_subtitulo():
    return ctk.CTkFont(size=15, weight="bold")


def fonte_padrao():
    return ctk.CTkFont(size=13)
