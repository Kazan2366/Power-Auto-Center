class Veiculo:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, marca_id, modelo_id, chassi, ano_fabricacao, cor, preco):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO veiculos (marca_id, modelo_id, chassi, ano_fabricacao, cor, preco) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (marca_id, modelo_id, chassi, ano_fabricacao, cor, preco),
        )
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT v.*, mc.nome AS marca_nome, m.nome AS modelo_nome "
            "FROM veiculos v "
            "LEFT JOIN marcas mc ON mc.id = v.marca_id "
            "LEFT JOIN modelos m ON m.id = v.modelo_id "
            "ORDER BY v.id"
        )
        return cur.fetchall()

    def buscar(self, veiculo_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM veiculos WHERE id = ?", (veiculo_id,))
        return cur.fetchone()

    def atualizar(self, veiculo_id, marca_id, modelo_id, chassi, ano_fabricacao, cor, preco):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE veiculos SET marca_id = ?, modelo_id = ?, chassi = ?, "
            "ano_fabricacao = ?, cor = ?, preco = ? WHERE id = ?",
            (marca_id, modelo_id, chassi, ano_fabricacao, cor, preco, veiculo_id),
        )
        self.connection.commit()

    def excluir(self, veiculo_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM veiculos WHERE id = ?", (veiculo_id,))
        self.connection.commit()
