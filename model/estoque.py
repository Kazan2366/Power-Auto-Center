class Estoque:
    def __init__(self, connection):
        self.connection = connection

    def definir_veiculo(self, veiculo_id, quantidade):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO estoque_veiculos (veiculo_id, quantidade) VALUES (?, ?) "
            "ON CONFLICT(veiculo_id) DO UPDATE SET quantidade = excluded.quantidade",
            (veiculo_id, quantidade),
        )
        self.connection.commit()

    def definir_peca(self, peca_id, quantidade):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO estoque_pecas (peca_id, quantidade) VALUES (?, ?) "
            "ON CONFLICT(peca_id) DO UPDATE SET quantidade = excluded.quantidade",
            (peca_id, quantidade),
        )
        self.connection.commit()

    def buscar_veiculo(self, veiculo_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM estoque_veiculos WHERE veiculo_id = ?", (veiculo_id,))
        return cur.fetchone()

    def buscar_peca(self, peca_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM estoque_pecas WHERE peca_id = ?", (peca_id,))
        return cur.fetchone()

    def listar_veiculos(self):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT ev.veiculo_id, ev.quantidade, mc.nome AS marca, v.chassi "
            "FROM estoque_veiculos ev JOIN veiculos v ON v.id = ev.veiculo_id "
            "LEFT JOIN marcas mc ON mc.id = v.marca_id "
            "ORDER BY ev.veiculo_id"
        )
        return cur.fetchall()

    def listar_pecas(self):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT ep.peca_id, ep.quantidade, p.nome "
            "FROM estoque_pecas ep JOIN pecas p ON p.id = ep.peca_id "
            "ORDER BY ep.peca_id"
        )
        return cur.fetchall()

    def total_veiculos(self):
        cur = self.connection.cursor()
        cur.execute("SELECT COALESCE(SUM(quantidade), 0) AS total FROM estoque_veiculos")
        return cur.fetchone()["total"]

    def total_pecas(self):
        cur = self.connection.cursor()
        cur.execute("SELECT COALESCE(SUM(quantidade), 0) AS total FROM estoque_pecas")
        return cur.fetchone()["total"]
