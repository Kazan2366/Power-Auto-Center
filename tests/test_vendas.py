import pytest

from controller.categoria_peca_controller import CategoriaPecaController
from controller.estoque_controller import EstoqueController
from controller.marca_controller import MarcaController
from controller.modelo_controller import ModeloController
from controller.peca_controller import PecaController
from controller.venda_controller import VendaController


def _seed_produtos(conn):
    marca_id = MarcaController(conn).cadastrar("Fiat")
    modelo_id = ModeloController(conn).cadastrar("Uno", "SN-VENDA-1", marca_id)
    categoria_id = CategoriaPecaController(conn).cadastrar("Freios", None)
    peca_id = PecaController(conn).cadastrar("Pastilha", categoria_id, 100.0)
    estoque = EstoqueController(conn)
    estoque.definir_veiculo(modelo_id, 2)
    estoque.definir_peca(peca_id, 5)
    return modelo_id, peca_id, estoque


def test_venda_baixa_estoque_e_exclusao_devolve(conn):
    modelo_id, peca_id, estoque = _seed_produtos(conn)
    vendas = VendaController(conn)

    venda_id = vendas.registrar_venda("mista", [
        {"produto_id": modelo_id, "tipo_produto": "veiculo", "quantidade": 1, "preco_unitario": 1000.0},
        {"produto_id": peca_id, "tipo_produto": "peca", "quantidade": 2, "preco_unitario": 100.0},
    ])

    assert estoque.buscar_veiculo(modelo_id)["quantidade"] == 1
    assert estoque.buscar_peca(peca_id)["quantidade"] == 3

    vendas.excluir(venda_id)
    assert estoque.buscar_veiculo(modelo_id)["quantidade"] == 2
    assert estoque.buscar_peca(peca_id)["quantidade"] == 5


def test_venda_bloqueia_estoque_insuficiente_sem_gravar(conn):
    _modelo_id, peca_id, estoque = _seed_produtos(conn)
    vendas = VendaController(conn)

    with pytest.raises(ValueError, match="Estoque insuficiente"):
        vendas.registrar_venda("peca", [
            {"produto_id": peca_id, "tipo_produto": "peca", "quantidade": 99, "preco_unitario": 100.0},
        ])

    assert vendas.listar() == []
    assert estoque.buscar_peca(peca_id)["quantidade"] == 5


def test_venda_rejeita_tipo_invalido_no_controller(conn):
    with pytest.raises(ValueError, match="Tipo de venda"):
        VendaController(conn).registrar_venda("servico", [
            {"produto_id": 1, "tipo_produto": "peca", "quantidade": 1, "preco_unitario": 10.0},
        ])

    with pytest.raises(ValueError, match="Tipo de produto"):
        VendaController(conn).registrar_venda("peca", [
            {"produto_id": 1, "tipo_produto": "servico", "quantidade": 1, "preco_unitario": 10.0},
        ])
