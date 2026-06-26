from model.estoque import Estoque


class EstoqueController:
    def __init__(self, connection):
        self.model = Estoque(connection)

    def _validar_qtd(self, quantidade):
        if quantidade is None or quantidade < 0:
            raise ValueError("Quantidade não pode ser negativa.")

    def definir_veiculo(self, modelo_id, quantidade):
        self._validar_qtd(quantidade)
        self.model.definir_veiculo(modelo_id, quantidade)

    def definir_peca(self, peca_id, quantidade):
        self._validar_qtd(quantidade)
        self.model.definir_peca(peca_id, quantidade)

    def buscar_veiculo(self, modelo_id):
        row = self.model.buscar_veiculo(modelo_id)
        return dict(row) if row else None

    def buscar_peca(self, peca_id):
        row = self.model.buscar_peca(peca_id)
        return dict(row) if row else None

    def listar_veiculos(self):
        return [dict(r) for r in self.model.listar_veiculos()]

    def listar_pecas(self):
        return [dict(r) for r in self.model.listar_pecas()]

    def total_veiculos(self):
        return self.model.total_veiculos()

    def total_pecas(self):
        return self.model.total_pecas()
