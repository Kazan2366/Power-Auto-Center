"""Camada de apresentação (View) em CustomTkinter.

Consome a fachada :class:`backend.Backend` — não acessa o banco diretamente,
mantendo o padrão MVC do projeto (model → controller/service → view).

Ponto de entrada: :func:`view.app.run`.
"""
from view.app import run

__all__ = ["run"]
