import pytest

from controller.funcionario_controller import FuncionarioController


def test_crud_funcionario(conn):
    ctrl = FuncionarioController(conn)
    fid = ctrl.cadastrar(
        "Ana Souza", cargo="Vendedora", cpf="11122233344",
        telefone="11999990000", email="ana@loja.com",
        salario=2500.0, data_admissao="2026-01-10",
    )
    assert isinstance(fid, int)

    registro = ctrl.buscar(fid)
    assert registro["nome"] == "Ana Souza"
    assert registro["salario"] == 2500.0

    ctrl.atualizar(fid, "Ana S. Lima", cargo="Gerente", cpf="11122233344",
                   telefone=None, email=None, salario=4000.0, data_admissao="2026-01-10")
    assert ctrl.buscar(fid)["cargo"] == "Gerente"
    assert ctrl.total_salarios() == 4000.0

    ctrl.excluir(fid)
    assert ctrl.buscar(fid) is None


def test_nome_obrigatorio(conn):
    with pytest.raises(ValueError):
        FuncionarioController(conn).cadastrar("")


def test_salario_negativo_invalido(conn):
    with pytest.raises(ValueError):
        FuncionarioController(conn).cadastrar("Bruno", salario=-1)
