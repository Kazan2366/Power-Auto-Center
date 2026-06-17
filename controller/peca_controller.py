from model.peca import Peca


class PecaController:
    def __init__(self, connection):
        self.model = Peca(connection)

    def _validar(self, nome, preco):
        if not (nome or "").strip():
            raise ValueError("Nome da peça é obrigatório.")
        if preco is not None and preco < 0:
            raise ValueError("Preço não pode ser negativo.")

    def cadastrar(self, nome, categoria_id, preco):
        self._validar(nome, preco)
        return self.model.criar(nome.strip(), categoria_id, preco)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, peca_id):
        row = self.model.buscar(peca_id)
        return dict(row) if row else None

    def atualizar(self, peca_id, nome, categoria_id, preco):
        self._validar(nome, preco)
        self.model.atualizar(peca_id, nome.strip(), categoria_id, preco)

    def excluir(self, peca_id):
        self.model.excluir(peca_id)
