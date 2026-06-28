# Concessionária — Sistema de Gestão (MVC + CustomTkinter)

Sistema de gerenciamento de concessionária em **Python 3.14 + SQLite**
(stdlib `sqlite3`) com **interface gráfica em CustomTkinter**. A camada de
apresentação (`view/`) consome o backend exclusivamente através da fachada
[`Backend`](backend.py), preservando o padrão MVC. O banco `concessionaria.db`
é criado e populado automaticamente em runtime — sem servidor de banco externo.

> Aplicação executável: `python main.py` abre a tela de login e o painel de
> gestão. O backend (model/controller/service) permanece independente da UI e
> pode ser consumido por qualquer outro frontend.

## Arquitetura

```
MVC + DAO com injeção de conexão:

  View (CustomTkinter)           view/*.py          ── login, sidebar, telas CRUD/dashboard
    └─ Backend (fachada)         backend.py
         └─ Controller(connection) controller/*.py  ── validação + retorna dict/list[dict]
              └─ Model(connection) model/*.py        ── SQL parametrizado (?), sqlite3.Row
         └─ Service(connection)  service/*.py        ── agregações, relatórios, backup

  database/connection.py  → create_connection() cria schema (idempotente) + usuários-semente
```

A view nunca acessa o `sqlite3` diretamente: instancia um único `Backend()` por
sessão e usa os atributos da fachada. O menu lateral é filtrado pelo **perfil**
do usuário autenticado (cadastro / vendas / mecanico / admin).

- Uma única `connection` é criada em `create_connection()` e injetada para baixo.
- Controllers validam (lançam `ValueError`) e devolvem estruturas Python puras
  (`dict`/`list[dict]`), nunca `sqlite3.Row` — desacoplando o frontend do sqlite3.
- Unicidade (CPF, chassi, placa, username, marca, numero_serie) propaga como `sqlite3.IntegrityError`.

## Mapa do menu → módulo de backend → view

Cada item da sidebar corresponde a um atributo da fachada `Backend` e a uma tela:

| Item do menu | Atributo | Classe (backend) | View |
|---|---|---|---|
| Dashboard | `backend.dashboard` | `DashboardService` | `DashboardView` |
| Clientes | `backend.clientes` | `ClienteController` | `CrudView` |
| Funcionários | `backend.funcionarios` | `FuncionarioController` | `CrudView` |
| Usuários | `backend.usuarios` | `UsuarioController` | `CrudView` |
| Marcas | `backend.marcas` | `MarcaController` | `CrudView` |
| Categorias | `backend.categorias` | `CategoriaPecaController` | `CrudView` |
| Modelos | `backend.modelos` | `ModeloController` | `CrudView` |
| Veículos | `backend.veiculos` | `VeiculoController` | `CrudView` |
| Veíc. Clientes | `backend.veiculos_cliente` | `VeiculoClienteController` | `CrudView` |
| Peças | `backend.pecas` | `PecaController` | `CrudView` |
| Estoque | `backend.estoque` | `EstoqueController` | `EstoqueView` |
| **Vendas** | `backend.vendas` | `VendaController` | `VendasView` (carrinho de itens) |
| Ordens Serviço | `backend.ordens_servico` | `OrdemServicoController` | `CrudView` (+ ação "Fechar OS") |
| Financeiro | `backend.financeiro` | `FinanceiroService` | `FinanceiroView` |
| Relatórios | `backend.relatorios` | `RelatorioService` | `RelatoriosView` |
| Backup | `backend.backup` | `BackupService` | `BackupView` |
| _(Sair)_ | `backend.fechar()` | — | botão da sidebar → volta ao login |

Apoio fora do menu: `backend.auth` (login).

### Perfis e permissões

O menu lateral é **filtrado pelo perfil** autenticado (definido em
`view/main_window.py::PERMISSOES`). Perfis desconhecidos e `admin` veem tudo.

| Perfil | Itens visíveis |
|---|---|
| `cadastro` | Dashboard, Clientes, Funcionários, Usuários, Marcas, Categorias, Modelos, Veículos, Peças, Estoque, Relatórios, Backup |
| `vendas` | Dashboard, Clientes, Veículos, Estoque, **Vendas**, Financeiro, Relatórios |
| `mecanico` | Dashboard, Clientes, Veíc. Clientes, Ordens Serviço, Peças, Estoque |
| `admin` | Todos os itens |

O contrato completo de métodos do backend está em
[`docs/handoff-backend-api.md`](docs/handoff-backend-api.md).

## Estrutura do projeto

```
CONCESSIONÁRIA
├── backend.py               # Fachada Backend (ponto de entrada da view)
├── main.py                  # Executável: abre a GUI (--headless imprime o dashboard)
├── seed_exemplos.py         # Popula 3 exemplos de cada cadastro (idempotente)
├── requirements.txt         # Dependências (customtkinter, pytest)
├── view/                    # Camada de apresentação (CustomTkinter)
│   ├── app.py               # App: orquestra login → janela principal
│   ├── login_view.py        # Tela de login (backend.auth)
│   ├── main_window.py       # Sidebar (menu por perfil) + roteamento de telas
│   ├── crud_view.py         # Tela CRUD genérica (dirigida por spec)
│   ├── specs.py             # Especificações das entidades de cadastro
│   ├── dashboard_view.py    # Cartões de indicadores
│   ├── vendas_view.py       # Registro de vendas com carrinho de itens
│   ├── estoque_view.py      # Define quantidades (abas Veículos/Peças)
│   ├── financeiro_view.py   # Resumo + movimentos
│   ├── relatorios_view.py   # Geração e exportação CSV
│   ├── backup_view.py       # Cria/lista backups do .db
│   ├── widgets.py           # DataTable, StatCard
│   └── theme.py             # Cores, fontes e estilo das tabelas
├── database/
│   ├── connection.py        # create_connection() + schema canônico (SCHEMA_SQL)
│   └── sql/create_database.sql  # Espelho do schema (documentação)
├── model/                   # DAOs SQLite (1 por entidade)
├── controller/              # Controllers (validação + CRUD)
├── service/                 # Serviços derivados
│   ├── dashboard_service.py # Indicadores agregados
│   ├── financeiro_service.py# Receitas (vendas/OS) e despesas (salários)
│   ├── relatorio_service.py # Listagens em CSV/console
│   └── backup_service.py    # Cópia datada do .db
├── utils/helpers.py         # Funções puras (moeda, validações)
├── tests/                   # Suíte pytest (SQLite em memória)
└── docs/                    # Documentação e handoff
```

## Instalação e uso

```bash
pip install -r requirements.txt   # customtkinter + pytest
python main.py                    # abre a aplicação gráfica (tela de login)
python main.py --headless         # apenas cria o banco e imprime o dashboard
python seed_exemplos.py           # cadastra 3 exemplos de cada entidade (opcional)
python -m pytest -q               # roda a suíte de testes
```

Login (usuários-semente, todos com senha `senha123`): `operador.cadastro`
(cadastro), `operador.vendas` (vendas), `operador.mecanico` (mecanico),
`operador.admin` (admin).

Exemplo de consumo pelo frontend:

```python
from backend import Backend

backend = Backend()                       # cria a conexão e todos os módulos
backend.marcas.cadastrar("Fiat")
clientes = backend.clientes.listar()      # list[dict]
print(backend.dashboard.resumo())         # indicadores
caminho = backend.backup.criar_backup()   # backups/concessionaria-AAAAMMDD-HHMMSS.db
backend.fechar()
```

## Banco de dados

Schema canônico em `database/connection.py::SCHEMA_SQL` (criado via `CREATE TABLE
IF NOT EXISTS` — idempotente). Entidades: `users`, `funcionarios`, `marcas`,
`clientes`, `modelos`, `veiculos`, `categorias_peca`, `pecas`, `veiculo_cliente`,
`estoque_veiculos`, `estoque_pecas`, `vendas`, `venda_itens`, `ordem_servico`.

Usuários-semente (ambiente de teste, todos com senha `senha123`):
`operador.cadastro` (cadastro), `operador.vendas` (vendas), `operador.mecanico`
(mecanico), `operador.admin` (admin).

## Notas para o frontend

- **Cadeia normalizada Marca → Modelo → Veículo:** `veiculos.marca_id` e
  `modelos.marca_id` são FKs → `marcas` (`ON DELETE SET NULL`). `marca_id` é
  obrigatório no veículo e opcional no modelo. `b.veiculos.listar()` e
  `b.modelos.listar()` já devolvem `marca_nome` (e o veículo também `modelo_nome`)
  por JOIN. Use `b.marcas.listar()` para os seletores. O `veiculo_cliente` (carro
  do cliente, usado em OS) mantém `marca` como texto livre — é outra entidade.
- **Vendas:** a tela monta um carrinho de itens (`produto_id`, `tipo_produto`,
  `quantidade`, `preco_unitario`) e chama `b.vendas.registrar_venda(tipo, itens)`,
  onde o `tipo` é `veiculo`, `peca` ou `mista` (deduzido dos itens). O preço
  unitário é pré-preenchido a partir do produto, mas pode ser editado.
- `Financeiro` é **derivado** de vendas + ordens de serviço (receitas) e salários
  de funcionários (despesas); não há tabela de lançamentos manuais.
- Mudanças de schema exigem banco novo: como o schema usa `CREATE TABLE IF NOT
  EXISTS`, alterações em tabelas já criadas não migram automaticamente — recrie o
  `concessionaria.db` (ou migre manualmente) ao evoluir o schema.
- `Relatórios` cobre as entidades principais (`backend.relatorios.listar_disponiveis()`),
  com saída em `dict`, CSV (`exportar_csv`) ou texto de console (`formatar_console`).
