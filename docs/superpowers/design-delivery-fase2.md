# Concessionária — Fase 2: Design Delivery (UI Flet)

**Autora:** Diana Desenha (UX/UI + frontend) · OpenSquad
**Data:** 2026-06-10
**Status:** Design entregue (somente design — implementação é a execução da Fase 2)
**Stack alvo:** Python 3.14 · Flet (Flutter por baixo) · SQLite (via controllers do Caio)

> Escopo deste documento: **DESIGN APENAS**. Nenhum código de implementação Flet. As referências a
> `ft.*` são notas de mapeamento (qual widget/token usar), não implementação. Wireframe textual vem
> sempre antes de qualquer descrição de widget.

---

## 0. Direção estética (passo ZERO)

**Ponto de vista escolhido: "Balcão de oficina — ferramenta de turno, não vitrine."**

Layout de **densidade operacional**: tabela é a protagonista (o funcionário passa o turno olhando
linhas), formulário fica encostado à esquerda como uma bancada fixa, e a cor só aparece para
**sinalizar estado** (salvo, erro, OS aberta) — nunca para decorar. Superfície clara levemente
acinzentada (reduz brilho em jornada longa sob luz de loja), um **azul-petróleo** sóbrio como cor de
ação (lê bem em monitor barato de balcão e contrasta forte sobre claro), e um **âmbar** reservado
para "atenção/aberto". Cantos pouco arredondados (4px) e tipografia de sistema legível à distância
de um balcão.

**Racional (1 linha):** funcionário de cadastro/vendas/oficina precisa ler dados rápido e agir sem
erro — então densidade + cor-só-para-estado + alvos clicáveis grandes vencem qualquer estética de
vitrine.

Anti-slop: nada de "moderno/clean/minimalista". As decisões concretas estão nos tokens abaixo
(espaçamento de 8px, paleta nomeada com hex, 3 pesos tipográficos, raio 4px).

---

## 1. Identidade visual (tokens)

### 1.1 Paleta nomeada (todos com hex)

| Token | Nome | Hex | Uso |
|---|---|---|---|
| `primary` | Petróleo | `#0F6E8C` | Botões de ação, item ativo do NavigationRail, foco, links |
| `primary-hover` | Petróleo escuro | `#0B5469` | Estado hover/pressed do primário |
| `on-primary` | Branco | `#FFFFFF` | Texto/ícone sobre `primary` |
| `surface` | Névoa | `#F4F6F7` | Fundo geral do app (janela) |
| `surface-card` | Branco | `#FFFFFF` | Cartões, formulário, cabeçalho de tabela |
| `surface-rail` | Ardósia | `#1E2A30` | Fundo do NavigationRail (faixa lateral) |
| `on-rail` | Cinza-claro | `#C4CED3` | Ícones/labels inativos no rail |
| `on-rail-active`| Branco | `#FFFFFF` | Ícone/label ativo no rail (sobre destaque petróleo) |
| `border` | Traço | `#D5DCDF` | Bordas de campo, divisórias de linha da tabela |
| `text` | Grafite | `#1A2226` | Texto primário (títulos, valores) |
| `text-muted` | Cinza-médio | `#5B686E` | Rótulos, placeholders, metadados |
| `success` | Verde-sinal | `#2E7D4F` | SnackBar de salvo/excluído, badge "fechada" |
| `error` | Vermelho-sinal | `#B3261E` | Validação, SnackBar de erro, ação excluir |
| `warning` | Âmbar | `#B26A00` | Badge "OS aberta", avisos de estoque baixo |

Cores de série dos gráficos (categóricas, distinguíveis e coerentes com a paleta):
`#0F6E8C` (petróleo) · `#B26A00` (âmbar) · `#2E7D4F` (verde) · `#6A4C93` (uva) · `#8C5A2B` (terra).

### 1.2 Escala de espaçamento (base 8, numérica)

| Token | px | Uso típico |
|---|---|---|
| `space-1` | 4 | gap interno (ícone↔label), padding de chip |
| `space-2` | 8 | gap entre campos do formulário |
| `space-3` | 12 | padding de célula de tabela |
| `space-4` | 16 | padding de Card, padding de conteúdo |
| `space-5` | 24 | gap entre blocos (formulário ↔ tabela) |
| `space-6` | 32 | margem de página / gutters do dashboard |

### 1.3 Tipografia

- **Família:** stack de sistema — `"Segoe UI", Roboto, system-ui` (sem download; legível em monitor
  de balcão Windows). Em Flet: `theme.font_family`.
- **3 pesos:** Regular 400 (corpo/tabela) · Medium 500 (rótulos, cabeçalho de coluna, botão) ·
  SemiBold 600 (títulos de tela, valores grandes do MetricCard).
- **Escala (size / peso):**
  - `display` 28 / 600 — valor numérico do MetricCard
  - `title` 20 / 600 — título da tela ("Clientes", "Vendas")
  - `subtitle` 16 / 500 — rótulo do MetricCard, cabeçalho de seção
  - `body` 14 / 400 — texto de tabela e de campo
  - `label` 13 / 500 — rótulo de campo, header de coluna (uppercase opcional)
  - `caption` 12 / 400 — texto auxiliar, contador de itens

### 1.4 Raio de borda e elevação

- `radius` = **4px** (campos, botões, chips). `radius-card` = **8px** (Cards/MetricCard).
- Elevação: Cards com sombra sutil (`elevation 1`); o rail é plano (sem sombra, só cor).

### 1.5 Mapeamento para `ft.Theme` / `ColorScheme`

Centralizar tudo num módulo `view/theme.py` (constantes) + um `ft.Theme` aplicado em `page.theme`:

| Token de design | Destino no Flet |
|---|---|
| `primary` / `on-primary` / `error` | `ColorScheme(primary=..., on_primary=..., error=...)` |
| `surface` | `page.bgcolor` |
| `surface-card` | `ColorScheme(surface=..., on_surface=text)` e `bgcolor` de `ft.Card` |
| `success` / `warning` | constantes próprias (o ColorScheme não tem slot semântico nativo) |
| família + pesos | `Theme(font_family=...)`; pesos via `ft.FontWeight.W_400/500/600` no `ft.Text` |
| `radius` | `ft.RoundedRectangleBorder(radius=4)` / `border_radius=8` no Card |
| espaçamento | constantes `SPACE = {1:4, 2:8, ...}` usadas em `padding`/`spacing` |
| cores de série | lista `CHART_COLORS` consumida por Pie/Bar/Line |

> Os tokens viram **um único módulo importável** — nenhum hex hardcoded nas views. Isso é o
> "design system" da Fase 2.

---

## 2. Inventário de componentes reutilizáveis

Princípio "Componente > tela": as 8 telas CRUD são quase 100% montadas por `AppShell + CrudForm +
CrudTable`. Cada componente abaixo lista propósito, entradas (props) e qual controller consome.

> Caminhos: estes mapeiam para `view/components/` (`layout.py`, `forms.py`, `table.py`) já existentes
> no projeto, atualizados para a API atual do Flet.

### 2.1 `AppShell` — `components/layout.py`
- **Propósito:** moldura única (NavigationRail filtrado por `role` + área de conteúdo trocável +
  barra superior com usuário/logout). Um só `ft.app`; trocar de destino só substitui o conteúdo.
- **Entradas:** `page`, `connection`, `role`, `username`, `destinos: list[Destino]`
  (cada `Destino` = `{label, icon, view_factory}`), `on_logout`.
- **Consome:** nenhum controller diretamente — apenas instancia a View do destino selecionado
  passando `(page, connection)`. O filtro por `role` usa o **Mapa perfil→telas** (seção 5).

### 2.2 `LoginCard` — `components/layout.py` (usado por `login_view.py`)
- **Propósito:** cartão central de autenticação; em erro mostra mensagem inline; em sucesso entrega
  ao `AppShell`.
- **Entradas:** `page`, `connection`, `on_success(role, username)`.
- **Consome:** `LoginController.authenticate(username, password)` → `{success, role, username}` ou
  `{success: False, message}`.

### 2.3 `CrudForm` — `components/forms.py`
- **Propósito:** bancada de entrada genérica: campos + validação inline + botões **Salvar** /
  **Limpar**. Alterna entre modo "novo" e "editar id=X" (preenchido a partir de uma linha da tabela).
- **Entradas:** `campos: list[Campo]` (cada `Campo` = `{name, label, tipo: texto|numero|dropdown,
  obrigatorio, options?}`), `on_submit(values: dict)`, `on_clear`, `valores_iniciais?`.
- **Validação:** obrigatórios marcados; mensagem sob o campo em `error`. Os `name` **batem
  exatamente** com os parâmetros dos controllers (nome/cpf/telefone/email, marca/modelo_id/chassi/
  ano_fabricacao/cor/preco, etc.).
- **Consome:** indireto — repassa `values` para o `cadastrar`/`atualizar` do controller dono da tela.

### 2.4 `CrudTable` — `components/table.py`
- **Propósito:** `DataTable` genérico a partir de `colunas + list[dict]`, com **coluna de ações por
  linha** (Editar ✏️ / Excluir 🗑️) e estado vazio ("Nenhum registro").
- **Entradas:** `colunas: list[{key, label, fmt?}]`, `linhas: list[dict]`,
  `on_edit(row)`, `on_delete(row)`.
- **Consome:** indireto — recebe a lista já vinda do `listar()` do controller dono da tela; `on_delete`
  chama `excluir(id)` do controller.

### 2.5 `MetricCard` — `components/layout.py`
- **Propósito:** indicador único do dashboard (rótulo + valor grande + ícone). Sem interação.
- **Entradas:** `label`, `valor` (já formatado), `icon`, `cor_accent` (default `primary`).
- **Consome:** indireto — recebe o número pronto. Fontes: `VendaController.total_vendas()`,
  `EstoqueController.total_veiculos()`, `OrdemServicoController.total_abertas()`.

### 2.6 `ChartCard` — `components/layout.py`
- **Propósito:** moldura padrão para um gráfico nativo do Flet (título + `PieChart`/`BarChart`/
  `LineChart`), aplicando `CHART_COLORS` e raio de card.
- **Entradas:** `titulo`, `tipo: pie|bar|line`, `dados` (séries já calculadas).
- **Consome:** indireto — dados de venda/estoque já agregados pelos controllers/models (Fase 3
  formaliza os agregados; aqui o componente já fica pronto para recebê-los).

### 2.7 `ItemEditor` (específico de Vendas) — dentro de `venda_view.py`
- **Propósito:** linha de item de venda (produto + tipo + quantidade + preço unitário + subtotal) com
  **+ adicionar** / **remover**, recalculando o total ao vivo.
- **Entradas:** lista mutável de itens `{produto_id, tipo_produto, quantidade, preco_unitario}`,
  `on_change(total)`.
- **Consome:** monta exatamente o `itens=[dict...]` que `VendaController.registrar_venda(tipo, itens)`
  espera; lê produtos de `VeiculoController.listar()` / `PecaController.listar()` para os dropdowns.

### 2.8 `SnackFeedback` — helper em `components/layout.py`
- **Propósito:** feedback consistente (sucesso verde / erro vermelho) após qualquer ação CRUD.
  Traduz `ValueError` (validação) e `sqlite3.IntegrityError` (ex.: CPF/placa/chassi duplicado) em
  mensagem amigável.
- **Entradas:** `page`, `mensagem`, `tipo: sucesso|erro`.
- **Consome:** indireto — chamado pelas views ao redor das chamadas de controller.

---

## 3. Wireframes ASCII

> Regra da casa: wireframe primeiro. Todas as telas vivem **dentro do `AppShell`**, exceto Login.

### 3.1 Login

```
+--------------------------------------------------------------------------+
|                                                                          |
|                                                                          |
|                  +----------------------------------+                    |
|                  |        CONCESSIONÁRIA            |   <- title 20/600   |
|                  |        Acesso ao sistema         |   <- subtitle muted |
|                  |                                  |                    |
|                  |  Usuário                         |                    |
|                  |  [______________________________]|   <- TextField     |
|                  |  Senha                           |                    |
|                  |  [•••••••••••••••••••••••••••••• ]|   (password)       |
|                  |                                  |                    |
|                  |  (!) Usuário ou senha inválidos! |   <- error inline  |
|                  |                                  |     (só se falhar) |
|                  |  [        ENTRAR (petróleo)     ]|   <- ElevatedButton |
|                  +----------------------------------+                    |
|                                                                          |
|        Usuários de teste (ambiente de demonstração):                     |
|        +------------------+------------+------------------------+        |
|        | Usuário          | Senha      | Perfil                 |        |
|        +------------------+------------+------------------------+        |
|        | Cadastrar23      | 4590       | cadastro               |        |
|        | Vendendor13      | 8955       | vendas                 |        |
|        | Mecânico         | 7675       | mecanico               |        |
|        +------------------+------------+------------------------+        |
|                                                                          |
+--------------------------------------------------------------------------+
```
Fluxo: `ENTRAR` → `LoginController.authenticate(username, password)`. Sucesso → monta `AppShell(role,
username)`. Falha → exibe `message` inline (token `error`). Enter no campo Senha também envia.

### 3.2 AppShell (NavigationRail muda por perfil)

Faixa lateral `surface-rail` (ardósia), item ativo em `primary` (petróleo). Topo com usuário + logout.

```
PERFIL = cadastro
+-------------+----------------------------------------------------------+
|  CONCESS.   |  Clientes                         Cadastrar23 (cadastro) |
|             |                                              [ Sair ⎋ ]  |
| [▣] Dashbrd |----------------------------------------------------------|
| [▣] Clientes|                                                          |
| [ ] Modelos |   (conteúdo da tela selecionada — ver 3.3)               |
| [ ] Veículos|                                                          |
| [ ] Categ.  |                                                          |
| [ ] Peças   |                                                          |
| [ ] Estoque |                                                          |
|             |                                                          |
|             |                                                          |
+-------------+----------------------------------------------------------+

PERFIL = vendas                         PERFIL = mecanico
+-------------+--------------+          +-------------+--------------+
| [▣] Dashbrd |              |          | [▣] Dashbrd |              |
| [ ] Vendas  |  conteúdo    |          | [ ] Ordens  |  conteúdo    |
|             |              |          |   de Serviço|              |
|             |              |          |             |              |
+-------------+--------------+          +-------------+--------------+
```
`[▣]` = destino ativo (petróleo). O conjunto de destinos é decidido pelo Mapa da seção 5.

### 3.3 CRUD representativo — Clientes (form + tabela + ações + SnackBar)

Campos batem o contrato `ClienteController.cadastrar(nome, cpf, telefone, email)`.

```
+----------------------------------------------------------------------------+
|  Clientes                                          Cadastrar23 (cadastro)  |
|                                                              [ Sair ⎋ ]    |
+----------------------------------------------------------------------------+
|  +--------------------------+   +---------------------------------------+  |
|  |  NOVO CLIENTE            |   |  Buscar: [_______________]            |  |
|  |  ----------------------  |   +----+--------------+--------+----------+ |  |
|  |  Nome *                  |   | ID | Nome         | CPF    | Ações    | |  |
|  |  [____________________]  |   +----+--------------+--------+----------+ |  |
|  |  CPF *                   |   | 1  | Ana Maria    | 111... | ✏️  🗑️  | |  |
|  |  [____________________]  |   | 2  | Bruno Costa  | 222... | ✏️  🗑️  | |  |
|  |  Telefone                |   | 3  | Carla Dias   | 333... | ✏️  🗑️  | |  |
|  |  [____________________]  |   +----+--------------+--------+----------+ |  |
|  |  Email                   |   |  3 registros                          | |  |
|  |  [____________________]  |   +---------------------------------------+  |
|  |                          |                                             |
|  |  [ SALVAR ] [ LIMPAR ]   |                                             |
|  +--------------------------+                                             |
+----------------------------------------------------------------------------+
|  [✓ Cliente salvo com sucesso.]   <- SnackBar verde (success), 3s          |
+----------------------------------------------------------------------------+
```
- **Salvar** (modo novo) → `cadastrar(nome, cpf, telefone, email)`; (modo editar) →
  `atualizar(id, nome, cpf, telefone, email)`. Recarrega via `listar()` e dá SnackBar verde.
- **✏️ Editar** → `buscar(id)` preenche o `CrudForm` (vira modo editar id=X).
- **🗑️ Excluir** → confirma → `excluir(id)` → SnackBar verde + recarrega.
- **Erro:** `ValueError` ("Nome é obrigatório.") vira mensagem inline no campo; CPF duplicado
  (`IntegrityError`) vira SnackBar vermelho "CPF já cadastrado."

> As demais telas CRUD (Modelos, Veículos, Categorias, Peças, Estoque, Veículo-Cliente) usam **este
> mesmo layout**, só trocando o conjunto de `campos`/`colunas`. Ex.: Veículos = campos
> `marca/modelo_id(dropdown→Modelos)/chassi/ano_fabricacao/cor/preco`.

### 3.4 Vendas (múltiplos itens → total ao vivo)

Monta o `itens=[{produto_id, tipo_produto, quantidade, preco_unitario}]` de `registrar_venda`.

```
+----------------------------------------------------------------------------+
|  Vendas                                            Vendendor13 (vendas)    |
+----------------------------------------------------------------------------+
|  Tipo da venda: ( ) Veículo  ( ) Peça  (•) Mista                           |
|                                                                            |
|  ITENS DA VENDA                                                            |
|  +------------+-----------+--------+-------------+-----------+-----+        |
|  | Produto    | Tipo      | Qtd    | Preço unit. | Subtotal  |     |        |
|  +------------+-----------+--------+-------------+-----------+-----+        |
|  | [Civic  ▾] | [veículo▾]| [ 1 ]  | [ 90000,00 ]| 90.000,00 | [🗑]|        |
|  | [Pastilha▾]| [peça   ▾]| [ 2 ]  | [   100,00 ]|    200,00 | [🗑]|        |
|  +------------+-----------+--------+-------------+-----------+-----+        |
|  [ + Adicionar item ]                                                      |
|                                                                            |
|                                       +---------------------------------+  |
|                                       |  TOTAL:        R$ 90.200,00      |  |
|                                       |  (display 28/600, petróleo)     |  |
|                                       +---------------------------------+  |
|                                                                            |
|  [        REGISTRAR VENDA (petróleo)        ]   [ Limpar ]                 |
+----------------------------------------------------------------------------+
|  [✓ Venda registrada — total R$ 90.200,00]   <- SnackBar success           |
+----------------------------------------------------------------------------+
```
- Dropdown "Produto" carrega de `VeiculoController.listar()` (tipo=veículo) ou
  `PecaController.listar()` (tipo=peça); `preco_unitario` pré-preenche com o `preco` do produto.
- Total = Σ(qtd × preço) recalculado a cada mudança (espelha o cálculo do `VendaController`).
- **Registrar venda** → `registrar_venda(tipo, itens)`. `itens` vazio → o botão fica desabilitado e
  o controller também barra com `ValueError`.

### 3.5 Ordem de Serviço (cliente → veículo do cliente → abrir/fechar)

Contrato: `OrdemServicoController.cadastrar(cliente_id, veiculo_cliente_id, tipo_servico,
valor_mao_de_obra, valor_peca)` · `.fechar(os_id)` · `.total_abertas()`.

```
+----------------------------------------------------------------------------+
|  Ordens de Serviço                                  Mecânico (mecanico)    |
+----------------------------------------------------------------------------+
|  +----------------------------+   OS abertas no momento: 2  (badge âmbar)  |
|  |  NOVA OS                   |                                            |
|  |  ------------------------  |   +---+----------+-----------+--------+---+ |
|  |  Cliente *                 |   |ID | Cliente  | Veículo   | Status |   | |
|  |  [ Ana Maria         ▾]    |   +---+----------+-----------+--------+---+ |
|  |  Veículo do cliente *      |   | 1 | Ana Maria| Fiat ABC..| ABERTA | ⊗ | |
|  |  [ Fiat ABC1234      ▾]    |   | 2 | B. Costa | VW XYZ..  | ABERTA | ⊗ | |
|  |   (filtra por cliente via  |   | 3 | C. Dias  | GM JKL..  | fechada|   | |
|  |    listar_por_cliente)     |   +---+----------+-----------+--------+---+ |
|  |  Tipo de serviço           |                                            |
|  |  [____________________]    |   Legenda: ABERTA=âmbar  fechada=verde     |
|  |  Mão de obra (R$)          |   ⊗ = Fechar OS (saida=agora)              |
|  |  [____________________]    |                                            |
|  |  Peças (R$)                |                                            |
|  |  [____________________]    |                                            |
|  |  [ ABRIR OS ] [ LIMPAR ]   |                                            |
|  +----------------------------+                                            |
+----------------------------------------------------------------------------+
|  [✓ OS aberta para Ana Maria]   <- SnackBar success                        |
+----------------------------------------------------------------------------+
```
- Dropdown **Cliente** ← `ClienteController.listar()`. Ao escolher, dropdown **Veículo** recarrega via
  `VeiculoClienteController.listar_por_cliente(cliente_id)` (só os veículos daquele cliente).
- **ABRIR OS** → `cadastrar(...)` (entrada=agora, saída=NULL ⇒ status ABERTA âmbar).
- **⊗ Fechar** → `fechar(os_id)` (saída=agora ⇒ status fechada verde). Contador no topo usa
  `total_abertas()`.

### 3.6 Dashboard (3 MetricCards + Pie/Bar/Line)

```
+----------------------------------------------------------------------------+
|  Dashboard                                          Cadastrar23 (cadastro) |
+----------------------------------------------------------------------------+
|  +------------------+  +------------------+  +------------------------+     |
|  | 💰 Total vendas  |  | 🚗 Veíc. estoque |  | 🔧 OS abertas         |     |
|  |                  |  |                  |  |                       |     |
|  |  R$ 90.200,00    |  |       12         |  |        2              |     |
|  |  (display 28/600)|  |  (display)       |  |  (display, âmbar)     |     |
|  +------------------+  +------------------+  +------------------------+     |
|                                                                            |
|  +-----------------------------+   +-----------------------------------+   |
|  | Distribuição de vendas      |   | Estoque por veículo               |   |
|  |        (PieChart)           |   |        (BarChart)                 |   |
|  |          _____              |   |   █                               |   |
|  |        /  ▓▓▓  \   ▓ Veíc.  |   |   █    █                          |   |
|  |       | ▓▓░░░░ |  ░ Peças   |   |   █    █    █     █               |   |
|  |        \ ░░░░ /             |   |  Civic Onix Gol  HB20             |   |
|  +-----------------------------+   +-----------------------------------+   |
|                                                                            |
|  +----------------------------------------------------------------------+  |
|  | Tendência de vendas (LineChart)                                      |  |
|  |   R$ |                                   •                           |  |
|  |      |                 •        •      /                             |  |
|  |      |       •      /     \   /                                      |  |
|  |      |  •  /                                                         |  |
|  |      +--------------------------------------------------------       |  |
|  |        jan   fev   mar   abr   mai   jun                             |  |
|  +----------------------------------------------------------------------+  |
+----------------------------------------------------------------------------+
```
- MetricCards: `total_vendas()` (formatado R$), `total_veiculos()`, `total_abertas()` (âmbar pois é
  "atenção"). Gráficos: Pie = mix veículo×peça (de `venda_itens`), Bar = `listar_veiculos()`
  (quantidade por veículo), Line = vendas no tempo (de `vendas.data/total`). Cores = `CHART_COLORS`.

---

## 4. Mapa perfil → telas (confirmado)

Idêntico ao spec §4.4. Cada perfil só vê seus destinos no `NavigationRail`; **Dashboard sempre presente**.

| Perfil | Destinos no NavigationRail (ordem) |
|---|---|
| `cadastro` | Dashboard · Clientes · Modelos · Veículos · Categorias · Peças · Estoque |
| `vendas` | Dashboard · Vendas |
| `mecanico` | Dashboard · Ordens de Serviço |

Observações:
- Vendas e OS **leem** clientes/veículos/peças para dropdowns mesmo sem o menu de cadastro visível
  (consomem `listar()` dos controllers diretamente, não dependem do destino estar no rail).
- A entidade `Veículo-Cliente` (placas do cliente) é gerida **dentro da tela de OS** (cadastro do
  veículo do cliente ao abrir a OS) — não recebe destino próprio no rail para manter o menu enxuto;
  seu controller (`VeiculoClienteController`) é consumido pela tela de OS.

---

## 5. Acessibilidade (WCAG AA — alvo 4.5:1 texto normal)

Contrastes calculados dos pares texto/fundo da paleta:

| Par | Fundo | Texto/elemento | Ratio | Veredito |
|---|---|---|---|---|
| Corpo sobre app | `#F4F6F7` Névoa | `#1A2226` Grafite | **15.6:1** | AAA ✓ |
| Corpo sobre card | `#FFFFFF` Branco | `#1A2226` Grafite | **16.6:1** | AAA ✓ |
| Texto auxiliar | `#FFFFFF` Branco | `#5B686E` Cinza-médio | **5.3:1** | AA ✓ (texto normal) |
| Botão primário | `#0F6E8C` Petróleo | `#FFFFFF` Branco | **4.6:1** | AA ✓ (texto normal) |
| Item ativo no rail | `#0F6E8C` Petróleo | `#FFFFFF` Branco | **4.6:1** | AA ✓ |
| Rail inativo | `#1E2A30` Ardósia | `#C4CED3` Cinza-claro | **8.4:1** | AAA ✓ |
| Erro/validação | `#FFFFFF` Branco | `#B3261E` Vermelho-sinal | **5.7:1** | AA ✓ |
| Sucesso (SnackBar) | `#2E7D4F` Verde-sinal | `#FFFFFF` Branco | **4.6:1** | AA ✓ |
| Aviso "OS aberta" | `#FFFFFF` Branco | `#B26A00` Âmbar | **4.6:1** | AA ✓ |

> O `text-muted` `#5B686E` (5.3:1) deve ser usado **só em ≥14px** (corpo normal), nunca em 12px de
> corpo sobre branco como informação crítica — em `caption` 12px crítico, usar `text` Grafite.

Demais requisitos:
- **Foco visível:** anel de foco `primary` 2px em campos/botões/itens do rail (`ft.FocusBorder` /
  borda no estado focado). Nunca remover o indicador de foco.
- **Teclado:** Tab navega campos → Salvar; Enter envia o formulário (e o login). NavigationRail
  navegável por teclado; ação de excluir exige confirmação (evita exclusão acidental por foco).
- **Alvos clicáveis:** mínimo **40×40px** para ícones de ação (Editar/Excluir/Fechar OS) e altura de
  botão ≥40px — coerente com uso de balcão (clique rápido, às vezes touch).
- **Não-cor:** estado nunca é só cor — "ABERTA/fechada" tem **texto** além do badge; erro tem ícone
  `(!)` além do vermelho; ativo no rail tem realce de fundo além da cor do ícone.
- **Densidade:** linha de tabela com `space-3` (12px) vertical para legibilidade sem rolagem excessiva.

---

## 6. Dependências do Caio (componente/tela → controller/método)

Mapa sem ambiguidade para a Fase 2 "amarrar". Assinaturas conforme o plano da Fase 1.

| Componente / Tela | Controller.método consumido |
|---|---|
| `LoginCard` / Login | `LoginController.authenticate(username, password)` → `{success, role, username, message?}` |
| `AppShell` / shell | — (instancia views; filtra rail pelo `role`) |
| Clientes (CRUD) | `ClienteController.cadastrar(nome, cpf, telefone, email)` · `listar()` · `buscar(id)` · `atualizar(id, nome, cpf, telefone, email)` · `excluir(id)` |
| Modelos (CRUD) | `ModeloController.cadastrar(nome, numero_serie)` · `listar()` · `buscar(id)` · `atualizar(id, nome, numero_serie)` · `excluir(id)` |
| Veículos (CRUD) | `VeiculoController.cadastrar(marca, modelo_id, chassi, ano_fabricacao, cor, preco)` · `listar()` · `buscar(id)` · `atualizar(id, marca, modelo_id, chassi, ano_fabricacao, cor, preco)` · `excluir(id)` ; dropdown modelo ← `ModeloController.listar()` |
| Categorias (CRUD) | `CategoriaPecaController.cadastrar(nome, descricao)` · `listar()` · `buscar(id)` · `atualizar(id, nome, descricao)` · `excluir(id)` |
| Peças (CRUD) | `PecaController.cadastrar(nome, categoria_id, preco)` · `listar()` · `buscar(id)` · `atualizar(id, nome, categoria_id, preco)` · `excluir(id)` ; dropdown categoria ← `CategoriaPecaController.listar()` |
| Estoque (CRUD) | `EstoqueController.definir_veiculo(veiculo_id, quantidade)` · `definir_peca(peca_id, quantidade)` · `buscar_veiculo(id)` · `buscar_peca(id)` · `listar_veiculos()` · `listar_pecas()` ; dropdowns ← `VeiculoController.listar()` / `PecaController.listar()` |
| Vendas + `ItemEditor` | `VendaController.registrar_venda(tipo, itens[{produto_id, tipo_produto, quantidade, preco_unitario}])` · `listar()` · `buscar(id)` · `listar_itens(id)` · `excluir(id)` ; produtos ← `VeiculoController.listar()` / `PecaController.listar()` |
| Ordem de Serviço | `OrdemServicoController.cadastrar(cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca)` · `listar()` · `buscar(id)` · `fechar(id)` · `excluir(id)` · `total_abertas()` ; cliente ← `ClienteController.listar()` ; veículo do cliente ← `VeiculoClienteController.listar_por_cliente(cliente_id)` / `cadastrar(cliente_id, marca, placa, ano)` |
| `MetricCard` × 3 (Dashboard) | `VendaController.total_vendas()` · `EstoqueController.total_veiculos()` · `OrdemServicoController.total_abertas()` |
| `ChartCard` Pie/Bar/Line | Pie ← itens de venda (`VendaController.listar_itens`/agregado) · Bar ← `EstoqueController.listar_veiculos()` · Line ← `VendaController.listar()` (`data`/`total`) |

Contratos de **campos** alinhados (sem renomear): cliente `nome/cpf/telefone/email`; modelo
`nome/numero_serie`; veículo `marca/modelo_id/chassi/ano_fabricacao/cor/preco`; categoria
`nome/descricao`; peça `nome/categoria_id/preco`; veículo-cliente `cliente_id/marca/placa/ano`;
estoque `veiculo_id|peca_id/quantidade`; venda `tipo/total` + itens `produto_id/tipo_produto/
quantidade/preco_unitario`; OS `cliente_id/veiculo_cliente_id/tipo_servico/entrada/saida/
valor_mao_de_obra/valor_peca`.

---

## 7. Stack / notas de implementação (para o plano da Fase 2)

- **Tokens primeiro:** criar `view/theme.py` (paleta, SPACE, CHART_COLORS, font/pesos, radius) e um
  `ft.Theme`/`ColorScheme` aplicado em `page.theme`. Nenhum hex hardcoded nas views.
- **Componentes antes das telas:** `AppShell`, `CrudForm`, `CrudTable`, `MetricCard`, `ChartCard`,
  `LoginCard`, `SnackFeedback` em `view/components/`. As 6 telas CRUD restantes caem quase de graça.
- Widgets-base: `NavigationRail`, `DataTable`/`DataColumn`/`DataRow`/`DataCell`, `TextField`,
  `Dropdown`, `ElevatedButton`, `Card`, `SnackBar`, `PieChart`/`BarChart`/`LineChart`, `Icons`.
- Um único `ft.app(target=...)`; troca de destino substitui o conteúdo do `AppShell` (sem novo app).
- Os agregados dos gráficos (Pie/Bar/Line) são formalizados na Fase 3; nesta fase o `ChartCard` já
  nasce pronto para recebê-los.
```
