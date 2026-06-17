from model.veiculo_cliente import VeiculoCliente


class VeiculoClienteController:
    def __init__(self, connection):
        self.model = VeiculoCliente(connection)

    def _validar(self, cliente_id, placa):
        if not cliente_id:
            raise ValueError("Cliente é obrigatório.")
        if not (placa or "").strip():
            raise ValueError("Placa é obrigatória.")

    def cadastrar(self, cliente_id, marca, placa, ano):
        self._validar(cliente_id, placa)
        return self.model.criar(cliente_id, marca, placa.strip(), ano)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def listar_por_cliente(self, cliente_id):
        return [dict(r) for r in self.model.listar_por_cliente(cliente_id)]

    def buscar(self, vc_id):
        row = self.model.buscar(vc_id)
        return dict(row) if row else None

    def atualizar(self, vc_id, cliente_id, marca, placa, ano):
        self._validar(cliente_id, placa)
        self.model.atualizar(vc_id, cliente_id, marca, placa.strip(), ano)

    def excluir(self, vc_id):
        self.model.excluir(vc_id)
