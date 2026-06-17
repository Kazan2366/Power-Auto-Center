from model.ordem_servico import OrdemServico


class OrdemServicoController:
    def __init__(self, connection):
        self.model = OrdemServico(connection)

    def _validar(self, cliente_id, veiculo_cliente_id):
        if not cliente_id:
            raise ValueError("Cliente é obrigatório.")
        if not veiculo_cliente_id:
            raise ValueError("Veículo do cliente é obrigatório.")

    def cadastrar(self, cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca):
        self._validar(cliente_id, veiculo_cliente_id)
        return self.model.criar(
            cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca
        )

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, os_id):
        row = self.model.buscar(os_id)
        return dict(row) if row else None

    def atualizar(self, os_id, cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca):
        self._validar(cliente_id, veiculo_cliente_id)
        self.model.atualizar(
            os_id, cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca
        )

    def fechar(self, os_id):
        self.model.fechar(os_id)

    def total_abertas(self):
        return self.model.total_abertas()

    def excluir(self, os_id):
        self.model.excluir(os_id)
