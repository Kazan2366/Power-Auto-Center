from controller.common import duplicidade_amigavel
from model.marca import Marca


class MarcaController:
    def __init__(self, connection):
        self.model = Marca(connection)

    def cadastrar(self, nome):
        if not (nome or "").strip():
            raise ValueError("Nome da marca é obrigatório.")
        nome = nome.strip()
        with duplicidade_amigavel("nome da marca", nome):
            return self.model.criar(nome)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, marca_id):
        row = self.model.buscar(marca_id)
        return dict(row) if row else None

    def atualizar(self, marca_id, nome):
        if not (nome or "").strip():
            raise ValueError("Nome da marca é obrigatório.")
        nome = nome.strip()
        with duplicidade_amigavel("nome da marca", nome):
            self.model.atualizar(marca_id, nome)

    def excluir(self, marca_id):
        self.model.excluir(marca_id)
