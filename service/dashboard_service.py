"""DashboardService — indicadores agregados para a tela inicial.

Lê apenas (somatórios/contagens) a partir da conexão injetada. Retorna um dict
plano, pronto para o frontend renderizar em cards.
"""


class DashboardService:
    def __init__(self, connection):
        self.connection = connection

    def _scalar(self, sql):
        cur = self.connection.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        return row[0] if row else 0

    def resumo(self) -> dict:
        return {
            "total_clientes": self._scalar("SELECT COUNT(*) FROM clientes"),
            "total_funcionarios": self._scalar("SELECT COUNT(*) FROM funcionarios"),
            "total_usuarios": self._scalar("SELECT COUNT(*) FROM users"),
            "total_marcas": self._scalar("SELECT COUNT(*) FROM marcas"),
            "total_categorias": self._scalar("SELECT COUNT(*) FROM categorias_peca"),
            "total_veiculos": self._scalar("SELECT COUNT(*) FROM veiculos"),
            "total_pecas": self._scalar("SELECT COUNT(*) FROM pecas"),
            "veiculos_em_estoque": self._scalar(
                "SELECT COALESCE(SUM(quantidade), 0) FROM estoque_veiculos"
            ),
            "pecas_em_estoque": self._scalar(
                "SELECT COALESCE(SUM(quantidade), 0) FROM estoque_pecas"
            ),
            "qtd_vendas": self._scalar("SELECT COUNT(*) FROM vendas"),
            "total_vendas": self._scalar("SELECT COALESCE(SUM(total), 0) FROM vendas"),
            "os_abertas": self._scalar(
                "SELECT COUNT(*) FROM ordem_servico WHERE saida IS NULL"
            ),
            "os_total": self._scalar("SELECT COUNT(*) FROM ordem_servico"),
        }
