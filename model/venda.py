class Venda:
    # tipo_produto -> (tabela de estoque, coluna-chave)
    _ESTOQUE_REF = {
        "veiculo": ("estoque_veiculos", "veiculo_id"),
        "peca": ("estoque_pecas", "peca_id"),
    }

    def __init__(self, connection):
        self.connection = connection

    def registrar(self, tipo, itens, total):
        """Insere a venda e seus itens numa transação, baixando o estoque.

        A baixa de estoque só ocorre para produtos com estoque controlado (que
        possuem registro em ``estoque_veiculos``/``estoque_pecas``). Para esses,
        valida a disponibilidade antes de gravar e levanta ``ValueError`` se
        faltar saldo — tudo dentro da mesma transação (atômico).
        """
        cur = self.connection.cursor()
        try:
            # 1) Valida disponibilidade (apenas produtos com estoque controlado)
            for i in itens:
                ref = self._ESTOQUE_REF.get(i["tipo_produto"])
                if ref is None:
                    continue
                tabela, coluna = ref
                cur.execute(
                    f"SELECT quantidade FROM {tabela} WHERE {coluna} = ?",
                    (i["produto_id"],),
                )
                row = cur.fetchone()
                if row is not None and row["quantidade"] < i["quantidade"]:
                    raise ValueError(
                        f"Estoque insuficiente (disponível: {row['quantidade']}, "
                        f"solicitado: {i['quantidade']})."
                    )

            # 2) Grava a venda e seus itens
            cur.execute("INSERT INTO vendas (tipo, total) VALUES (?, ?)", (tipo, total))
            venda_id = cur.lastrowid
            cur.executemany(
                "INSERT INTO venda_itens "
                "(venda_id, produto_id, tipo_produto, quantidade, preco_unitario) "
                "VALUES (?, ?, ?, ?, ?)",
                [
                    (venda_id, i["produto_id"], i["tipo_produto"], i["quantidade"], i["preco_unitario"])
                    for i in itens
                ],
            )

            # 3) Baixa o estoque dos produtos controlados
            for i in itens:
                ref = self._ESTOQUE_REF.get(i["tipo_produto"])
                if ref is None:
                    continue
                tabela, coluna = ref
                cur.execute(
                    f"UPDATE {tabela} SET quantidade = quantidade - ? WHERE {coluna} = ?",
                    (i["quantidade"], i["produto_id"]),
                )

            self.connection.commit()
            return venda_id
        except Exception:
            self.connection.rollback()
            raise

    def listar(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM vendas ORDER BY id")
        return cur.fetchall()

    def buscar(self, venda_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM vendas WHERE id = ?", (venda_id,))
        return cur.fetchone()

    def listar_itens(self, venda_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM venda_itens WHERE venda_id = ? ORDER BY id", (venda_id,))
        return cur.fetchall()

    def total_vendas(self):
        cur = self.connection.cursor()
        cur.execute("SELECT COALESCE(SUM(total), 0) AS total FROM vendas")
        return cur.fetchone()["total"]

    def excluir(self, venda_id):
        """Exclui a venda e devolve ao estoque os itens com estoque controlado."""
        cur = self.connection.cursor()
        try:
            cur.execute(
                "SELECT produto_id, tipo_produto, quantidade FROM venda_itens "
                "WHERE venda_id = ?",
                (venda_id,),
            )
            for item in cur.fetchall():
                ref = self._ESTOQUE_REF.get(item["tipo_produto"])
                if ref is None:
                    continue
                tabela, coluna = ref
                cur.execute(
                    f"UPDATE {tabela} SET quantidade = quantidade + ? WHERE {coluna} = ?",
                    (item["quantidade"], item["produto_id"]),
                )
            cur.execute("DELETE FROM venda_itens WHERE venda_id = ?", (venda_id,))
            cur.execute("DELETE FROM vendas WHERE id = ?", (venda_id,))
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
