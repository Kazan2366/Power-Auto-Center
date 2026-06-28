# Relatorio para Claude Code - Correcoes Concessionaria

Data: 2026-06-28  
Projeto: `C:/Users/silvi/OneDrive/PROJETOS_CARLOS/CONCESSONARIA`  
Stack: Python + SQLite (`sqlite3`) + CustomTkinter, arquitetura MVC + DAO.

## Contexto

Foram aplicados dois pacotes de correcao gerados pelo Dev Squad/OpenSquad:

- `codex-fix-pack.md`: criticos e altos.
- `codex-fix-pack-2-medios-baixos.md`: qualidade, validacoes e refactors.

O objetivo foi corrigir bugs reais, endurecer regras de dominio, reduzir vazamento de erro tecnico para UI e aumentar cobertura de testes, sem trocar stack nem adicionar dependencias.

## Resultado Atual

Validacoes finais executadas com sucesso:

```powershell
python -m pytest -q
# 39 passed

python -m compileall -q .
python main.py --headless
python seed_exemplos.py
```

O `seed_exemplos.py` roda de forma idempotente no banco atual e nao quebra quando os registros ja existem.

## Principais Correcoes - Rodada 1

- Corrigido crash do seed por variavel `veiculos` nao definida.
- Senhas deixam de ser gravadas em texto puro:
  - novo helper `database/security.py`;
  - hash `pbkdf2_sha256`;
  - salt por usuario;
  - comparacao via `hmac.compare_digest`;
  - migracao de senhas legadas em plaintext.
- Login passou a usar `Usuario.buscar_por_username`.
- Login nao vaza mais `str(exc)` de SQLite para a UI.
- `DEFAULT_USERS` agora nasce com senha hasheada.
- Schema ganhou `CHECK` para:
  - `users.role`;
  - `vendas.tipo`;
  - `venda_itens.tipo_produto`;
  - precos, totais, quantidades e valores de OS nao negativos.
- Foi criada migracao idempotente para aplicar `CHECKs` em bancos existentes.
- `database/sql/create_database.sql` foi sincronizado com o schema runtime.
- `modelo_id` em veiculos ficou opcional na UI.
- Estoque passou a mostrar mensagem amigavel para quantidade nao-inteira.
- Backup, relatorios e dashboard ganharam feedback visual minimo para operacoes demoradas.

## Principais Correcoes - Rodada 2

### Backend

- `utils/helpers.py` agora contem validadores ativos:
  - `validate_cpf`;
  - `validate_email`;
  - `validate_placa`;
  - `validate_chassi`.
- Controllers agora validam:
  - CPF/e-mail em cliente e funcionario;
  - placa antiga/Mercosul em veiculo de cliente;
  - chassi com 17 caracteres validos em veiculo.
- Criado `controller/common.py` com `duplicidade_amigavel`.
- Duplicidade amigavel aplicada em:
  - usuario;
  - cliente CPF;
  - funcionario CPF;
  - marca nome;
  - modelo numero de serie;
  - veiculo chassi;
  - veiculo de cliente placa.
- `OrdemServico.fechar` agora e idempotente/verificavel:
  - OS inexistente levanta `ValueError`;
  - OS ja fechada levanta `ValueError`;
  - model retorna flag de sucesso do `UPDATE`.
- Criado `service/common.py` com `scalar`.
- `_scalar` duplicado removido de services.
- `DashboardService` reaproveita `Venda.total_vendas` e `Estoque.total_*`.
- `FinanceiroService` reaproveita `Venda.total_vendas` e `FuncionarioController.total_salarios`.
- Metodo morto `Veiculo.buscar_modelos_por_marca` removido.
- `model/venda.py` recebeu comentario/guardrail explicando que SQL com f-string usa apenas allowlist interna `_ESTOQUE_REF`.
- `Backend` documenta a premissa de conexao SQLite unica/single-thread.

### UI

- `view/theme.py` centraliza tokens novos:
  - `COR_TEXTO_INVERTIDO`;
  - `COR_LARANJA`;
  - `COR_ROXO`;
  - `COR_CIANO`;
  - `COR_AMARELO`;
  - `PALETA_SERIES`.
- `view/charts.py`, `view/dashboard_view.py` e `view/financeiro_view.py` passaram a consumir tokens do tema.
- `view/widgets.py` ganhou:
  - `PageHeader`;
  - `chamar_backend`.
- `backup_view.py` e `relatorios_view.py` usam `PageHeader` e `chamar_backend`.
- `vendas_view.py`:
  - limpar carrinho reseta quantidade para `1`;
  - repoe preco do produto selecionado;
  - exclusao de venda confirma sucesso visualmente.
- `crud_view.py` confirma exclusao bem-sucedida com `messagebox.showinfo`.
- `estoque_view.py` foi refatorada:
  - criada dataclass `AbaEstoque`;
  - removido estado pendurado em widgets (`combo._mapa`, `_fonte`, `_listar`, `_tabela`);
  - nomes agora condizem com o conteudo (`aba_veiculos`, `aba_pecas`);
  - `<Return>` no campo de quantidade executa a acao primaria.
- `main_window.py` foi reescrito preservando comportamento, removendo a terceira coluna de icones mortos do `MENU`.

## Testes Adicionados/Ajustados

Arquivos novos:

- `tests/test_security_and_constraints.py`
- `tests/test_validacoes.py`
- `tests/test_vendas.py`

Coberturas novas:

- Login com senha correta/incorreta.
- Senhas seed hasheadas.
- `CHECKs` de schema para role, tipo de venda/produto e valores negativos.
- Validacao de CPF, e-mail, placa e chassi.
- Duplicidade amigavel em entidades-chave.
- Fechamento de OS: sucesso, inexistente, ja fechada.
- Venda:
  - baixa de estoque;
  - devolucao de estoque na exclusao;
  - bloqueio por estoque insuficiente;
  - rollback sem gravar venda;
  - rejeicao de tipo de venda/produto invalido.

Teste ajustado:

- `tests/test_veiculo.py` agora usa chassi valido de 17 caracteres.

## Arquivos Novos

- `controller/common.py`
- `database/security.py`
- `service/common.py`
- `tests/test_security_and_constraints.py`
- `tests/test_validacoes.py`
- `tests/test_vendas.py`
- `docs/relatorio-claude-code-2026-06-28.md`

## Arquivos Mais Relevantes Alterados

- `database/connection.py`
- `database/sql/create_database.sql`
- `controller/login_controller.py`
- `controller/*_controller.py`
- `model/usuario.py`
- `model/ordem_servico.py`
- `model/venda.py`
- `service/dashboard_service.py`
- `service/financeiro_service.py`
- `utils/helpers.py`
- `view/theme.py`
- `view/widgets.py`
- `view/estoque_view.py`
- `view/main_window.py`
- `view/vendas_view.py`
- `seed_exemplos.py`

## Atenções Para o Proximo Agente

1. A worktree esta suja e inclui mudancas da rodada anterior e desta rodada. Nao usar `git reset` nem reverter arquivos sem revisar.
2. `README.md` ja estava modificado antes da rodada atual, alinhando credenciais seed reais.
3. O projeto tem arquivos antigos com encoding misto/mojibake em algumas strings historicas. Onde arquivos foram reescritos, as strings novas estao em PT-BR correto.
4. Em `seed_exemplos.py`, ha definicoes antigas sobrescritas por definicoes novas por causa do encoding legado. A versao ativa passa nos smokes, mas uma limpeza futura pode reescrever o arquivo inteiro em UTF-8 limpo.
5. Refactors intencionalmente nao feitos por custo/risco:
   - `BE-Q2`: BaseModel/BaseController generico amplo.
   - `UI-B1`: extrair SelectsDependentes do `CrudView`.
   - `UI-B3`: centralizar todas as strings de UI.
6. A premissa atual do backend continua sendo conexao SQLite unica na mesma thread. UI com thread real exigiria conexao por thread ou fila serializada.

## Estado de Aceite

Aceite tecnico atual:

- Testes verdes: `39 passed`.
- Compilacao Python sem erro.
- `main.py --headless` inicializa e mostra indicadores.
- `seed_exemplos.py` roda sem excecao e preserva idempotencia.

