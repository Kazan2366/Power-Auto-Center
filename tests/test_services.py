import os

from controller.cliente_controller import ClienteController
from controller.veiculo_cliente_controller import VeiculoClienteController
from controller.ordem_servico_controller import OrdemServicoController
from controller.venda_controller import VendaController
from controller.funcionario_controller import FuncionarioController
from service import DashboardService, FinanceiroService, RelatorioService, BackupService


def _seed_financeiro(conn):
    """Cria 1 venda (200), 1 OS (200) e 1 funcionário (salário 1000)."""
    VendaController(conn).registrar_venda(
        "peca", [{"produto_id": 1, "tipo_produto": "peca", "quantidade": 2, "preco_unitario": 100.0}]
    )
    cli = ClienteController(conn).cadastrar("Cliente A", "99988877766", None, None)
    vc = VeiculoClienteController(conn).cadastrar(cli, "Fiat", "ABC1D23", 2020)
    OrdemServicoController(conn).cadastrar(cli, vc, "Revisão", 150.0, 50.0)
    FuncionarioController(conn).cadastrar("Func A", salario=1000.0)
    return cli


def test_dashboard_resumo(conn):
    _seed_financeiro(conn)
    resumo = DashboardService(conn).resumo()
    assert resumo["total_clientes"] == 1
    assert resumo["qtd_vendas"] == 1
    assert resumo["total_vendas"] == 200.0
    assert resumo["total_funcionarios"] == 1
    assert resumo["os_abertas"] == 1


def test_financeiro_resumo_e_movimentos(conn):
    _seed_financeiro(conn)
    fin = FinanceiroService(conn)
    resumo = fin.resumo()
    assert resumo["receita_vendas"] == 200.0
    assert resumo["receita_servicos"] == 200.0
    assert resumo["receita_total"] == 400.0
    assert resumo["despesa_salarios"] == 1000.0
    assert resumo["saldo"] == -600.0

    movimentos = fin.movimentos()
    tipos = {m["origem"] for m in movimentos}
    assert {"venda", "ordem_servico", "salario"} <= tipos


def test_relatorio_gerar_csv_e_console(conn, tmp_path):
    ClienteController(conn).cadastrar("Maria", "12345678901", "11", "m@x.com")
    rel = RelatorioService(conn, dest_dir=tmp_path)

    dados = rel.gerar("clientes")
    assert "nome" in dados["headers"]
    assert any(l["nome"] == "Maria" for l in dados["linhas"])

    caminho = rel.exportar_csv("clientes")
    assert os.path.exists(caminho)
    with open(caminho, encoding="utf-8") as f:
        conteudo = f.read()
    assert "Maria" in conteudo

    texto = rel.formatar_console("clientes")
    assert "clientes" in texto and "Maria" in texto


def test_backup_cria_e_lista(conn, tmp_path):
    svc = BackupService(connection=conn, dest_dir=tmp_path)
    caminho = svc.criar_backup()
    assert os.path.exists(caminho)
    assert caminho in svc.listar_backups()
