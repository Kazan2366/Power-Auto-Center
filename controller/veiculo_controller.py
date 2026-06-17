from model.veiculo import Veiculo


class VeiculoController:
    def __init__(self, connection):
        self.model = Veiculo(connection)

    def _validar(self, marca_id, preco):
        if not marca_id:
            raise ValueError("Marca é obrigatória.")
        if preco is not None and preco < 0:
            raise ValueError("Preço não pode ser negativo.")

    def cadastrar(self, marca_id, modelo_id, chassi, ano_fabricacao, cor, preco):
        self._validar(marca_id, preco)
        return self.model.criar(marca_id, modelo_id, chassi, ano_fabricacao, cor, preco)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, veiculo_id):
        row = self.model.buscar(veiculo_id)
        return dict(row) if row else None

    def atualizar(self, veiculo_id, marca_id, modelo_id, chassi, ano_fabricacao, cor, preco):
        self._validar(marca_id, preco)
        self.model.atualizar(veiculo_id, marca_id, modelo_id, chassi, ano_fabricacao, cor, preco)

    def excluir(self, veiculo_id):
        self.model.excluir(veiculo_id)
