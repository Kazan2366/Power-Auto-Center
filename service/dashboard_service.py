"""DashboardService - indicadores agregados para a tela inicial."""
from model.estoque import Estoque
from model.venda import Venda
from service.common import scalar


class DashboardService:
    def __init__(self, connection):
        self.connection = connection
        self.estoque = Estoque(connection)
        self.venda = Venda(connection)

    def resumo(self) -> dict:
        return {
            "total_clientes": scalar(self.connection, "SELECT COUNT(*) FROM clientes"),
            "total_funcionarios": scalar(self.connection, "SELECT COUNT(*) FROM funcionarios"),
            "total_usuarios": scalar(self.connection, "SELECT COUNT(*) FROM users"),
            "total_marcas": scalar(self.connection, "SELECT COUNT(*) FROM marcas"),
            "total_categorias": scalar(self.connection, "SELECT COUNT(*) FROM categorias_peca"),
            "total_veiculos": scalar(self.connection, "SELECT COUNT(*) FROM veiculos"),
            "total_pecas": scalar(self.connection, "SELECT COUNT(*) FROM pecas"),
            "veiculos_em_estoque": self.estoque.total_veiculos(),
            "pecas_em_estoque": self.estoque.total_pecas(),
            "qtd_vendas": scalar(self.connection, "SELECT COUNT(*) FROM vendas"),
            "total_vendas": self.venda.total_vendas(),
            "os_abertas": scalar(
                self.connection,
                "SELECT COUNT(*) FROM ordem_servico WHERE saida IS NULL",
            ),
            "os_total": scalar(self.connection, "SELECT COUNT(*) FROM ordem_servico"),
        }
