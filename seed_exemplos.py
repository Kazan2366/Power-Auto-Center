"""Popula o banco com 3 exemplos de cada cadastro (idempotente por unicidade).

Uso: python seed_exemplos.py
Respeita as dependências: marcas/modelos → veículos · categorias → peças.
Registros já existentes (CPF/chassi/username/etc. duplicados) são ignorados.
"""
import sqlite3

from backend import Backend


def _tentar(rotulo, fn):
    """Executa fn() ignorando duplicidade; retorna o id criado ou None."""
    try:
        return fn()
    except sqlite3.IntegrityError:
        print(f"  · {rotulo}: já existe (ignorado)")
    except ValueError as exc:
        print(f"  · {rotulo}: inválido ({exc})")
    return None


def _id_por_nome(lista, nome, chave="nome"):
    return next((r["id"] for r in lista if r.get(chave) == nome), None)


def seed(b: Backend):
    # --- Marcas ---
    print("Marcas:")
    for nome in ("Fiat", "Volkswagen", "Toyota"):
        _tentar(nome, lambda n=nome: b.marcas.cadastrar(n))
    marcas = b.marcas.listar()

    # --- Modelos (apoio para veículos) ---
    print("Modelos:")
    modelos_def = [
        ("Uno", "SN-0001", "Fiat"),
        ("Gol", "SN-0002", "Volkswagen"),
        ("Corolla", "SN-0003", "Toyota"),
    ]
    for nome, serie, marca in modelos_def:
        mid = _id_por_nome(marcas, marca)
        _tentar(nome, lambda n=nome, s=serie, m=mid: b.modelos.cadastrar(n, s, marca_id=m))
    modelos = b.modelos.listar()

    # --- Categorias (sem unicidade no schema → evita duplicar por nome) ---
    print("Categorias:")
    categorias_def = [
        ("Freios", "Pastilhas, discos e fluidos"),
        ("Motor", "Óleos, filtros e correias"),
        ("Suspensão", "Amortecedores e molas"),
    ]
    categorias = b.categorias.listar()
    for nome, desc in categorias_def:
        if _id_por_nome(categorias, nome):
            print(f"  · {nome}: já existe (ignorado)")
            continue
        _tentar(nome, lambda n=nome, d=desc: b.categorias.cadastrar(n, d))
    categorias = b.categorias.listar()

    # --- Peças (sem unicidade no schema → evita duplicar por nome) ---
    print("Peças:")
    pecas_def = [
        ("Pastilha de freio", "Freios", 120.0),
        ("Filtro de óleo", "Motor", 45.0),
        ("Amortecedor dianteiro", "Suspensão", 320.0),
    ]
    pecas_existentes = b.pecas.listar()
    for nome, cat, preco in pecas_def:
        if _id_por_nome(pecas_existentes, nome):
            print(f"  · {nome}: já existe (ignorado)")
            continue
        cid = _id_por_nome(categorias, cat)
        _tentar(nome, lambda n=nome, c=cid, p=preco: b.pecas.cadastrar(n, c, p))

    # --- Veículos (catálogo) ---
    print("Veículos:")
    veiculos_def = [
        ("Fiat", "Uno", "9BWZZZ377VT004251", 2022, "Preto", 65000.0),
        ("Volkswagen", "Gol", "9BWAB45U7KP123456", 2023, "Branco", 78000.0),
        ("Toyota", "Corolla", "9BR53ZEC4P9012345", 2024, "Prata", 145000.0),
    ]
    for marca, modelo, chassi, ano, cor, preco in veiculos_def:
        mid = _id_por_nome(marcas, marca)
        moid = _id_por_nome(modelos, modelo)
        _tentar(chassi, lambda mi=mid, mo=moid, ch=chassi, a=ano, c=cor, p=preco:
                b.veiculos.cadastrar(mi, mo, ch, a, c, p))

    # --- Clientes ---
    print("Clientes:")
    clientes_def = [
        ("Ana Maria Souza", "11122233344", "11999990001", "ana@email.com"),
        ("Bruno Carvalho", "22233344455", "11999990002", "bruno@email.com"),
        ("Carla Mendes", "33344455566", "11999990003", "carla@email.com"),
    ]
    for nome, cpf, tel, email in clientes_def:
        _tentar(nome, lambda n=nome, c=cpf, t=tel, e=email: b.clientes.cadastrar(n, c, t, e))

    # --- Funcionários ---
    print("Funcionários:")
    funcionarios_def = [
        ("Carlos Pereira", "Mecânico", "44455566677", "11988880001", "carlos@conc.com", 3200.0, "2026-01-10"),
        ("Daniela Lima", "Vendedora", "55566677788", "11988880002", "daniela@conc.com", 2800.0, "2026-02-15"),
        ("Eduardo Rocha", "Gerente", "66677788899", "11988880003", "eduardo@conc.com", 6500.0, "2025-11-01"),
    ]
    for nome, cargo, cpf, tel, email, sal, adm in funcionarios_def:
        _tentar(nome, lambda n=nome, ca=cargo, c=cpf, t=tel, e=email, s=sal, d=adm:
                b.funcionarios.cadastrar(n, cargo=ca, cpf=c, telefone=t, email=e,
                                         salario=s, data_admissao=d))

    # --- Usuários (além dos 3 usuários-semente) ---
    print("Usuários:")
    usuarios_def = [
        ("operador.cadastro", "senha123", "cadastro"),
        ("operador.vendas", "senha123", "vendas"),
        ("operador.admin", "senha123", "admin"),
    ]
    for user, senha, role in usuarios_def:
        _tentar(user, lambda u=user, s=senha, r=role: b.usuarios.cadastrar(u, s, r))

    # --- Estoque (UPSERT por produto: define a quantidade) ---
    print("Estoque:")
    veiculos = b.veiculos.listar()
    pecas = b.pecas.listar()
    for qtd, v in zip((4, 7, 2), veiculos):
        _tentar(f"veiculo {v['id']}", lambda i=v["id"], q=qtd: b.estoque.definir_veiculo(i, q))
    for qtd, p in zip((50, 80, 30), pecas):
        _tentar(f"peca {p['id']}", lambda i=p["id"], q=qtd: b.estoque.definir_peca(i, q))

    # --- Veículos de clientes (necessários para Ordens de Serviço) ---
    print("Veículos de clientes:")
    clientes = b.clientes.listar()
    vc_def = [
        ("Fiat", "ABC1D23", 2019),
        ("Volkswagen", "DEF4G56", 2021),
        ("Toyota", "GHI7J89", 2020),
    ]
    for (marca, placa, ano), cli in zip(vc_def, clientes):
        _tentar(placa, lambda c=cli["id"], m=marca, pl=placa, a=ano:
                b.veiculos_cliente.cadastrar(c, m, pl, a))
    veic_clientes = b.veiculos_cliente.listar()

    # --- Vendas (sem unicidade: só semeia se ainda não houver vendas) ---
    print("Vendas:")
    if b.vendas.listar():
        print("  · já existem vendas (ignorado)")
    elif veiculos and pecas:
        vendas_def = [
            ("veiculo", [{"produto_id": veiculos[0]["id"], "tipo_produto": "veiculo",
                          "quantidade": 1, "preco_unitario": veiculos[0]["preco"]}]),
            ("peca", [{"produto_id": pecas[0]["id"], "tipo_produto": "peca",
                       "quantidade": 4, "preco_unitario": pecas[0]["preco"]}]),
            ("mista", [{"produto_id": veiculos[1]["id"], "tipo_produto": "veiculo",
                        "quantidade": 1, "preco_unitario": veiculos[1]["preco"]},
                       {"produto_id": pecas[1]["id"], "tipo_produto": "peca",
                        "quantidade": 2, "preco_unitario": pecas[1]["preco"]}]),
        ]
        for tipo, itens in vendas_def:
            _tentar(f"venda {tipo}", lambda t=tipo, it=itens: b.vendas.registrar_venda(t, it))

    # --- Ordens de serviço (sem unicidade: só semeia se ainda não houver OS) ---
    print("Ordens de serviço:")
    if b.ordens_servico.listar():
        print("  · já existem ordens (ignorado)")
    elif clientes and veic_clientes:
        os_def = [
            ("Revisão completa", 250.0, 180.0),
            ("Troca de óleo e filtro", 80.0, 90.0),
            ("Alinhamento e balanceamento", 120.0, 0.0),
        ]
        for (servico, mao, peca), cli, vc in zip(os_def, clientes, veic_clientes):
            _tentar(servico, lambda c=cli["id"], v=vc["id"], s=servico, m=mao, p=peca:
                    b.ordens_servico.cadastrar(c, v, s, m, p))


def main():
    b = Backend()
    print("Cadastrando 3 exemplos por funcionalidade...\n")
    seed(b)
    print("\nResumo após o seed:")
    for chave, valor in b.dashboard.resumo().items():
        print(f"  - {chave}: {valor}")
    b.fechar()
    print("\nConcluído.")


if __name__ == "__main__":
    main()
