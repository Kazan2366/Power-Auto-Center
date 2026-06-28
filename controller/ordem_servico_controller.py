from model.ordem_servico import OrdemServico


class OrdemServicoController:
    def __init__(self, connection):
        self.model = OrdemServico(connection)

    def _validar(self, cliente_id, veiculo_cliente_id, valor_mao_de_obra, valor_peca):
        if not cliente_id:
            raise ValueError("Cliente e obrigatorio.")
        if not veiculo_cliente_id:
            raise ValueError("Veiculo do cliente e obrigatorio.")
        if valor_mao_de_obra is not None and valor_mao_de_obra < 0:
            raise ValueError("Valor de mao de obra nao pode ser negativo.")
        if valor_peca is not None and valor_peca < 0:
            raise ValueError("Valor de peca nao pode ser negativo.")

    def cadastrar(self, cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca):
        self._validar(cliente_id, veiculo_cliente_id, valor_mao_de_obra, valor_peca)
        return self.model.criar(
            cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca
        )

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, os_id):
        row = self.model.buscar(os_id)
        return dict(row) if row else None

    def atualizar(self, os_id, cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca):
        self._validar(cliente_id, veiculo_cliente_id, valor_mao_de_obra, valor_peca)
        self.model.atualizar(
            os_id, cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca
        )

    def fechar(self, os_id):
        os = self.buscar(os_id)
        if os is None:
            raise ValueError("Ordem de serviço não encontrada.")
        if os.get("saida"):
            raise ValueError("OS já está fechada.")
        if not self.model.fechar(os_id):
            raise ValueError("OS já está fechada.")

    def total_abertas(self):
        return self.model.total_abertas()

    def excluir(self, os_id):
        self.model.excluir(os_id)
