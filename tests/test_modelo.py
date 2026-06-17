import pytest

from controller.marca_controller import MarcaController
from controller.modelo_controller import ModeloController


def test_modelo_vinculado_a_marca(conn):
    marca_id = MarcaController(conn).cadastrar("Fiat")
    ctrl = ModeloController(conn)

    mid = ctrl.cadastrar("Uno", "SN-0001", marca_id=marca_id)
    modelo = next(m for m in ctrl.listar() if m["id"] == mid)
    assert modelo["marca_id"] == marca_id
    assert modelo["marca_nome"] == "Fiat"

    ctrl.atualizar(mid, "Uno Mille", "SN-0001", marca_id=None)
    assert ctrl.buscar(mid)["marca_id"] is None


def test_modelo_sem_marca_e_permitido(conn):
    ctrl = ModeloController(conn)
    mid = ctrl.cadastrar("Gol", "SN-0002")  # marca_id opcional
    assert ctrl.buscar(mid)["marca_id"] is None


def test_nome_obrigatorio(conn):
    with pytest.raises(ValueError):
        ModeloController(conn).cadastrar("  ", "SN-X")
