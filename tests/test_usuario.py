import pytest

from controller.usuario_controller import UsuarioController


def test_crud_usuario(conn):
    ctrl = UsuarioController(conn)
    uid = ctrl.cadastrar("operador1", "senha123", "vendas")
    assert isinstance(uid, int)

    registro = ctrl.buscar(uid)
    assert registro["username"] == "operador1"
    assert "password" not in registro  # senha nunca exposta

    ctrl.atualizar(uid, "operador1", "novasenha", "cadastro")
    assert ctrl.buscar(uid)["role"] == "cadastro"

    ctrl.excluir(uid)
    assert ctrl.buscar(uid) is None


def test_listar_inclui_semente_sem_senha(conn):
    usuarios = UsuarioController(conn).listar()
    assert len(usuarios) >= 3
    assert all("password" not in u for u in usuarios)


def test_role_invalido(conn):
    with pytest.raises(ValueError):
        UsuarioController(conn).cadastrar("x", "y", "papel_invalido")


def test_campos_obrigatorios(conn):
    ctrl = UsuarioController(conn)
    with pytest.raises(ValueError):
        ctrl.cadastrar("", "y", "vendas")
    with pytest.raises(ValueError):
        ctrl.cadastrar("x", "", "vendas")
