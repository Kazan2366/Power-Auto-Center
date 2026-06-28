class OrdemServico:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO ordem_servico "
            "(cliente_id, veiculo_cliente_id, tipo_servico, entrada, saida, "
            "valor_mao_de_obra, valor_peca) "
            "VALUES (?, ?, ?, CURRENT_TIMESTAMP, NULL, ?, ?)",
            (cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca),
        )
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM ordem_servico ORDER BY id")
        return cur.fetchall()

    def buscar(self, os_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM ordem_servico WHERE id = ?", (os_id,))
        return cur.fetchone()

    def atualizar(self, os_id, cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE ordem_servico SET cliente_id = ?, veiculo_cliente_id = ?, "
            "tipo_servico = ?, valor_mao_de_obra = ?, valor_peca = ? WHERE id = ?",
            (cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca, os_id),
        )
        self.connection.commit()

    def fechar(self, os_id):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE ordem_servico SET saida = CURRENT_TIMESTAMP "
            "WHERE id = ? AND saida IS NULL",
            (os_id,),
        )
        self.connection.commit()
        return cur.rowcount == 1

    def total_abertas(self):
        cur = self.connection.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM ordem_servico WHERE saida IS NULL")
        return cur.fetchone()["total"]

    def excluir(self, os_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM ordem_servico WHERE id = ?", (os_id,))
        self.connection.commit()
