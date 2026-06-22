from backend import Backend
from seed_exemplos import _banco_sem_exemplos, garantir_dados_exemplo


def test_garantir_dados_exemplo_semeia_banco_vazio(conn):
    b = Backend(connection=conn)
    assert _banco_sem_exemplos(b) is True

    assert garantir_dados_exemplo(b) is True

    # populou as principais entidades — sistema não começa vazio
    assert b.marcas.listar()
    assert b.clientes.listar()
    assert b.funcionarios.listar()
    assert b.veiculos.listar()
    assert _banco_sem_exemplos(b) is False


def test_garantir_dados_exemplo_idempotente(conn):
    b = Backend(connection=conn)
    assert garantir_dados_exemplo(b) is True
    qtd_marcas = len(b.marcas.listar())

    # 2ª chamada não semeia de novo nem duplica
    assert garantir_dados_exemplo(b) is False
    assert len(b.marcas.listar()) == qtd_marcas
