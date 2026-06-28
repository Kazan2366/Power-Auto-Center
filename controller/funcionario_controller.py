from controller.common import duplicidade_amigavel
from model.funcionario import Funcionario
from utils.helpers import validate_cpf, validate_email


class FuncionarioController:
    def __init__(self, connection):
        self.model = Funcionario(connection)

    def _validar(self, nome, cpf, email, salario):
        if not (nome or "").strip():
            raise ValueError("Nome do funcionário é obrigatório.")
        if cpf and not validate_cpf(cpf):
            raise ValueError("CPF deve conter 11 dígitos.")
        if email and not validate_email(email):
            raise ValueError("E-mail inválido.")
        if salario is not None and salario < 0:
            raise ValueError("Salário não pode ser negativo.")

    @staticmethod
    def _normalizar_cpf(cpf):
        return "".join(filter(str.isdigit, cpf or "")) or None

    def cadastrar(self, nome, cargo=None, cpf=None, telefone=None, email=None,
                  salario=None, data_admissao=None):
        self._validar(nome, cpf, email, salario)
        cpf = self._normalizar_cpf(cpf)
        with duplicidade_amigavel("CPF", cpf):
            return self.model.criar(
                nome.strip(), cargo, cpf, telefone, email, salario, data_admissao,
            )

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, funcionario_id):
        row = self.model.buscar(funcionario_id)
        return dict(row) if row else None

    def atualizar(self, funcionario_id, nome, cargo=None, cpf=None, telefone=None,
                  email=None, salario=None, data_admissao=None):
        self._validar(nome, cpf, email, salario)
        cpf = self._normalizar_cpf(cpf)
        with duplicidade_amigavel("CPF", cpf):
            self.model.atualizar(
                funcionario_id, nome.strip(), cargo, cpf,
                telefone, email, salario, data_admissao,
            )

    def total_salarios(self):
        return self.model.total_salarios()

    def excluir(self, funcionario_id):
        self.model.excluir(funcionario_id)
