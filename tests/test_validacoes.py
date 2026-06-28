import pytest

from controller.cliente_controller import ClienteController
from controller.funcionario_controller import FuncionarioController
from controller.marca_controller import MarcaController
from controller.modelo_controller import ModeloController
from controller.veiculo_cliente_controller import VeiculoClienteController
from controller.ordem_servico_controller import OrdemServicoController


def test_cliente_valida_cpf_email_e_duplicidade(conn):
    ctrl = ClienteController(conn)
    with pytest.raises(ValueError, match="CPF deve conter 11"):
        ctrl.cadastrar("Ana", "123", None, None)
    with pytest.raises(ValueError, match="E-mail inválido"):
        ctrl.cadastrar("Ana", "11122233344", None, "email-invalido")

    ctrl.cadastrar("Ana", "111.222.333-44", None, "ana@email.com")
    with pytest.raises(ValueError, match="CPF"):
        ctrl.cadastrar("Outra", "11122233344", None, None)


def test_funcionario_valida_cpf_email(conn):
    ctrl = FuncionarioController(conn)
    with pytest.raises(ValueError, match="CPF deve conter 11"):
        ctrl.cadastrar("João", cpf="123")
    with pytest.raises(ValueError, match="E-mail inválido"):
        ctrl.cadastrar("João", cpf="11122233344", email="email")


def test_veiculo_cliente_valida_placa_e_duplicidade(conn):
    cliente_id = ClienteController(conn).cadastrar("Ana", "11122233344", None, None)
    ctrl = VeiculoClienteController(conn)
    with pytest.raises(ValueError, match="Placa deve"):
        ctrl.cadastrar(cliente_id, "Fiat", "XYZ", 2020)

    ctrl.cadastrar(cliente_id, "Fiat", "ABC-1234", 2020)
    with pytest.raises(ValueError, match="placa"):
        ctrl.cadastrar(cliente_id, "Fiat", "ABC1234", 2021)


def test_duplicidade_marca_e_modelo_amigavel(conn):
    marcas = MarcaController(conn)
    marca_id = marcas.cadastrar("Fiat")
    with pytest.raises(ValueError, match="nome da marca"):
        marcas.cadastrar("Fiat")

    modelos = ModeloController(conn)
    modelos.cadastrar("Uno", "SN-0001", marca_id)
    with pytest.raises(ValueError, match="número de série"):
        modelos.cadastrar("Outro", "SN-0001", marca_id)


def test_fechar_ordem_servico_idempotente(conn):
    cliente_id = ClienteController(conn).cadastrar("Ana", "11122233344", None, None)
    veiculo_cliente_id = VeiculoClienteController(conn).cadastrar(cliente_id, "Fiat", "ABC1234", 2020)
    ctrl = OrdemServicoController(conn)
    os_id = ctrl.cadastrar(cliente_id, veiculo_cliente_id, "Revisão", 10.0, 0.0)

    ctrl.fechar(os_id)
    assert ctrl.buscar(os_id)["saida"] is not None

    with pytest.raises(ValueError, match="já está fechada"):
        ctrl.fechar(os_id)
    with pytest.raises(ValueError, match="não encontrada"):
        ctrl.fechar(9999)
