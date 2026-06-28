from controller.common import duplicidade_amigavel
from model.veiculo_cliente import VeiculoCliente
from utils.helpers import validate_placa


class VeiculoClienteController:
    def __init__(self, connection):
        self.model = VeiculoCliente(connection)

    def _validar(self, cliente_id, placa):
        if not cliente_id:
            raise ValueError("Cliente é obrigatório.")
        if not (placa or "").strip():
            raise ValueError("Placa é obrigatória.")
        if not validate_placa(placa):
            raise ValueError("Placa deve estar no formato ABC1234 ou ABC1D23.")

    @staticmethod
    def _normalizar_placa(placa):
        return "".join(ch for ch in (placa or "").upper() if ch.isalnum())

    def cadastrar(self, cliente_id, marca, placa, ano):
        self._validar(cliente_id, placa)
        placa = self._normalizar_placa(placa)
        with duplicidade_amigavel("placa", placa):
            return self.model.criar(cliente_id, marca, placa, ano)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def listar_por_cliente(self, cliente_id):
        return [dict(r) for r in self.model.listar_por_cliente(cliente_id)]

    def buscar(self, vc_id):
        row = self.model.buscar(vc_id)
        return dict(row) if row else None

    def atualizar(self, vc_id, cliente_id, marca, placa, ano):
        self._validar(cliente_id, placa)
        placa = self._normalizar_placa(placa)
        with duplicidade_amigavel("placa", placa):
            self.model.atualizar(vc_id, cliente_id, marca, placa, ano)

    def excluir(self, vc_id):
        self.model.excluir(vc_id)
