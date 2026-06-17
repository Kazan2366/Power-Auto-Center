# Handoff — Contrato da API de Backend

**Data:** 2026-06-11 · **Stack:** Python 3.14 · SQLite (stdlib) · sem UI

Ponto de entrada único: `from backend import Backend`. `Backend(connection=None)`
cria (ou recebe) a conexão e instancia todos os módulos abaixo. Ao final,
`backend.fechar()` fecha a conexão.

Convenções:
- Controllers retornam `dict` / `list[dict]` / `None` / `int` (id) — nunca `Row`.
- Validação de domínio ⇒ `ValueError` (mensagem legível para exibir na UI).
- Violação de unicidade (cpf, chassi, placa, username, marca, numero_serie) ⇒ `sqlite3.IntegrityError`.
- Parâmetros opcionais aceitam `None`.

```python
from backend import Backend
b = Backend()
# ... use os módulos abaixo ...
b.fechar()
```

---

## Autenticação — `b.auth` (LoginController)

| Método | Retorno |
|---|---|
| `authenticate(username, password)` | `{"success": True, "role": "...", "username": "..."}` ou `{"success": False, "message": "..."}` |

```python
r = b.auth.authenticate("Cadastrar23", "4590")
# {'success': True, 'role': 'cadastro', 'username': 'Cadastrar23'}
```

## Dashboard — `b.dashboard` (DashboardService)

`resumo()` → dict de indicadores:

```python
b.dashboard.resumo()
# {'total_clientes': 0, 'total_funcionarios': 0, 'total_usuarios': 3,
#  'total_marcas': 0, 'total_categorias': 0, 'total_veiculos': 0, 'total_pecas': 0,
#  'veiculos_em_estoque': 0, 'pecas_em_estoque': 0, 'qtd_vendas': 0,
#  'total_vendas': 0, 'os_abertas': 0, 'os_total': 0}
```

## Clientes — `b.clientes` (ClienteController)

`cadastrar(nome, cpf, telefone, email) -> int` · `listar()` · `buscar(id)` ·
`atualizar(id, nome, cpf, telefone, email)` · `excluir(id)`

```python
cid = b.clientes.cadastrar("Ana Maria", "11122233344", "11999990000", "ana@x.com")
b.clientes.listar()   # [{'id': 1, 'nome': 'Ana Maria', 'cpf': '...', 'telefone': '...', 'email': '...'}]
```

## Funcionários — `b.funcionarios` (FuncionarioController)

`cadastrar(nome, cargo=None, cpf=None, telefone=None, email=None, salario=None, data_admissao=None) -> int` ·
`listar()` · `buscar(id)` ·
`atualizar(id, nome, cargo, cpf, telefone, email, salario, data_admissao)` ·
`total_salarios() -> float` · `excluir(id)`

```python
fid = b.funcionarios.cadastrar("Carlos", cargo="Mecânico", cpf="55566677788",
                               salario=3000.0, data_admissao="2026-01-10")
```

## Usuários — `b.usuarios` (UsuarioController)

`cadastrar(username, password, role) -> int` · `listar()` (sem senha) ·
`buscar(id)` (sem senha) · `atualizar(id, username, password, role)` · `excluir(id)`
Perfis válidos: `cadastro`, `vendas`, `mecanico`, `admin`.

```python
uid = b.usuarios.cadastrar("operador1", "senha123", "vendas")
b.usuarios.listar()   # [{'id': 1, 'username': 'Cadastrar23', 'role': 'cadastro'}, ...]  (sem password)
```

## Marcas — `b.marcas` (MarcaController)

`cadastrar(nome) -> int` · `listar()` · `buscar(id)` · `atualizar(id, nome)` · `excluir(id)`

```python
mid = b.marcas.cadastrar("Fiat")
b.marcas.listar()   # [{'id': 1, 'nome': 'Fiat'}]
```

## Categorias — `b.categorias` (CategoriaPecaController)

`cadastrar(nome, descricao) -> int` · `listar()` · `buscar(id)` ·
`atualizar(id, nome, descricao)` · `excluir(id)`

```python
cat = b.categorias.cadastrar("Freios", "Pastilhas, discos e fluidos")
```

## Veículos — `b.veiculos` (VeiculoController) — **normalizado por marca_id**

`cadastrar(marca_id, modelo_id, chassi, ano_fabricacao, cor, preco) -> int` ·
`listar()` · `buscar(id)` ·
`atualizar(id, marca_id, modelo_id, chassi, ano_fabricacao, cor, preco)` · `excluir(id)`

- `marca_id` ← `b.marcas.listar()` (obrigatório). `modelo_id` ← `b.modelos.listar()` (opcional).
- `listar()` já resolve os nomes por JOIN: cada item traz `marca_id`, `marca_nome`,
  `modelo_id`, `modelo_nome`. `buscar(id)` traz as colunas cruas (ids) para edição.

```python
mid = b.marcas.cadastrar("Fiat")
vid = b.veiculos.cadastrar(mid, None, "9BWZZZ377VT004251", 2022, "Preto", 90000.0)
b.veiculos.listar()
# [{'id': 1, 'marca_id': 1, 'modelo_id': None, 'chassi': '...', 'ano_fabricacao': 2022,
#   'cor': 'Preto', 'preco': 90000.0, 'marca_nome': 'Fiat', 'modelo_nome': None}]
```

## Vendas — `b.vendas` (VendaController)

`registrar_venda(tipo, itens) -> int` · `listar()` · `buscar(id)` ·
`listar_itens(venda_id)` · `total_vendas() -> float` · `excluir(id)`

`itens` = `list[dict]` com `produto_id, tipo_produto, quantidade, preco_unitario`
(o controller calcula o `total = Σ quantidade × preco_unitario`).

```python
vid = b.vendas.registrar_venda("mista", [
    {"produto_id": 1, "tipo_produto": "veiculo", "quantidade": 1, "preco_unitario": 90000.0},
    {"produto_id": 7, "tipo_produto": "peca",    "quantidade": 2, "preco_unitario": 100.0},
])
b.vendas.total_vendas()   # 90200.0
```

## Financeiro — `b.financeiro` (FinanceiroService)

| Método | Retorno |
|---|---|
| `resumo()` | `{receita_vendas, receita_servicos, receita_total, despesa_salarios, saldo}` |
| `movimentos()` | `list[{data, origem, tipo, descricao, valor}]` — origem ∈ venda/ordem_servico/salario; tipo ∈ entrada/saida |

```python
b.financeiro.resumo()
# {'receita_vendas': 90200.0, 'receita_servicos': 200.0, 'receita_total': 90400.0,
#  'despesa_salarios': 3000.0, 'saldo': 87400.0}
```

## Relatórios — `b.relatorios` (RelatorioService)

| Método | Retorno |
|---|---|
| `listar_disponiveis()` | `list[str]` |
| `gerar(nome)` | `{"nome", "headers": [...], "linhas": [dict, ...]}` |
| `exportar_csv(nome, caminho=None)` | caminho do CSV (default `relatorios/<nome>-<ts>.csv`) |
| `formatar_console(nome)` | `str` tabular |

Relatórios disponíveis: `clientes, funcionarios, usuarios, marcas, modelos,
categorias, veiculos, pecas, estoque_veiculos, estoque_pecas, vendas, ordens_servico`.

```python
b.relatorios.gerar("veiculos")["headers"]   # ['id', 'marca', 'modelo', 'chassi', 'ano_fabricacao', 'cor', 'preco']
b.relatorios.exportar_csv("clientes")        # 'C:\\...\\relatorios\\clientes-20260611-101500.csv'
print(b.relatorios.formatar_console("marcas"))
```

## Backup — `b.backup` (BackupService)

| Método | Retorno |
|---|---|
| `criar_backup(dest_dir=None)` | caminho do `.db` datado (default `backups/concessionaria-<ts>.db`) |
| `listar_backups(dest_dir=None)` | `list[str]` |

```python
b.backup.criar_backup()      # 'C:\\...\\backups\\concessionaria-20260611-101530.db'
b.backup.listar_backups()    # ['C:\\...\\backups\\concessionaria-20260611-101530.db']
```

---

## Módulos de apoio (também na fachada)

### `b.modelos` (ModeloController) — vinculável a marca
`cadastrar(nome, numero_serie, marca_id=None) -> int` · `listar()` · `buscar(id)` ·
`atualizar(id, nome, numero_serie, marca_id=None)` · `excluir(id)`
- `marca_id` (← `b.marcas.listar()`) é **opcional** (FK → `marcas`, `ON DELETE SET NULL`).
- `listar()` resolve o nome por JOIN: cada item traz `marca_id` e `marca_nome`.
```python
mid = b.marcas.cadastrar("Fiat")
b.modelos.cadastrar("Uno", "SN-0001", marca_id=mid)
b.modelos.listar()   # [{'id': 1, 'nome': 'Uno', 'numero_serie': 'SN-0001', 'marca_id': 1, 'marca_nome': 'Fiat'}]
```

### `b.veiculos_cliente` (VeiculoClienteController)
Veículo que pertence a um cliente (para Ordem de Serviço). `marca` aqui é **texto livre**
(é o carro do cliente, não o catálogo da loja).
`cadastrar(cliente_id, marca, placa, ano) -> int` · `listar()` ·
`listar_por_cliente(cliente_id)` · `buscar(id)` · `atualizar(id, cliente_id, marca, placa, ano)` · `excluir(id)`
```python
vc = b.veiculos_cliente.cadastrar(cliente_id, "Fiat", "ABC1D23", 2020)
```

### `b.pecas` (PecaController)
`cadastrar(nome, categoria_id, preco) -> int` · `listar()` · `buscar(id)` ·
`atualizar(id, nome, categoria_id, preco)` · `excluir(id)`  (categoria ← `b.categorias.listar()`)

### `b.estoque` (EstoqueController)
Quantidade é **definida** (set), não incrementada (UPSERT por produto).
`definir_veiculo(veiculo_id, quantidade)` · `definir_peca(peca_id, quantidade)` ·
`buscar_veiculo(id)` · `buscar_peca(id)` · `listar_veiculos()` · `listar_pecas()` ·
`total_veiculos() -> int` · `total_pecas() -> int`
```python
b.estoque.definir_veiculo(vid, 5)
b.estoque.listar_veiculos()   # [{'veiculo_id': 1, 'quantidade': 5, 'marca': 'Fiat', 'chassi': '...'}]
```

### `b.ordens_servico` (OrdemServicoController)
`cadastrar(cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca) -> int` ·
`listar()` · `buscar(id)` · `atualizar(...)` · `fechar(id)` (carimba a saída) ·
`total_abertas() -> int` · `excluir(id)`
```python
osid = b.ordens_servico.cadastrar(cliente_id, vc, "Revisão", 150.0, 50.0)
b.ordens_servico.fechar(osid)
```
