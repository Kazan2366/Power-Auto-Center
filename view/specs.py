"""Especificações declarativas das telas CRUD.

Cada spec descreve uma entidade para :class:`view.crud_view.CrudView`:
colunas da tabela, campos do formulário e as funções que chamam o controller.
"""


# Fontes para campos do tipo "select" (FK) → list[(id, rótulo)]
def _fonte_marcas(b):
    return [(m["id"], m["nome"]) for m in b.marcas.listar()]


def _fonte_marcas_nome(b):
    # Para colunas que armazenam o nome da marca (texto), não o id.
    return [(m["nome"], m["nome"]) for m in b.marcas.listar()]


def _fonte_modelos(b, marca_id=None):
    if marca_id:
        return [(m["id"], m["nome"]) for m in b.modelos.listar_por_marca(marca_id)]
    return [(m["id"], m["nome"]) for m in b.modelos.listar()]


def _fonte_categorias(b):
    return [(c["id"], c["nome"]) for c in b.categorias.listar()]


def _fonte_clientes(b):
    return [(c["id"], f'{c["nome"]} (CPF {c["cpf"]})') for c in b.clientes.listar()]


def _fonte_veic_cliente(b):
    return [(v["id"], f'{v["marca"]} — {v["placa"]}') for v in b.veiculos_cliente.listar()]


def construir_specs():
    """Retorna o dicionário de specs indexado pela chave da entidade."""
    return {
        "clientes": {
            "titulo": "Clientes", "attr": "clientes",
            "colunas": [("id", "ID", 50), ("nome", "Nome", 200), ("cpf", "CPF", 120),
                        ("telefone", "Telefone", 120), ("email", "E-mail", 200)],
            "campos": [
                {"key": "nome", "label": "Nome"},
                {"key": "cpf", "label": "CPF"},
                {"key": "telefone", "label": "Telefone"},
                {"key": "email", "label": "E-mail"},
            ],
            "listar": lambda c: c.listar(),
            "criar": lambda c, v: c.cadastrar(v["nome"], v["cpf"], v["telefone"], v["email"]),
            "atualizar": lambda c, i, v: c.atualizar(i, v["nome"], v["cpf"], v["telefone"], v["email"]),
            "excluir": lambda c, i: c.excluir(i),
        },
        "funcionarios": {
            "titulo": "Funcionários", "attr": "funcionarios",
            "colunas": [("id", "ID", 50), ("nome", "Nome", 180), ("cargo", "Cargo", 120),
                        ("cpf", "CPF", 110), ("salario", "Salário", 100),
                        ("data_admissao", "Admissão", 110)],
            "campos": [
                {"key": "nome", "label": "Nome"},
                {"key": "cargo", "label": "Cargo"},
                {"key": "cpf", "label": "CPF"},
                {"key": "telefone", "label": "Telefone"},
                {"key": "email", "label": "E-mail"},
                {"key": "salario", "label": "Salário", "tipo": "float"},
                {"key": "data_admissao", "label": "Admissão (AAAA-MM-DD)"},
            ],
            "listar": lambda c: c.listar(),
            "criar": lambda c, v: c.cadastrar(v["nome"], cargo=v["cargo"], cpf=v["cpf"],
                                              telefone=v["telefone"], email=v["email"],
                                              salario=v["salario"], data_admissao=v["data_admissao"]),
            "atualizar": lambda c, i, v: c.atualizar(i, v["nome"], v["cargo"], v["cpf"],
                                                     v["telefone"], v["email"], v["salario"],
                                                     v["data_admissao"]),
            "excluir": lambda c, i: c.excluir(i),
        },
        "usuarios": {
            "titulo": "Usuários", "attr": "usuarios",
            "colunas": [("id", "ID", 60), ("username", "Usuário", 200), ("role", "Perfil", 140)],
            "campos": [
                {"key": "username", "label": "Usuário"},
                {"key": "password", "label": "Senha", "tipo": "password"},
                {"key": "role", "label": "Perfil",
                 "tipo": "select", "fonte": lambda b: [(r, r) for r in
                                                       ("cadastro", "vendas", "mecanico", "admin")]},
            ],
            "listar": lambda c: c.listar(),
            "criar": lambda c, v: c.cadastrar(v["username"], v["password"], v["role"]),
            "atualizar": lambda c, i, v: c.atualizar(i, v["username"], v["password"], v["role"]),
            "excluir": lambda c, i: c.excluir(i),
        },
        "marcas": {
            "titulo": "Marcas", "attr": "marcas",
            "colunas": [("id", "ID", 60), ("nome", "Nome", 240)],
            "campos": [{"key": "nome", "label": "Nome"}],
            "listar": lambda c: c.listar(),
            "criar": lambda c, v: c.cadastrar(v["nome"]),
            "atualizar": lambda c, i, v: c.atualizar(i, v["nome"]),
            "excluir": lambda c, i: c.excluir(i),
        },
        "modelos": {
            "titulo": "Modelos", "attr": "modelos",
            "colunas": [("id", "ID", 50), ("nome", "Nome", 180), ("numero_serie", "Nº Série", 140),
                        ("marca_nome", "Marca", 140)],
            "campos": [
                {"key": "nome", "label": "Nome"},
                {"key": "numero_serie", "label": "Número de série"},
                {"key": "marca_id", "label": "Marca", "tipo": "select",
                 "fonte": _fonte_marcas},
            ],
            "listar": lambda c: c.listar(),
            "criar": lambda c, v: c.cadastrar(v["nome"], v["numero_serie"], marca_id=v["marca_id"]),
            "atualizar": lambda c, i, v: c.atualizar(i, v["nome"], v["numero_serie"], marca_id=v["marca_id"]),
            "excluir": lambda c, i: c.excluir(i),
        },
        "categorias": {
            "titulo": "Categorias de Peça", "attr": "categorias",
            "colunas": [("id", "ID", 60), ("nome", "Nome", 180), ("descricao", "Descrição", 260)],
            "campos": [
                {"key": "nome", "label": "Nome"},
                {"key": "descricao", "label": "Descrição"},
            ],
            "listar": lambda c: c.listar(),
            "criar": lambda c, v: c.cadastrar(v["nome"], v["descricao"]),
            "atualizar": lambda c, i, v: c.atualizar(i, v["nome"], v["descricao"]),
            "excluir": lambda c, i: c.excluir(i),
        },
        "veiculos": {
            "titulo": "Veículos (catálogo)", "attr": "veiculos",
            "colunas": [("id", "ID", 50), ("marca_nome", "Marca", 110), ("modelo_nome", "Modelo", 110),
                        ("chassi", "Chassi", 160), ("ano_fabricacao", "Ano", 70),
                        ("cor", "Cor", 90), ("preco", "Preço", 100)],
            "campos": [
                {"key": "marca_id", "label": "Marca", "tipo": "select", "fonte": _fonte_marcas},
                {"key": "modelo_id", "label": "Modelo", "tipo": "select", "fonte": _fonte_modelos, "depende_de": "marca_id"},
                {"key": "chassi", "label": "Chassi"},
                {"key": "ano_fabricacao", "label": "Ano de fabricação", "tipo": "int"},
                {"key": "cor", "label": "Cor"},
                {"key": "preco", "label": "Preço", "tipo": "float"},
            ],
            "listar": lambda c: c.listar(),
            "criar": lambda c, v: c.cadastrar(v["marca_id"], v["modelo_id"], v["chassi"],
                                             v["ano_fabricacao"], v["cor"], v["preco"]),
            "atualizar": lambda c, i, v: c.atualizar(i, v["marca_id"], v["modelo_id"], v["chassi"],
                                                    v["ano_fabricacao"], v["cor"], v["preco"]),
            "excluir": lambda c, i: c.excluir(i),
        },
        "veiculos_cliente": {
            "titulo": "Veículos de Clientes", "attr": "veiculos_cliente",
            "colunas": [("id", "ID", 50), ("cliente_id", "Cliente", 90), ("marca", "Marca", 140),
                        ("placa", "Placa", 110), ("ano", "Ano", 80)],
            "campos": [
                {"key": "cliente_id", "label": "Cliente", "tipo": "select", "fonte": _fonte_clientes},
                {"key": "marca", "label": "Marca", "tipo": "select", "fonte": _fonte_marcas_nome},
                {"key": "placa", "label": "Placa"},
                {"key": "ano", "label": "Ano", "tipo": "int"},
            ],
            "listar": lambda c: c.listar(),
            "criar": lambda c, v: c.cadastrar(v["cliente_id"], v["marca"], v["placa"], v["ano"]),
            "atualizar": lambda c, i, v: c.atualizar(i, v["cliente_id"], v["marca"], v["placa"], v["ano"]),
            "excluir": lambda c, i: c.excluir(i),
        },
        "pecas": {
            "titulo": "Peças", "attr": "pecas",
            "colunas": [("id", "ID", 50), ("nome", "Nome", 200), ("categoria_id", "Categoria", 100),
                        ("preco", "Preço", 100)],
            "campos": [
                {"key": "nome", "label": "Nome"},
                {"key": "categoria_id", "label": "Categoria", "tipo": "select",
                 "fonte": _fonte_categorias},
                {"key": "preco", "label": "Preço", "tipo": "float"},
            ],
            "listar": lambda c: c.listar(),
            "criar": lambda c, v: c.cadastrar(v["nome"], v["categoria_id"], v["preco"]),
            "atualizar": lambda c, i, v: c.atualizar(i, v["nome"], v["categoria_id"], v["preco"]),
            "excluir": lambda c, i: c.excluir(i),
        },
        "ordens_servico": {
            "titulo": "Ordens de Serviço", "attr": "ordens_servico",
            "id_key": "id",
            "colunas": [("id", "ID", 50), ("cliente_id", "Cliente", 80),
                        ("tipo_servico", "Serviço", 160), ("entrada", "Entrada", 140),
                        ("saida", "Saída", 140), ("valor_mao_de_obra", "M. Obra", 90),
                        ("valor_peca", "Peças", 90)],
            "campos": [
                {"key": "cliente_id", "label": "Cliente", "tipo": "select", "fonte": _fonte_clientes},
                {"key": "veiculo_cliente_id", "label": "Veículo do cliente",
                 "tipo": "select", "fonte": _fonte_veic_cliente},
                {"key": "tipo_servico", "label": "Tipo de serviço"},
                {"key": "valor_mao_de_obra", "label": "Valor mão de obra", "tipo": "float"},
                {"key": "valor_peca", "label": "Valor peças", "tipo": "float"},
            ],
            "listar": lambda c: c.listar(),
            "criar": lambda c, v: c.cadastrar(v["cliente_id"], v["veiculo_cliente_id"],
                                             v["tipo_servico"], v["valor_mao_de_obra"], v["valor_peca"]),
            "atualizar": lambda c, i, v: c.atualizar(i, v["cliente_id"], v["veiculo_cliente_id"],
                                                    v["tipo_servico"], v["valor_mao_de_obra"], v["valor_peca"]),
            "excluir": lambda c, i: c.excluir(i),
            "acoes_extras": [("Fechar OS (carimbar saída)", lambda c, i: c.fechar(i))],
        },
    }
