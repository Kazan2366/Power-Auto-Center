from model.categoria_peca import CategoriaPeca


class CategoriaPecaController:
    def __init__(self, connection):
        self.model = CategoriaPeca(connection)

    def cadastrar(self, nome, descricao):
        if not (nome or "").strip():
            raise ValueError("Nome da categoria é obrigatório.")
        return self.model.criar(nome.strip(), descricao)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, categoria_id):
        row = self.model.buscar(categoria_id)
        return dict(row) if row else None

    def atualizar(self, categoria_id, nome, descricao):
        if not (nome or "").strip():
            raise ValueError("Nome da categoria é obrigatório.")
        self.model.atualizar(categoria_id, nome.strip(), descricao)

    def excluir(self, categoria_id):
        self.model.excluir(categoria_id)
