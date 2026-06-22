"""Ponto de entrada executável da Concessionária.

Inicia a interface gráfica (CustomTkinter) sobre a fachada `Backend`. A camada
de view (`view/`) consome apenas os controllers/serviços expostos por `Backend`,
preservando o padrão MVC (model → controller/service → view).

Uso:
    python main.py            # abre a aplicação gráfica
    python main.py --headless # apenas inicializa o banco e imprime o dashboard
"""
import sys

from backend import Backend
from database.connection import DB_FILE
from seed_exemplos import garantir_dados_exemplo


def executar_headless():
    """Modo sem UI: inicializa o banco e imprime os indicadores (debug/handoff)."""
    backend = Backend()
    garantir_dados_exemplo(backend)  # sistema nunca começa vazio
    print("Backend da Concessionária inicializado.")
    print(f"Banco de dados: {DB_FILE}")
    print("Indicadores (dashboard):")
    for chave, valor in backend.dashboard.resumo().items():
        print(f"  - {chave}: {valor}")
    backend.fechar()


def main():
    if "--headless" in sys.argv:
        executar_headless()
        return
    from view import run
    run()


if __name__ == "__main__":
    main()
