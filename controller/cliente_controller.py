from controller.common import duplicidade_amigavel
from model.cliente import Cliente
from utils.helpers import validate_cpf, validate_email


class ClienteController:
    def __init__(self, connection):
        self.model = Cliente(connection)

    def _validar(self, nome, cpf, email):
        if not (nome or "").strip():
            raise ValueError("Nome é obrigatório.")
        if not (cpf or "").strip():
            raise ValueError("CPF é obrigatório.")
        if not validate_cpf(cpf):
            raise ValueError("CPF deve conter 11 dígitos.")
        if email and not validate_email(email):
            raise ValueError("E-mail inválido.")

    @staticmethod
    def _normalizar_cpf(cpf):
        return "".join(filter(str.isdigit, cpf or ""))

    def cadastrar(self, nome, cpf, telefone, email):
        self._validar(nome, cpf, email)
        cpf = self._normalizar_cpf(cpf)
        with duplicidade_amigavel("CPF", cpf):
            return self.model.criar(nome.strip(), cpf, telefone, email)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, cliente_id):
        row = self.model.buscar(cliente_id)
        return dict(row) if row else None

    def atualizar(self, cliente_id, nome, cpf, telefone, email):
        self._validar(nome, cpf, email)
        cpf = self._normalizar_cpf(cpf)
        with duplicidade_amigavel("CPF", cpf):
            self.model.atualizar(cliente_id, nome.strip(), cpf, telefone, email)

    def excluir(self, cliente_id):
        self.model.excluir(cliente_id)
