import pytest

from controller.marca_controller import MarcaController
from controller.veiculo_controller import VeiculoController


def test_crud_veiculo_normalizado(conn):
    marca_id = MarcaController(conn).cadastrar("Fiat")
    ctrl = VeiculoController(conn)

    vid = ctrl.cadastrar(marca_id, None, "CHS-001", 2022, "Preto", 50000.0)
    assert isinstance(vid, int)

    # listar() resolve o nome da marca via JOIN
    veiculo = next(v for v in ctrl.listar() if v["id"] == vid)
    assert veiculo["marca_id"] == marca_id
    assert veiculo["marca_nome"] == "Fiat"

    nova_marca = MarcaController(conn).cadastrar("Volkswagen")
    ctrl.atualizar(vid, nova_marca, None, "CHS-001", 2022, "Branco", 52000.0)
    assert ctrl.buscar(vid)["marca_id"] == nova_marca

    ctrl.excluir(vid)
    assert ctrl.buscar(vid) is None


def test_marca_obrigatoria(conn):
    with pytest.raises(ValueError):
        VeiculoController(conn).cadastrar(None, None, "X", 2020, "Azul", 1000.0)
