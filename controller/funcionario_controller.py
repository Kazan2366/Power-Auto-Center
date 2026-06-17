from model.funcionario import Funcionario


class FuncionarioController:
    def __init__(self, connection):
        self.model = Funcionario(connection)

    def _validar(self, nome, salario):
        if not (nome or "").strip():
            raise ValueError("Nome do funcionário é obrigatório.")
        if salario is not None and salario < 0:
            raise ValueError("Salário não pode ser negativo.")

    def cadastrar(self, nome, cargo=None, cpf=None, telefone=None, email=None,
                  salario=None, data_admissao=None):
        self._validar(nome, salario)
        return self.model.criar(
            nome.strip(), cargo, (cpf or "").strip() or None,
            telefone, email, salario, data_admissao,
        )

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, funcionario_id):
        row = self.model.buscar(funcionario_id)
        return dict(row) if row else None

    def atualizar(self, funcionario_id, nome, cargo=None, cpf=None, telefone=None,
                  email=None, salario=None, data_admissao=None):
        self._validar(nome, salario)
        self.model.atualizar(
            funcionario_id, nome.strip(), cargo, (cpf or "").strip() or None,
            telefone, email, salario, data_admissao,
        )

    def total_salarios(self):
        return self.model.total_salarios()

    def excluir(self, funcionario_id):
        self.model.excluir(funcionario_id)
