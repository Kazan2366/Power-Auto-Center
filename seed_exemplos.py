"""Popula o banco com dados de demonstração realistas e idempotentes."""
import contextlib
import io
import sqlite3

from backend import Backend
from database.dados_exemplo import (
    CATEGORIAS,
    CLIENTES,
    ESTOQUE_PECAS,
    ESTOQUE_VEICULOS,
    FUNCIONARIOS,
    MARCAS,
    MODELOS,
    ORDENS_SERVICO,
    PECAS,
    VEICULOS,
    VEICULOS_CLIENTE,
    VENDAS,
)


def _tentar(rotulo, fn):
    """Executa fn() ignorando duplicidade; retorna o id criado ou None."""
    try:
        return fn()
    except sqlite3.IntegrityError:
        print(f"  · {rotulo}: já existe (ignorado)")
    except ValueError as exc:
        if str(exc).startswith("Já existe"):
            print(f"  · {rotulo}: já existe (ignorado)")
        else:
            print(f"  · {rotulo}: inválido ({exc})")
    return None


def _id_por_nome(lista, nome, chave="nome"):
    return next((r["id"] for r in lista if r.get(chave) == nome), None)


def _por_nome(lista, chave="nome"):
    return {r[chave]: r for r in lista}


def _itens_venda(itens_def, modelos_por_nome, pecas_por_nome):
    itens = []
    for item in itens_def:
        if item["tipo_produto"] == "veiculo":
            produto = modelos_por_nome.get(item["produto"])
        else:
            produto = pecas_por_nome.get(item["produto"])
        if produto is None:
            raise ValueError(f"Produto não encontrado no seed: {item['produto']}")
        itens.append({
            "produto_id": produto["id"],
            "tipo_produto": item["tipo_produto"],
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
        })
    return itens


def seed(b: Backend):
    print("Marcas:")
    for nome in MARCAS:
        _tentar(nome, lambda n=nome: b.marcas.cadastrar(n))
    marcas = b.marcas.listar()

    print("Modelos:")
    for item in MODELOS:
        marca_id = _id_por_nome(marcas, item["marca"])
        _tentar(
            item["nome"],
            lambda i=item, m=marca_id: b.modelos.cadastrar(i["nome"], i["numero_serie"], marca_id=m),
        )
    modelos = b.modelos.listar()

    print("Categorias:")
    categorias = b.categorias.listar()
    for item in CATEGORIAS:
        if _id_por_nome(categorias, item["nome"]):
            print(f"  · {item['nome']}: já existe (ignorado)")
            continue
        _tentar(item["nome"], lambda i=item: b.categorias.cadastrar(i["nome"], i["descricao"]))
    categorias = b.categorias.listar()

    print("Peças:")
    pecas = b.pecas.listar()
    for item in PECAS:
        if _id_por_nome(pecas, item["nome"]):
            print(f"  · {item['nome']}: já existe (ignorado)")
            continue
        categoria_id = _id_por_nome(categorias, item["categoria"])
        _tentar(
            item["nome"],
            lambda i=item, c=categoria_id: b.pecas.cadastrar(i["nome"], c, i["preco"]),
        )
    pecas = b.pecas.listar()

    print("Veículos:")
    for item in VEICULOS:
        marca_id = _id_por_nome(marcas, item["marca"])
        modelo_id = _id_por_nome(modelos, item["modelo"])
        _tentar(
            item["chassi"],
            lambda i=item, ma=marca_id, mo=modelo_id: b.veiculos.cadastrar(
                ma, mo, i["chassi"], i["ano"], i["cor"], i["preco"]
            ),
        )
    veiculos = b.veiculos.listar()

    print("Clientes:")
    for item in CLIENTES:
        _tentar(
            item["nome"],
            lambda i=item: b.clientes.cadastrar(i["nome"], i["cpf"], i["telefone"], i["email"]),
        )
    clientes = b.clientes.listar()

    print("Funcionários:")
    for item in FUNCIONARIOS:
        _tentar(
            item["nome"],
            lambda i=item: b.funcionarios.cadastrar(
                i["nome"],
                cargo=i["cargo"],
                cpf=i["cpf"],
                telefone=i["telefone"],
                email=i["email"],
                salario=i["salario"],
                data_admissao=i["data_admissao"],
            ),
        )

    print("Estoque:")
    modelos = b.modelos.listar()
    pecas = b.pecas.listar()
    modelos_por_nome = _por_nome(modelos)
    pecas_por_nome = _por_nome(pecas)
    for modelo_nome, quantidade in ESTOQUE_VEICULOS.items():
        modelo = modelos_por_nome.get(modelo_nome)
        if modelo:
            _tentar(f"modelo {modelo_nome}", lambda m=modelo, q=quantidade: b.estoque.definir_veiculo(m["id"], q))
    for peca_nome, quantidade in ESTOQUE_PECAS.items():
        peca = pecas_por_nome.get(peca_nome)
        if peca:
            _tentar(f"peça {peca_nome}", lambda p=peca, q=quantidade: b.estoque.definir_peca(p["id"], q))

    print("Veículos de clientes:")
    clientes = b.clientes.listar()
    clientes_por_nome = _por_nome(clientes)
    for item in VEICULOS_CLIENTE:
        cliente = clientes_por_nome.get(item["cliente"])
        if cliente is None:
            raise ValueError(f"Cliente não encontrado no seed: {item['cliente']}")
        _tentar(
            item["placa"],
            lambda i=item, c=cliente: b.veiculos_cliente.cadastrar(c["id"], i["marca"], i["placa"], i["ano"]),
        )
    veiculos_cliente = b.veiculos_cliente.listar()

    print("Vendas:")
    if b.vendas.listar():
        print("  · já existem vendas (ignorado)")
    elif veiculos and pecas:
        modelos_por_nome = _por_nome(b.modelos.listar())
        pecas_por_nome = _por_nome(b.pecas.listar())
        for venda in VENDAS:
            itens = _itens_venda(venda["itens"], modelos_por_nome, pecas_por_nome)
            _tentar(
                f"venda {venda['tipo']}",
                lambda v=venda, it=itens: b.vendas.registrar_venda(v["tipo"], it),
            )

    print("Ordens de serviço:")
    if b.ordens_servico.listar():
        print("  · já existem ordens (ignorado)")
    elif clientes and veiculos_cliente:
        clientes_por_nome = _por_nome(b.clientes.listar())
        veiculos_cliente_por_placa = _por_nome(b.veiculos_cliente.listar(), chave="placa")
        for ordem in ORDENS_SERVICO:
            cliente = clientes_por_nome.get(ordem["cliente"])
            veiculo_cliente = veiculos_cliente_por_placa.get(ordem["placa"])
            if cliente is None or veiculo_cliente is None:
                raise ValueError(f"OS com referência inválida no seed: {ordem}")
            _tentar(
                ordem["servico"],
                lambda o=ordem, c=cliente, v=veiculo_cliente: b.ordens_servico.cadastrar(
                    c["id"],
                    v["id"],
                    o["servico"],
                    o["valor_mao_de_obra"],
                    o["valor_peca"],
                ),
            )


def _banco_sem_exemplos(b: Backend) -> bool:
    """True quando ainda não há dados de demonstração (só os usuários-semente)."""
    return not (b.marcas.listar() or b.clientes.listar()
                or b.funcionarios.listar() or b.veiculos.listar())


def garantir_dados_exemplo(b: Backend, verbose: bool = False) -> bool:
    """Semeia exemplos na 1ª execução; idempotente nas demais."""
    if not _banco_sem_exemplos(b):
        return False
    if verbose:
        seed(b)
    else:
        with contextlib.redirect_stdout(io.StringIO()):
            seed(b)
    return True


def main():
    b = Backend()
    try:
        print("Cadastrando exemplos por funcionalidade...\n")
        seed(b)
        print("\nResumo após o seed:")
        for chave, valor in b.dashboard.resumo().items():
            print(f"  - {chave}: {valor}")
        print("\nConcluído.")
    finally:
        b.fechar()


if __name__ == "__main__":
    main()
