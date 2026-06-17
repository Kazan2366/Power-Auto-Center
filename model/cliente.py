class Cliente:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, nome, cpf, telefone, email):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO clientes (nome, cpf, telefone, email) VALUES (?, ?, ?, ?)",
            (nome, cpf, telefone, email),
        )
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM clientes ORDER BY id")
        return cur.fetchall()

    def buscar(self, cliente_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        return cur.fetchone()

    def atualizar(self, cliente_id, nome, cpf, telefone, email):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE clientes SET nome = ?, cpf = ?, telefone = ?, email = ? WHERE id = ?",
            (nome, cpf, telefone, email, cliente_id),
        )
        self.connection.commit()

    def excluir(self, cliente_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        self.connection.commit()
