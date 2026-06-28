from model.venda import Venda

TIPOS_VENDA = ("veiculo", "peca", "mista")
TIPOS_PRODUTO = ("veiculo", "peca")


class VendaController:
    def __init__(self, connection):
        self.model = Venda(connection)

    def registrar_venda(self, tipo, itens):
        if tipo not in TIPOS_VENDA:
            raise ValueError(f"Tipo de venda invalido. Use um de: {', '.join(TIPOS_VENDA)}.")
        if not itens:
            raise ValueError("A venda deve ter ao menos um item.")
        total = 0.0
        for i in itens:
            if i.get("tipo_produto") not in TIPOS_PRODUTO:
                raise ValueError(f"Tipo de produto invalido. Use um de: {', '.join(TIPOS_PRODUTO)}.")
            if i["quantidade"] <= 0:
                raise ValueError("Quantidade do item deve ser maior que zero.")
            if i["preco_unitario"] < 0:
                raise ValueError("Preço unitário não pode ser negativo.")
            total += i["quantidade"] * i["preco_unitario"]
        return self.model.registrar(tipo, itens, total)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, venda_id):
        row = self.model.buscar(venda_id)
        return dict(row) if row else None

    def listar_itens(self, venda_id):
        return [dict(r) for r in self.model.listar_itens(venda_id)]

    def total_vendas(self):
        return self.model.total_vendas()

    def excluir(self, venda_id):
        self.model.excluir(venda_id)
