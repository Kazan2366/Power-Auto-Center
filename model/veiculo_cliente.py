class VeiculoCliente:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, cliente_id, marca, placa, ano):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO veiculo_cliente (cliente_id, marca, placa, ano) VALUES (?, ?, ?, ?)",
            (cliente_id, marca, placa, ano),
        )
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM veiculo_cliente ORDER BY id")
        return cur.fetchall()

    def listar_por_cliente(self, cliente_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM veiculo_cliente WHERE cliente_id = ? ORDER BY id", (cliente_id,))
        return cur.fetchall()

    def buscar(self, vc_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM veiculo_cliente WHERE id = ?", (vc_id,))
        return cur.fetchone()

    def atualizar(self, vc_id, cliente_id, marca, placa, ano):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE veiculo_cliente SET cliente_id = ?, marca = ?, placa = ?, ano = ? WHERE id = ?",
            (cliente_id, marca, placa, ano, vc_id),
        )
        self.connection.commit()

    def excluir(self, vc_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM veiculo_cliente WHERE id = ?", (vc_id,))
        self.connection.commit()
