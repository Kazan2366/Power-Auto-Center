from model.cliente import Cliente


class ClienteController:
    def __init__(self, connection):
        self.model = Cliente(connection)

    def cadastrar(self, nome, cpf, telefone, email):
        if not (nome or "").strip():
            raise ValueError("Nome é obrigatório.")
        if not (cpf or "").strip():
            raise ValueError("CPF é obrigatório.")
        return self.model.criar(nome.strip(), cpf.strip(), telefone, email)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, cliente_id):
        row = self.model.buscar(cliente_id)
        return dict(row) if row else None

    def atualizar(self, cliente_id, nome, cpf, telefone, email):
        if not (nome or "").strip():
            raise ValueError("Nome é obrigatório.")
        if not (cpf or "").strip():
            raise ValueError("CPF é obrigatório.")
        self.model.atualizar(cliente_id, nome.strip(), cpf.strip(), telefone, email)

    def excluir(self, cliente_id):
        self.model.excluir(cliente_id)
