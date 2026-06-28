from controller.common import duplicidade_amigavel
from model.veiculo import Veiculo
from utils.helpers import validate_chassi


class VeiculoController:
    def __init__(self, connection):
        self.model = Veiculo(connection)

    def _validar(self, marca_id, chassi, preco):
        if not marca_id:
            raise ValueError("Marca é obrigatória.")
        if chassi and not validate_chassi(chassi):
            raise ValueError("Chassi deve conter 17 caracteres alfanuméricos válidos.")
        if preco is not None and preco < 0:
            raise ValueError("Preço não pode ser negativo.")

    @staticmethod
    def _normalizar_chassi(chassi):
        return "".join(ch for ch in (chassi or "").upper() if ch.isalnum()) or None

    def cadastrar(self, marca_id, modelo_id, chassi, ano_fabricacao, cor, preco):
        self._validar(marca_id, chassi, preco)
        chassi = self._normalizar_chassi(chassi)
        with duplicidade_amigavel("chassi", chassi):
            return self.model.criar(marca_id, modelo_id, chassi, ano_fabricacao, cor, preco)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, veiculo_id):
        row = self.model.buscar(veiculo_id)
        return dict(row) if row else None

    def atualizar(self, veiculo_id, marca_id, modelo_id, chassi, ano_fabricacao, cor, preco):
        self._validar(marca_id, chassi, preco)
        chassi = self._normalizar_chassi(chassi)
        with duplicidade_amigavel("chassi", chassi):
            self.model.atualizar(veiculo_id, marca_id, modelo_id, chassi, ano_fabricacao, cor, preco)

    def excluir(self, veiculo_id):
        self.model.excluir(veiculo_id)
