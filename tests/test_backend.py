from backend import Backend


def test_facade_expoe_todos_os_modulos(conn):
    b = Backend(connection=conn)
    for attr in [
        "auth", "clientes", "funcionarios", "usuarios", "marcas", "modelos",
        "categorias", "veiculos", "veiculos_cliente", "pecas", "estoque",
        "vendas", "ordens_servico", "dashboard", "financeiro", "relatorios", "backup",
    ]:
        assert hasattr(b, attr), f"Backend não expõe {attr}"


def test_crud_via_facade(conn):
    b = Backend(connection=conn)
    mid = b.marcas.cadastrar("Honda")
    assert any(m["nome"] == "Honda" for m in b.marcas.listar())
    fid = b.funcionarios.cadastrar("Carlos", cargo="Mecânico", salario=3000.0)
    assert b.funcionarios.buscar(fid)["nome"] == "Carlos"
    assert b.dashboard.resumo()["total_marcas"] == 1
