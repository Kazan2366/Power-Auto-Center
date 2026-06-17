# Concessionária — Normalização e Correção (Design)

**Data:** 2026-06-10
**Status:** Aprovado (Plano A)
**Stack alvo:** Python 3.14 · Flet (UI) · SQLite (`concessionaria.db`)

## 1. Contexto e problema

O projeto `CONCESSONARIA` é um sistema desktop de gerenciamento de concessionária (port de um
projeto PowerAutomate para Python/Flet, usado para testes). Hoje ele **não funciona**: foi montado
com três arquiteturas incompatíveis misturadas. As inconsistências encontradas:

1. **Três esquemas de banco contraditórios:**
   - `database/connection.py` → SQLite, tabelas no plural (`clientes`, `veiculos`, `vendas`,
     `venda_itens`, `estoque_veiculos`, `estoque_pecas`...). É o que roda de fato (cria o `.db`).
   - `database/sql/create_database.sql` → MySQL, tabelas no singular (`cliente`, `veiculo`, `venda`).
   - Os models → sintaxe MySQL (`%s`, `with connection.cursor() as cursor`) referenciando tabelas
     que não existem (`vendas_veiculos`, `vendas_pecas`, coluna `quantidade` em `veiculos`).
2. **Camadas não se encaixam:** `ClienteController` faz `Cliente()` sem args (o construtor exige 4) e
   chama `inserir_cliente()` (método inexistente); `Venda()`/`Estoque()` criados sem conexão; o
   `login_view` chama `DashboardView(connection, role, username)` (3 args) e `.run()`, mas
   `DashboardView` aceita só `page` e tem apenas `.build()`.
3. **Navegação Flet incorreta:** cada tela tenta abrir um novo `ft.app()`.
4. **APIs de Flet quebradas/antigas:** `Chart`/`PieChart` importados do topo do módulo, `TextColumn`
   inexistente, `icons`/`DataCell` mal importados.
5. **Dependências faltando:** `flet` e `matplotlib` não instalados; `requirements.txt` lista PyMySQL
   (irrelevante para SQLite).
6. **Lixo:** `main.py` tem `from socket import create_connection`; README descreve MySQL.

## 2. Objetivo

App CRUD **100% funcional** sobre uma **arquitetura MVC única e coerente** (Flet + SQLite), fiel à
estrutura de pastas documentada no README, com **menu restrito por perfil** e **gráficos nativos do
Flet**. Trabalho dividido em fases, começando pela **estrutura/normalização da camada de dados**.

## 3. Decisões (confirmadas com o usuário)

- **Escopo:** CRUD completo de todas as entidades do README (cadastrar, listar, editar, excluir).
- **Banco:** apenas SQLite. Fonte única de verdade = schema do `connection.py`.
- **Perfis:** menu restrito por papel (`cadastro`, `vendas`, `mecanico`).
- **Gráficos:** nativos do Flet (PieChart/BarChart/LineChart). **matplotlib é removido** do projeto.
- **Abordagem:** A (re-alinhar MVC mantendo a estrutura de pastas), com helpers compartilhados em
  `components/` para reduzir repetição entre as 9 entidades.

## 4. Arquitetura alvo

### 4.1 Fluxo de dependências (injeção de conexão)

```
main.py
  └─ cria 1 connection (sqlite3) e a injeta
       └─ App/MainShell (Flet, único ft.app)
            └─ View (build() -> Control)
                 └─ Controller(connection)
                      └─ Model(connection)  ── SQL com "?", sqlite3.Row
```

- A conexão é criada uma vez no `main.py` e passada para baixo. SQLite num app desktop de usuário
  único com callbacks no thread principal do Flet → uma conexão compartilhada é adequada.
- Todos os models recebem `connection` no construtor (DAO). Sem `with connection.cursor() as ...`
  (padrão PyMySQL); usar `cursor = connection.cursor()` + `connection.commit()`.

### 4.2 Schema canônico (SQLite — mantém o de `connection.py`)

| Tabela | Colunas-chave |
|---|---|
| `users` | id, username (unique), password, role |
| `clientes` | id, nome, cpf (unique), telefone, email |
| `modelos` | id, nome, numero_serie (unique) |
| `veiculos` | id, marca, modelo_id→modelos, chassi (unique), ano_fabricacao, cor, preco |
| `categorias_peca` | id, nome, descricao |
| `pecas` | id, nome, categoria_id→categorias_peca, preco |
| `veiculo_cliente` | id, cliente_id→clientes, marca, placa (unique), ano |
| `estoque_veiculos` | veiculo_id (PK)→veiculos, quantidade |
| `estoque_pecas` | peca_id (PK)→pecas, quantidade |
| `vendas` | id, data, tipo, total |
| `venda_itens` | id, venda_id→vendas, produto_id, tipo_produto, quantidade, preco_unitario |
| `ordem_servico` | id, cliente_id→clientes, veiculo_cliente_id→veiculo_cliente, tipo_servico, entrada, saida, valor_mao_de_obra, valor_peca |

- `database/sql/create_database.sql` será **reescrito como espelho SQLite** deste schema (documentação).
  O runtime continua criando as tabelas via `init_database()`.

### 4.3 Camada de Views e navegação

- **Um único `ft.app(target=app.main)`.** `main.py` instancia o `App`/`LoginView`.
- `LoginView` renderiza o formulário na `page`. No sucesso, chama o `MainShell` passando
  `connection`, `role`, `username`.
- **`MainShell`** = `NavigationRail` (destinos filtrados pelo `role`) + `Container` de conteúdo.
  Selecionar um destino instancia a View correspondente e coloca `view.build()` no container
  (substituindo o conteúdo). Botão de logout volta ao `LoginView`.
- **Cada View** é uma classe com `__init__(self, page, connection)` e `build(self) -> ft.Control`.
  Não chama `ft.app`. Operações CRUD atualizam o `DataTable` local via `control.update()`.

### 4.4 Mapa perfil → telas

| Perfil | Destinos no menu |
|---|---|
| `cadastro` | Dashboard, Clientes, Modelos, Veículos, Categorias, Peças, Estoque |
| `vendas` | Dashboard, Vendas |
| `mecanico` | Dashboard, Ordens de Serviço |

As telas de Vendas e Ordem de Serviço leem clientes/veículos/peças (para dropdowns) independentemente
do menu de cadastro estar visível para aquele perfil.

### 4.5 Dashboard

- Indicadores numéricos: total de vendas (soma `vendas.total`), veículos em estoque
  (soma `estoque_veiculos.quantidade`), OS abertas (`ordem_servico` com `saida` nula).
- Gráficos nativos do Flet: distribuição de vendas (Pie), estoque por veículo (Bar), tendência de
  vendas no tempo (Line). Dados vindos dos models — sem matplotlib.

## 5. Componentes compartilhados (`view/components/`)

- `table.py` — helper para construir `DataTable` a partir de colunas + lista de dicts, com callback de
  editar/excluir por linha. Reescrito para a API atual do Flet (`ft.DataColumn(ft.Text(...))`).
- `forms.py` — helpers de formulário reaproveitáveis (campo + validação simples). Reescrito para
  `ft.Icons`/API atual.
- `layout.py` — AppBar/containers utilitários, atualizado para a API atual.

## 6. Plano em fases

**Fase 1 — Estrutura e normalização da camada de dados (primeiro):**
- Unificar schema (confirmar `connection.py`, reescrever `create_database.sql` como SQLite).
- Reescrever os 9 models como DAOs SQLite (`?`, `Row`, conexão injetada) batendo no schema.
- Reescrever os 9 controllers com assinaturas alinhadas (recebem `connection`, CRUD + validação).
- Limpar `main.py` (remover import lixo) e `requirements.txt` (só `flet`).
- Testes `pytest` da camada model+controller (CRUD round-trip em SQLite temporário).

**Fase 2 — Views e navegação:**
- `MainShell` com `NavigationRail` filtrado por perfil + área de conteúdo.
- `LoginView` integrado ao shell (sem múltiplo `ft.app`).
- Reescrever as views CRUD (Clientes, Modelos, Veículos, Categorias, Peças, Estoque, Vendas, OS) com
  `build() -> Control`.
- Componentes (`table.py`, `forms.py`, `layout.py`) atualizados para a API atual do Flet.

**Fase 3 — Dashboard e gráficos:**
- Indicadores + gráficos nativos do Flet. Remover `matplotlib`/`utils/charts.py` antigo.

**Fase 4 — Acabamento:**
- Atualizar README (SQLite, instalação, perfis). Smoke test rodando o app.

## 7. Estratégia de testes

- **Unitários (pytest):** models e controllers contra SQLite temporário (fixture cria schema, roda
  CRUD round-trip, valida unicidade/validações). Camada principal de confiança.
- **Manual:** views e navegação verificadas rodando `python main.py` (login por perfil, navegação,
  cadastro/edição/exclusão, dashboard).

## 8. Fora de escopo (YAGNI)

- Hash de senha / segurança real (mantém usuários-semente de teste).
- Relatórios/exportação, multiusuário concorrente, migrações de schema versionadas.
- matplotlib e qualquer geração de gráfico estático.

## 9. Arquivos impactados

- **Reescritos:** todos em `model/`, `controller/`, `view/` (incl. `components/`), `main.py`,
  `database/sql/create_database.sql`, `requirements.txt`, `README.md`, `utils/charts.py` (→ removido
  ou substituído por helper de dados de gráfico).
- **Mantido/ajustado:** `database/connection.py` (schema canônico; pequenos ajustes se necessário).
- **Novos:** `tests/` (pytest), helpers em `components/`.
