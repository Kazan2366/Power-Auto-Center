# Backend — Entrega Fase 1 (Camada de Dados)

> Autor: Caio Codifica (backend, OpenSquad) · Data: 2026-06-11 · Status: ✅ Concluída

## Resumo

A camada de dados da concessária foi normalizada de três arquiteturas incompatíveis para uma única
arquitetura MVC/DAO coerente sobre SQLite. Existe agora **uma fonte de verdade do schema**
(`database/connection.py::SCHEMA_SQL`), criada automaticamente em runtime e espelhada em
`database/sql/create_database.sql` apenas como documentação. Cada uma das 9 entidades (Cliente, Modelo,
Veículo, CategoriaPeça, Peça, VeículoCliente, Estoque, Venda, OrdemServiço) tem um **Model (DAO)** que
recebe a `connection` injetada e fala SQL parametrizado (`?` + `sqlite3.Row`), e um **Controller** que
valida entradas, delega ao model e devolve `dict`/`list[dict]` (nunca `Row`), desacoplando a futura
camada de views do sqlite3. Estoque usa UPSERT, Venda grava itens + total numa transação com rollback,
e Ordem de Serviço controla abertura/fechamento por timestamp. Tudo coberto por 28 testes pytest
(round-trip CRUD + validações) rodando contra um banco SQLite em memória — **100% verde**.

## Stack escolhida

| Componente | Versão | Papel |
|---|---|---|
| Python | 3.14.4 | Linguagem |
| sqlite3 | stdlib (Python 3.14) | Banco de dados (arquivo `concessionaria.db`) |
| pytest | 9.0.3 | Testes unitários da camada model+controller |
| flet | 0.85.3 | Instalado para a Fase 2 (UI) — **não usado na Fase 1** |

`matplotlib`/`pandas`/`PyMySQL` foram **removidos** do `requirements.txt` (fora de escopo / irrelevantes
para SQLite).

## Arquitetura

**Padrão: MVC com camada de dados em Layered DAO + injeção de conexão.**

- `main.py` cria **uma** `connection` (`create_connection()`) e a injeta para baixo.
- `Controller(connection)` instancia `Model(connection)`. Validação de domínio mora no controller
  (`raise ValueError`); SQL mora no model.
- Models usam `cursor = connection.cursor()` + `connection.commit()` (sem `with connection.cursor()`,
  que era padrão PyMySQL e não existe em sqlite3). Placeholders `?`, `row_factory = sqlite3.Row`,
  `PRAGMA foreign_keys = ON`.

```
model/                              controller/
├── cliente.py          (Cliente)   ├── cliente_controller.py          (ClienteController)
├── modelo.py           (Modelo)    ├── modelo_controller.py           (ModeloController)
├── veiculo.py          (Veiculo)   ├── veiculo_controller.py          (VeiculoController)
├── categoria_peca.py   (Categoria  ├── categoria_peca_controller.py   (CategoriaPecaController)
│                        Peca)      │
├── peca.py             (Peca)      ├── peca_controller.py             (PecaController)
├── veiculo_cliente.py  (Veiculo    ├── veiculo_cliente_controller.py  (VeiculoClienteController)
│                        Cliente)   │
├── estoque.py          (Estoque)   ├── estoque_controller.py          (EstoqueController)
├── venda.py            (Venda)     ├── venda_controller.py            (VendaController)
└── ordem_servico.py    (OrdemSer   └── ordem_servico_controller.py    (OrdemServicoController)
                         vico)

database/connection.py  → create_connection(db_path=None) | create_schema | seed_users | SCHEMA_SQL
tests/                  → conftest.py (fixture `conn` em :memory:) + 1 arquivo por entidade
```

## Contratos (para a Diana consumir na Fase 2)

Controllers retornam `dict`/`list[dict]`/`None`/`int`. Models retornam `sqlite3.Row`/lista de `Row`/
`lastrowid`. Validação inválida ⇒ `ValueError`; violação de unicidade ⇒ `sqlite3.IntegrityError`
(a view trata).

| Entidade | Métodos do Controller | Métodos do Model |
|---|---|---|
| **Cliente** | `cadastrar(nome, cpf, telefone, email)→int`, `listar()`, `buscar(id)`, `atualizar(id, nome, cpf, telefone, email)`, `excluir(id)` | `criar`, `listar`, `buscar`, `atualizar`, `excluir` |
| **Modelo** | `cadastrar(nome, numero_serie)→int`, `listar()`, `buscar(id)`, `atualizar(id, nome, numero_serie)`, `excluir(id)` | `criar`, `listar`, `buscar`, `atualizar`, `excluir` |
| **Veiculo** | `cadastrar(marca, modelo_id, chassi, ano_fabricacao, cor, preco)→int`, `listar()`, `buscar(id)`, `atualizar(id, marca, modelo_id, chassi, ano_fabricacao, cor, preco)`, `excluir(id)` | `criar`, `listar`, `buscar`, `atualizar`, `excluir` |
| **CategoriaPeca** | `cadastrar(nome, descricao)→int`, `listar()`, `buscar(id)`, `atualizar(id, nome, descricao)`, `excluir(id)` | `criar`, `listar`, `buscar`, `atualizar`, `excluir` |
| **Peca** | `cadastrar(nome, categoria_id, preco)→int`, `listar()`, `buscar(id)`, `atualizar(id, nome, categoria_id, preco)`, `excluir(id)` | `criar`, `listar`, `buscar`, `atualizar`, `excluir` |
| **VeiculoCliente** | `cadastrar(cliente_id, marca, placa, ano)→int`, `listar()`, `listar_por_cliente(cliente_id)`, `buscar(id)`, `atualizar(id, cliente_id, marca, placa, ano)`, `excluir(id)` | `criar`, `listar`, `listar_por_cliente`, `buscar`, `atualizar`, `excluir` |
| **Estoque** | `definir_veiculo(veiculo_id, qtd)`, `definir_peca(peca_id, qtd)`, `buscar_veiculo(id)`, `buscar_peca(id)`, `listar_veiculos()`, `listar_pecas()`, `total_veiculos()→int`, `total_pecas()→int` | `definir_veiculo`, `definir_peca`, `buscar_veiculo`, `buscar_peca`, `listar_veiculos`, `listar_pecas`, `total_veiculos`, `total_pecas` |
| **Venda** | `registrar_venda(tipo, itens)→int`, `listar()`, `buscar(id)`, `listar_itens(venda_id)`, `total_vendas()→float`, `excluir(id)` | `registrar(tipo, itens, total)`, `listar`, `buscar`, `listar_itens`, `total_vendas`, `excluir` |
| **OrdemServico** | `cadastrar(cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca)→int`, `listar()`, `buscar(id)`, `atualizar(id, cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca)`, `fechar(id)`, `total_abertas()→int`, `excluir(id)` | `criar`, `listar`, `buscar`, `atualizar`, `fechar`, `total_abertas`, `excluir` |

**Formato de `itens` em `Venda.registrar_venda`:** `list[dict]` com chaves
`produto_id`, `tipo_produto`, `quantidade`, `preco_unitario`. O controller calcula o `total`
(`Σ quantidade × preco_unitario`).

## Decisões (racional em 1 linha)

- **Schema único em `connection.py`**: elimina as 3 arquiteturas contraditórias; `create_database.sql`
  vira só espelho/documentação (SQLite, não MySQL).
- **`create_connection(db_path=None)` cria schema + seed sempre**: idempotente (`IF NOT EXISTS` /
  `INSERT OR IGNORE`), permite testar em `:memory:` sem efeito colateral de import.
- **UPSERT no estoque** (`ON CONFLICT(...) DO UPDATE`): "definir quantidade" é set, não increment;
  uma linha por item, sem duplicar.
- **Transação na venda** (`executemany` + `commit`, `except: rollback; raise`): venda+itens são
  atômicos — catch silencioso seria bug em incubação, então re-propaga.
- **Validação via `ValueError`**: regra de domínio (campo obrigatório, preço/quantidade negativos) é
  responsabilidade do controller, com mensagem legível para a view exibir.
- **Controllers devolvem `dict`/`list[dict]`**: desacopla a view do `sqlite3.Row`; a Diana consome
  estruturas Python puras.
- **Unicidade propaga como `sqlite3.IntegrityError`**: CPF/chassi/placa duplicados não são validados no
  controller (evita race + duplicar a constraint); a view da Fase 2 captura e exibe.
- **OrdemServico com timestamps**: `entrada = CURRENT_TIMESTAMP` na criação, `saida = NULL` (aberta) →
  `fechar()` carimba `saida`; `total_abertas()` = `COUNT(*) WHERE saida IS NULL`.

## Como rodar

```bash
# 1. Instalar dependências (flet p/ Fase 2, pytest p/ testes)
pip install -r requirements.txt

# 2. Rodar a suíte de testes da camada de dados
python -m pytest -v

# 3. Rodar o app (Fase 2 fará a UI; hoje main.py instancia LoginView)
python main.py
```

O banco `concessionaria.db` é criado automaticamente na primeira conexão (schema + usuários-semente).
Usuários-semente: `Cadastrar23/4590` (cadastro), `Vendendor13/8955` (vendas), `Mecânico/7675` (mecanico).

## Resultado dos testes

`python -m pytest -v` → **28 passed, 0 failed, 0 errors** (≈0.21s), cobrindo `connection` + as 9 entidades:

```
tests/test_connection.py ......... test_schema_tem_todas_as_tabelas              PASSED
                                   test_usuarios_semente_inseridos                PASSED
tests/test_cliente.py ............ test_cadastrar_e_listar                        PASSED
                                   test_buscar_atualizar_excluir                  PASSED
                                   test_nome_obrigatorio                          PASSED
                                   test_cpf_obrigatorio                           PASSED
tests/test_modelo.py ............. test_crud_modelo                               PASSED
                                   test_nome_obrigatorio                          PASSED
tests/test_veiculo.py ............ test_crud_veiculo                              PASSED
                                   test_marca_obrigatoria                         PASSED
                                   test_preco_negativo_invalido                   PASSED
tests/test_categoria_peca.py ..... test_crud_categoria                           PASSED
                                   test_nome_obrigatorio                          PASSED
tests/test_peca.py ............... test_crud_peca                                 PASSED
                                   test_nome_obrigatorio                          PASSED
                                   test_preco_negativo_invalido                   PASSED
tests/test_veiculo_cliente.py .... test_crud_veiculo_cliente                      PASSED
                                   test_cliente_obrigatorio                       PASSED
                                   test_placa_obrigatoria                         PASSED
tests/test_estoque.py ............ test_estoque_veiculo_upsert_e_total            PASSED
                                   test_estoque_peca                              PASSED
                                   test_quantidade_negativa_invalida              PASSED
tests/test_venda.py .............. test_registrar_venda_calcula_total            PASSED
                                   test_itens_obrigatorios                        PASSED
                                   test_quantidade_invalida                       PASSED
                                   test_excluir_venda_remove_itens                PASSED
tests/test_ordem_servico.py ...... test_crud_e_fechamento                         PASSED
                                   test_cliente_e_veiculo_obrigatorios            PASSED

============================== 28 passed ==============================
```

> Nota de ferramenta: o `pytest` local roda atrás de um wrapper (`rtk/tee`) que condensa a saída a
> `Pytest: 28 passed`. A listagem por teste acima foi extraída do relatório JUnit-XML
> (`--junit-xml`) gerado na mesma execução (28 testcases, 0 failures, 0 errors).

## Notas para a Fase 2 (handoff)

- Indicadores de dashboard já disponíveis nos controllers: `VendaController.total_vendas()`,
  `EstoqueController.total_veiculos()`, `OrdemServicoController.total_abertas()`.
- Joins de exibição (veículo→nome do modelo, peça→nome da categoria) ficam nas views/controllers da
  Fase 2; `Estoque.listar_veiculos()`/`listar_pecas()` já trazem o join de exibição (marca/chassi/nome).
- `main.py` está limpo mas ainda chama `LoginView(connection).run()` — a Fase 2 substitui por
  `ft.app(target=app.main)` único, conforme o design.
