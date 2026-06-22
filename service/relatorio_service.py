"""RelatorioService — listagens exportáveis (console / CSV).

Cada relatório é uma consulta nomeada. `gerar` devolve {headers, linhas} pronto
para a UI; `exportar_csv` grava um arquivo; `formatar_console` devolve texto
tabular para impressão direta no terminal.
"""
import csv
import datetime
from pathlib import Path

# nome do relatório -> SQL (colunas explícitas, sem expor senha)
RELATORIOS = {
    "clientes": "SELECT id, nome, cpf, telefone, email FROM clientes ORDER BY id",
    "funcionarios": (
        "SELECT id, nome, cargo, cpf, telefone, email, salario, data_admissao "
        "FROM funcionarios ORDER BY id"
    ),
    "usuarios": "SELECT id, username, role FROM users ORDER BY id",
    "marcas": "SELECT id, nome FROM marcas ORDER BY nome",
    "modelos": (
        "SELECT m.id, m.nome, m.numero_serie, mc.nome AS marca FROM modelos m "
        "LEFT JOIN marcas mc ON mc.id = m.marca_id ORDER BY m.id"
    ),
    "categorias": "SELECT id, nome, descricao FROM categorias_peca ORDER BY id",
    "veiculos": (
        "SELECT v.id, mc.nome AS marca, m.nome AS modelo, v.chassi, v.ano_fabricacao, "
        "v.cor, v.preco FROM veiculos v "
        "LEFT JOIN marcas mc ON mc.id = v.marca_id "
        "LEFT JOIN modelos m ON m.id = v.modelo_id ORDER BY v.id"
    ),
    "pecas": (
        "SELECT p.id, p.nome, c.nome AS categoria, p.preco FROM pecas p "
        "LEFT JOIN categorias_peca c ON c.id = p.categoria_id ORDER BY p.id"
    ),
    "estoque_veiculos": (
        "SELECT ev.veiculo_id, v.marca, v.chassi, ev.quantidade FROM estoque_veiculos ev "
        "JOIN veiculos v ON v.id = ev.veiculo_id ORDER BY ev.veiculo_id"
    ),
    "estoque_pecas": (
        "SELECT ep.peca_id, p.nome, ep.quantidade FROM estoque_pecas ep "
        "JOIN pecas p ON p.id = ep.peca_id ORDER BY ep.peca_id"
    ),
    "vendas": "SELECT id, data, tipo, total FROM vendas ORDER BY id",
    "ordens_servico": (
        "SELECT id, cliente_id, veiculo_cliente_id, tipo_servico, entrada, saida, "
        "valor_mao_de_obra, valor_peca FROM ordem_servico ORDER BY id"
    ),
}


class RelatorioService:
    def __init__(self, connection, dest_dir=None):
        self.connection = connection
        self.dest_dir = Path(dest_dir) if dest_dir else Path(__file__).parent.parent / "relatorios"

    def listar_disponiveis(self) -> list:
        return sorted(RELATORIOS.keys())

    def gerar(self, nome) -> dict:
        if nome not in RELATORIOS:
            raise ValueError(f"Relatório desconhecido: {nome}. Disponíveis: {self.listar_disponiveis()}")
        cur = self.connection.cursor()
        cur.execute(RELATORIOS[nome])
        rows = cur.fetchall()
        headers = [d[0] for d in cur.description]
        linhas = [dict(r) for r in rows]
        return {"nome": nome, "headers": headers, "linhas": linhas}

    def exportar_csv(self, nome, caminho=None) -> str:
        rel = self.gerar(nome)
        if caminho is None:
            self.dest_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            caminho = self.dest_dir / f"{nome}-{ts}.csv"
        caminho = Path(caminho)
        # Excel pt-BR usa ';' como separador de listas e ',' como decimal; o BOM
        # (utf-8-sig) garante que os acentos abram corretamente.
        with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(rel["headers"])
            for linha in rel["linhas"]:
                writer.writerow([self._fmt_csv(linha.get(h)) for h in rel["headers"]])
        return str(caminho)

    @staticmethod
    def _fmt_csv(valor):
        if valor is None:
            return ""
        if isinstance(valor, float):
            return str(valor).replace(".", ",")
        # CPF, telefone etc. são strings de dígitos: força texto no Excel
        # (="...") p/ evitar notação científica e preservar zeros à esquerda.
        # `id` e demais inteiros chegam como int e seguem como número.
        if isinstance(valor, str) and valor.isdigit():
            return f'="{valor}"'
        return valor

    def formatar_console(self, nome) -> str:
        rel = self.gerar(nome)
        headers = rel["headers"]
        linhas = rel["linhas"]
        larguras = {h: len(h) for h in headers}
        for linha in linhas:
            for h in headers:
                larguras[h] = max(larguras[h], len(str(linha.get(h, ""))))
        sep = " | "
        cab = sep.join(h.ljust(larguras[h]) for h in headers)
        traco = "-+-".join("-" * larguras[h] for h in headers)
        corpo = [
            sep.join(str(linha.get(h, "")).ljust(larguras[h]) for h in headers)
            for linha in linhas
        ]
        titulo = f"Relatório: {nome} ({len(linhas)} registro(s))"
        return "\n".join([titulo, cab, traco, *corpo]) if linhas else f"{titulo}\n(sem registros)"
