from controller.common import duplicidade_amigavel
from model.modelo import Modelo


class ModeloController:
    def __init__(self, connection):
        self.model = Modelo(connection)

    def cadastrar(self, nome, numero_serie, marca_id=None):
        if not (nome or "").strip():
            raise ValueError("Nome do modelo é obrigatório.")
        numero_serie = (numero_serie or "").strip() or None
        with duplicidade_amigavel("número de série", numero_serie):
            return self.model.criar(nome.strip(), numero_serie, marca_id)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def listar_por_marca(self, marca_id):
        return [dict(r) for r in self.model.listar_por_marca(marca_id)]

    def buscar(self, modelo_id):
        row = self.model.buscar(modelo_id)
        return dict(row) if row else None

    def atualizar(self, modelo_id, nome, numero_serie, marca_id=None):
        if not (nome or "").strip():
            raise ValueError("Nome do modelo é obrigatório.")
        numero_serie = (numero_serie or "").strip() or None
        with duplicidade_amigavel("número de série", numero_serie):
            self.model.atualizar(modelo_id, nome.strip(), numero_serie, marca_id)

    def excluir(self, modelo_id):
        self.model.excluir(modelo_id)
