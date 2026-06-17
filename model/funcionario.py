class Funcionario:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, nome, cargo, cpf, telefone, email, salario, data_admissao):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO funcionarios "
            "(nome, cargo, cpf, telefone, email, salario, data_admissao) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (nome, cargo, cpf, telefone, email, salario, data_admissao),
        )
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM funcionarios ORDER BY id")
        return cur.fetchall()

    def buscar(self, funcionario_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM funcionarios WHERE id = ?", (funcionario_id,))
        return cur.fetchone()

    def atualizar(self, funcionario_id, nome, cargo, cpf, telefone, email, salario, data_admissao):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE funcionarios SET nome = ?, cargo = ?, cpf = ?, telefone = ?, "
            "email = ?, salario = ?, data_admissao = ? WHERE id = ?",
            (nome, cargo, cpf, telefone, email, salario, data_admissao, funcionario_id),
        )
        self.connection.commit()

    def total_salarios(self):
        cur = self.connection.cursor()
        cur.execute("SELECT COALESCE(SUM(salario), 0) AS total FROM funcionarios")
        return cur.fetchone()["total"]

    def excluir(self, funcionario_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM funcionarios WHERE id = ?", (funcionario_id,))
        self.connection.commit()
