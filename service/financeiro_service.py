"""FinanceiroService - visão financeira derivada de vendas e ordens de serviço."""
from controller.funcionario_controller import FuncionarioController
from model.venda import Venda
from service.common import scalar


class FinanceiroService:
    def __init__(self, connection):
        self.connection = connection
        self.venda = Venda(connection)
        self.funcionarios = FuncionarioController(connection)

    def resumo(self) -> dict:
        receita_vendas = self.venda.total_vendas()
        receita_servicos = scalar(
            self.connection,
            "SELECT COALESCE(SUM(COALESCE(valor_mao_de_obra, 0) + COALESCE(valor_peca, 0)), 0) "
            "FROM ordem_servico",
        )
        despesa_salarios = self.funcionarios.total_salarios()
        receita_total = receita_vendas + receita_servicos
        return {
            "receita_vendas": receita_vendas,
            "receita_servicos": receita_servicos,
            "receita_total": receita_total,
            "despesa_salarios": despesa_salarios,
            "saldo": receita_total - despesa_salarios,
        }

    def movimentos(self) -> list:
        """Lista unificada de movimentos (entradas e saídas), ordenada por data."""
        cur = self.connection.cursor()
        movs = []

        cur.execute("SELECT id, data, tipo, total FROM vendas")
        for r in cur.fetchall():
            movs.append({
                "data": r["data"],
                "origem": "venda",
                "tipo": "entrada",
                "descricao": f"Venda #{r['id']} ({r['tipo']})",
                "valor": r["total"],
            })

        cur.execute(
            "SELECT id, entrada, tipo_servico, "
            "COALESCE(valor_mao_de_obra, 0) + COALESCE(valor_peca, 0) AS valor "
            "FROM ordem_servico"
        )
        for r in cur.fetchall():
            movs.append({
                "data": r["entrada"],
                "origem": "ordem_servico",
                "tipo": "entrada",
                "descricao": f"OS #{r['id']} - {r['tipo_servico'] or 'serviço'}",
                "valor": r["valor"],
            })

        cur.execute("SELECT id, nome, salario, data_admissao FROM funcionarios")
        for r in cur.fetchall():
            if r["salario"]:
                movs.append({
                    "data": r["data_admissao"],
                    "origem": "salario",
                    "tipo": "saida",
                    "descricao": f"Salário {r['nome']}",
                    "valor": r["salario"],
                })

        movs.sort(key=lambda m: (m["data"] is None, m["data"]))
        return movs
