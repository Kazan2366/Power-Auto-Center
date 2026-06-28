from backend import Backend
from database import dados_exemplo as dados
from seed_exemplos import seed
from utils.helpers import validate_chassi, validate_cpf, validate_email, validate_placa


def _assert_unicos(valores):
    assert len(valores) == len(set(valores))


def test_dados_exemplo_sao_validos():
    _assert_unicos(dados.MARCAS)
    _assert_unicos([m["numero_serie"] for m in dados.MODELOS])
    _assert_unicos([c["cpf"] for c in dados.CLIENTES])
    _assert_unicos([f["cpf"] for f in dados.FUNCIONARIOS])
    _assert_unicos([v["chassi"] for v in dados.VEICULOS])
    _assert_unicos([v["placa"] for v in dados.VEICULOS_CLIENTE])

    for cliente in dados.CLIENTES:
        assert validate_cpf(cliente["cpf"])
        assert validate_email(cliente["email"])

    for funcionario in dados.FUNCIONARIOS:
        assert validate_cpf(funcionario["cpf"])
        assert validate_email(funcionario["email"])
        assert funcionario["salario"] >= 0

    for veiculo in dados.VEICULOS:
        assert validate_chassi(veiculo["chassi"])
        assert veiculo["preco"] >= 0

    for veiculo_cliente in dados.VEICULOS_CLIENTE:
        assert validate_placa(veiculo_cliente["placa"])

    for venda in dados.VENDAS:
        assert venda["tipo"] in {"veiculo", "peca", "mista"}
        for item in venda["itens"]:
            assert item["tipo_produto"] in {"veiculo", "peca"}
            assert item["quantidade"] > 0
            assert item["preco_unitario"] >= 0

    for ordem in dados.ORDENS_SERVICO:
        assert ordem["valor_mao_de_obra"] >= 0
        assert ordem["valor_peca"] >= 0


def test_seed_expande_volume_minimo_e_e_idempotente(conn):
    b = Backend(connection=conn)

    seed(b)
    contagens = {
        "marcas": len(b.marcas.listar()),
        "modelos": len(b.modelos.listar()),
        "categorias": len(b.categorias.listar()),
        "pecas": len(b.pecas.listar()),
        "veiculos": len(b.veiculos.listar()),
        "clientes": len(b.clientes.listar()),
        "funcionarios": len(b.funcionarios.listar()),
        "veiculos_cliente": len(b.veiculos_cliente.listar()),
        "vendas": len(b.vendas.listar()),
        "ordens_servico": len(b.ordens_servico.listar()),
    }

    assert contagens["marcas"] >= 12
    assert contagens["modelos"] >= 12
    assert contagens["categorias"] >= 6
    assert contagens["pecas"] >= 12
    assert contagens["veiculos"] >= 12
    assert contagens["clientes"] >= 12
    assert contagens["funcionarios"] >= 10
    assert contagens["veiculos_cliente"] >= 12
    assert contagens["vendas"] >= 10
    assert contagens["ordens_servico"] >= 10

    seed(b)
    assert len(b.marcas.listar()) == contagens["marcas"]
    assert len(b.modelos.listar()) == contagens["modelos"]
    assert len(b.categorias.listar()) == contagens["categorias"]
    assert len(b.pecas.listar()) == contagens["pecas"]
    assert len(b.veiculos.listar()) == contagens["veiculos"]
    assert len(b.clientes.listar()) == contagens["clientes"]
    assert len(b.funcionarios.listar()) == contagens["funcionarios"]
    assert len(b.veiculos_cliente.listar()) == contagens["veiculos_cliente"]
    assert len(b.vendas.listar()) == contagens["vendas"]
    assert len(b.ordens_servico.listar()) == contagens["ordens_servico"]
