import pytest

from controller.marca_controller import MarcaController


def test_crud_marca(conn):
    ctrl = MarcaController(conn)
    marca_id = ctrl.cadastrar("Fiat")
    assert isinstance(marca_id, int)

    marcas = ctrl.listar()
    assert any(m["nome"] == "Fiat" for m in marcas)

    ctrl.atualizar(marca_id, "Volkswagen")
    assert ctrl.buscar(marca_id)["nome"] == "Volkswagen"

    ctrl.excluir(marca_id)
    assert ctrl.buscar(marca_id) is None


def test_nome_obrigatorio(conn):
    with pytest.raises(ValueError):
        MarcaController(conn).cadastrar("   ")
