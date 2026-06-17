# Concessionária — Fase 1: Camada de Dados (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Normalizar a camada de dados da concessionária numa única arquitetura MVC coerente (SQLite + DAOs com conexão injetada), com testes pytest cobrindo CRUD de todas as 9 entidades.

**Architecture:** Schema canônico único em `database/connection.py` (SQLite, tabelas no plural). Cada entidade tem um Model (DAO que recebe `connection`, SQL com `?` e `sqlite3.Row`) e um Controller (recebe `connection`, valida entradas, delega ao model e devolve `dict`). Views ficam para a Fase 2.

**Tech Stack:** Python 3.14 · sqlite3 (stdlib) · pytest. (Flet é instalado mas só usado na Fase 2.)

---

## Convenções (ler antes de começar)

**Padrão de Model (DAO):**
```python
class XModel:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, ...):
        cur = self.connection.cursor()
        cur.execute("INSERT INTO tabela (...) VALUES (?, ...)", (...))
        self.connection.commit()
        return cur.lastrowid
    # listar -> cur.fetchall() (lista de sqlite3.Row)
    # buscar -> cur.fetchone() (Row ou None)
    # atualizar/excluir -> execute + commit, retorna None
```

**Padrão de Controller:**
```python
class XController:
    def __init__(self, connection):
        self.model = XModel(connection)

    def cadastrar(self, ...):
        # valida -> raise ValueError("mensagem") se inválido
        return self.model.criar(...)

    def listar(self):
        return [dict(r) for r in self.model.listar()]  # Rows -> dicts
```
- Validação inválida ⇒ `raise ValueError(msg)`.
- Erros de integridade (ex.: CPF duplicado) propagam como `sqlite3.IntegrityError` — as views da Fase 2 tratam.
- Controllers devolvem `dict`/`list[dict]` (nunca `Row`) para desacoplar a view do sqlite3.

**Padrão de teste:** cada entidade tem `tests/test_<entidade>.py` usando a fixture `conn` (banco em memória com schema). Round-trip: criar → buscar/listar → atualizar → excluir.

**Commits:** cada task termina com commit. Mensagens em português, prefixo convencional (`feat:`, `refactor:`, `test:`, `chore:`).

---

## Task 0: Setup do ambiente

**Files:**
- Create: `requirements.txt` (sobrescreve), `.gitignore`
- Modify: `main.py`

- [ ] **Step 1: Inicializar git** (necessário para os commits do plano)

Run: `git init`
Expected: "Initialized empty Git repository"

- [ ] **Step 2: Reescrever `requirements.txt`**

```
flet
pytest
```

- [ ] **Step 3: Criar `.gitignore`**

```
__pycache__/
*.pyc
.pytest_cache/
concessionaria.db
.venv/
```

- [ ] **Step 4: Limpar `main.py`** (remover o import lixo `from socket import create_connection`)

```python
from database.connection import create_connection
from view.login_view import LoginView


def main():
    connection = create_connection()
    login_view = LoginView(connection)
    login_view.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Instalar dependências**

Run: `pip install -r requirements.txt`
Expected: flet e pytest instalados sem erro.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .gitignore main.py
git commit -m "chore: normaliza dependencias e limpa main.py"
```

---

## Task 1: Refatorar `connection.py` (schema reutilizável) + fixture de testes

Hoje `init_database()` roda no import (efeito colateral) e mistura schema com seed. Vamos expor o
schema como função reutilizável para que testes usem um banco em memória.

**Files:**
- Modify: `database/connection.py`
- Create: `tests/__init__.py`, `tests/conftest.py`
- Modify: `database/sql/create_database.sql` (espelho SQLite, documentação)

- [ ] **Step 1: Escrever o teste da conexão**

Create `tests/__init__.py` (vazio) e `tests/conftest.py`:
```python
import pytest
from database.connection import create_connection


@pytest.fixture
def conn():
    """Conexão SQLite em memória com schema criado e usuários-semente."""
    connection = create_connection(":memory:")
    yield connection
    connection.close()
```

Create `tests/test_connection.py`:
```python
def test_schema_tem_todas_as_tabelas(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = {r["name"] for r in cur.fetchall()}
    esperado = {
        "users", "clientes", "modelos", "veiculos", "categorias_peca",
        "pecas", "veiculo_cliente", "estoque_veiculos", "estoque_pecas",
        "vendas", "venda_itens", "ordem_servico",
    }
    assert esperado.issubset(tabelas)


def test_usuarios_semente_inseridos(conn):
    cur = conn.cursor()
    cur.execute("SELECT username, role FROM users ORDER BY id")
    users = [(r["username"], r["role"]) for r in cur.fetchall()]
    assert ("Cadastrar23", "cadastro") in users
    assert ("Vendendor13", "vendas") in users
    assert ("Mecânico", "mecanico") in users
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `pytest tests/test_connection.py -v`
Expected: FAIL — `create_connection(":memory:")` ainda não cria o schema (hoje só `init_database()` no DB de arquivo faz isso).

- [ ] **Step 3: Reescrever `database/connection.py`**

```python
import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).parent.parent / "concessionaria.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    telefone TEXT,
    email TEXT
);
CREATE TABLE IF NOT EXISTS modelos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    numero_serie TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS veiculos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    marca TEXT NOT NULL,
    modelo_id INTEGER,
    chassi TEXT UNIQUE,
    ano_fabricacao INTEGER,
    cor TEXT,
    preco REAL,
    FOREIGN KEY (modelo_id) REFERENCES modelos(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS categorias_peca (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT
);
CREATE TABLE IF NOT EXISTS pecas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    categoria_id INTEGER,
    preco REAL,
    FOREIGN KEY (categoria_id) REFERENCES categorias_peca(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS veiculo_cliente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    marca TEXT,
    placa TEXT UNIQUE,
    ano INTEGER,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS estoque_veiculos (
    veiculo_id INTEGER PRIMARY KEY,
    quantidade INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS estoque_pecas (
    peca_id INTEGER PRIMARY KEY,
    quantidade INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (peca_id) REFERENCES pecas(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo TEXT NOT NULL,
    total REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS venda_itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venda_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    tipo_produto TEXT NOT NULL,
    quantidade INTEGER NOT NULL,
    preco_unitario REAL NOT NULL,
    FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS ordem_servico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    veiculo_cliente_id INTEGER NOT NULL,
    tipo_servico TEXT,
    entrada TIMESTAMP,
    saida TIMESTAMP,
    valor_mao_de_obra REAL,
    valor_peca REAL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL,
    FOREIGN KEY (veiculo_cliente_id) REFERENCES veiculo_cliente(id) ON DELETE SET NULL
);
"""

DEFAULT_USERS = [
    ("Cadastrar23", "4590", "cadastro"),
    ("Vendendor13", "8955", "vendas"),
    ("Mecânico", "7675", "mecanico"),
]


def create_schema(conn):
    """Cria todas as tabelas (idempotente)."""
    conn.executescript(SCHEMA_SQL)


def seed_users(conn):
    """Insere os usuários-semente, ignorando duplicados."""
    cur = conn.cursor()
    cur.executemany(
        "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
        DEFAULT_USERS,
    )
    conn.commit()


def create_connection(db_path: str = None):
    """Retorna uma conexão sqlite3 pronta (schema + usuários garantidos)."""
    path = db_path or str(DB_FILE)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    create_schema(conn)
    seed_users(conn)
    return conn


def init_database():
    """Inicializa o banco em arquivo (uso opcional via CLI)."""
    conn = create_connection()
    conn.close()


if __name__ == "__main__":
    init_database()
    print("Banco inicializado em", DB_FILE)
```

- [ ] **Step 4: Rodar e ver passar**

Run: `pytest tests/test_connection.py -v`
Expected: PASS (2 testes).

- [ ] **Step 5: Reescrever `database/sql/create_database.sql` como espelho SQLite**

Substituir todo o conteúdo do arquivo por um cabeçalho de documentação seguido do mesmo DDL do
`SCHEMA_SQL` acima (sem `CREATE DATABASE`/`USE`, que não existem em SQLite):
```sql
-- Schema canônico (SQLite) — espelho de database/connection.py SCHEMA_SQL.
-- O runtime cria as tabelas automaticamente via create_connection().
-- Este arquivo é apenas documentação/referência.

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);
-- (... colar aqui as demais tabelas, idênticas ao SCHEMA_SQL da Task 1 Step 3 ...)
```

- [ ] **Step 6: Commit**

```bash
git add database/connection.py database/sql/create_database.sql tests/__init__.py tests/conftest.py tests/test_connection.py
git commit -m "refactor: schema SQLite reutilizavel e fixture de testes"
```

---

## Task 2: Cliente (Model + Controller)

**Files:**
- Modify: `model/cliente.py`
- Modify: `controller/cliente_controller.py`
- Create: `tests/test_cliente.py`

- [ ] **Step 1: Escrever o teste**

```python
import pytest
from controller.cliente_controller import ClienteController


def test_cadastrar_e_listar(conn):
    c = ClienteController(conn)
    cid = c.cadastrar("Ana", "111", "9999", "ana@x.com")
    assert isinstance(cid, int)
    clientes = c.listar()
    assert len(clientes) == 1
    assert clientes[0]["nome"] == "Ana"
    assert clientes[0]["cpf"] == "111"


def test_buscar_atualizar_excluir(conn):
    c = ClienteController(conn)
    cid = c.cadastrar("Ana", "111", "9999", "ana@x.com")
    assert c.buscar(cid)["nome"] == "Ana"
    c.atualizar(cid, "Ana Maria", "111", "8888", "am@x.com")
    assert c.buscar(cid)["nome"] == "Ana Maria"
    c.excluir(cid)
    assert c.buscar(cid) is None


def test_nome_obrigatorio(conn):
    c = ClienteController(conn)
    with pytest.raises(ValueError):
        c.cadastrar("", "111", "9999", "ana@x.com")


def test_cpf_obrigatorio(conn):
    c = ClienteController(conn)
    with pytest.raises(ValueError):
        c.cadastrar("Ana", "", "9999", "ana@x.com")
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `pytest tests/test_cliente.py -v`
Expected: FAIL — `ClienteController(conn)` ainda usa a assinatura antiga.

- [ ] **Step 3: Reescrever `model/cliente.py`**

```python
class Cliente:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, nome, cpf, telefone, email):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO clientes (nome, cpf, telefone, email) VALUES (?, ?, ?, ?)",
            (nome, cpf, telefone, email),
        )
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM clientes ORDER BY id")
        return cur.fetchall()

    def buscar(self, cliente_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        return cur.fetchone()

    def atualizar(self, cliente_id, nome, cpf, telefone, email):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE clientes SET nome = ?, cpf = ?, telefone = ?, email = ? WHERE id = ?",
            (nome, cpf, telefone, email, cliente_id),
        )
        self.connection.commit()

    def excluir(self, cliente_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        self.connection.commit()
```

- [ ] **Step 4: Reescrever `controller/cliente_controller.py`**

```python
from model.cliente import Cliente


class ClienteController:
    def __init__(self, connection):
        self.model = Cliente(connection)

    def cadastrar(self, nome, cpf, telefone, email):
        if not (nome or "").strip():
            raise ValueError("Nome é obrigatório.")
        if not (cpf or "").strip():
            raise ValueError("CPF é obrigatório.")
        return self.model.criar(nome.strip(), cpf.strip(), telefone, email)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, cliente_id):
        row = self.model.buscar(cliente_id)
        return dict(row) if row else None

    def atualizar(self, cliente_id, nome, cpf, telefone, email):
        if not (nome or "").strip():
            raise ValueError("Nome é obrigatório.")
        if not (cpf or "").strip():
            raise ValueError("CPF é obrigatório.")
        self.model.atualizar(cliente_id, nome.strip(), cpf.strip(), telefone, email)

    def excluir(self, cliente_id):
        self.model.excluir(cliente_id)
```

- [ ] **Step 5: Rodar e ver passar**

Run: `pytest tests/test_cliente.py -v`
Expected: PASS (4 testes).

- [ ] **Step 6: Commit**

```bash
git add model/cliente.py controller/cliente_controller.py tests/test_cliente.py
git commit -m "refactor: cliente model/controller como DAO SQLite"
```

---

## Task 3: Modelo (Model + Controller)

Tabela `modelos(id, nome, numero_serie)`.

**Files:**
- Modify: `model/modelo.py`, `controller/modelo_controller.py`
- Create: `tests/test_modelo.py`

- [ ] **Step 1: Escrever o teste**

```python
import pytest
from controller.modelo_controller import ModeloController


def test_crud_modelo(conn):
    c = ModeloController(conn)
    mid = c.cadastrar("Civic", "SN-001")
    assert c.buscar(mid)["nome"] == "Civic"
    assert len(c.listar()) == 1
    c.atualizar(mid, "Civic EX", "SN-001")
    assert c.buscar(mid)["nome"] == "Civic EX"
    c.excluir(mid)
    assert c.buscar(mid) is None


def test_nome_obrigatorio(conn):
    c = ModeloController(conn)
    with pytest.raises(ValueError):
        c.cadastrar("", "SN-001")
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `pytest tests/test_modelo.py -v`
Expected: FAIL.

- [ ] **Step 3: Reescrever `model/modelo.py`**

```python
class Modelo:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, nome, numero_serie):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO modelos (nome, numero_serie) VALUES (?, ?)",
            (nome, numero_serie),
        )
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM modelos ORDER BY id")
        return cur.fetchall()

    def buscar(self, modelo_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM modelos WHERE id = ?", (modelo_id,))
        return cur.fetchone()

    def atualizar(self, modelo_id, nome, numero_serie):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE modelos SET nome = ?, numero_serie = ? WHERE id = ?",
            (nome, numero_serie, modelo_id),
        )
        self.connection.commit()

    def excluir(self, modelo_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM modelos WHERE id = ?", (modelo_id,))
        self.connection.commit()
```

- [ ] **Step 4: Reescrever `controller/modelo_controller.py`**

```python
from model.modelo import Modelo


class ModeloController:
    def __init__(self, connection):
        self.model = Modelo(connection)

    def cadastrar(self, nome, numero_serie):
        if not (nome or "").strip():
            raise ValueError("Nome do modelo é obrigatório.")
        return self.model.criar(nome.strip(), (numero_serie or "").strip() or None)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, modelo_id):
        row = self.model.buscar(modelo_id)
        return dict(row) if row else None

    def atualizar(self, modelo_id, nome, numero_serie):
        if not (nome or "").strip():
            raise ValueError("Nome do modelo é obrigatório.")
        self.model.atualizar(modelo_id, nome.strip(), (numero_serie or "").strip() or None)

    def excluir(self, modelo_id):
        self.model.excluir(modelo_id)
```

- [ ] **Step 5: Rodar e ver passar**

Run: `pytest tests/test_modelo.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add model/modelo.py controller/modelo_controller.py tests/test_modelo.py
git commit -m "refactor: modelo model/controller como DAO SQLite"
```

---

## Task 4: Veiculo (Model + Controller)

Tabela `veiculos(id, marca, modelo_id, chassi, ano_fabricacao, cor, preco)`.

**Files:**
- Modify: `model/veiculo.py`, `controller/veiculo_controller.py`
- Create: `tests/test_veiculo.py`

- [ ] **Step 1: Escrever o teste**

```python
import pytest
from controller.modelo_controller import ModeloController
from controller.veiculo_controller import VeiculoController


def test_crud_veiculo(conn):
    mid = ModeloController(conn).cadastrar("Civic", "SN-1")
    c = VeiculoController(conn)
    vid = c.cadastrar("Honda", mid, "CHASSI1", 2020, "Preto", 90000.0)
    assert c.buscar(vid)["marca"] == "Honda"
    assert len(c.listar()) == 1
    c.atualizar(vid, "Honda", mid, "CHASSI1", 2021, "Branco", 95000.0)
    assert c.buscar(vid)["cor"] == "Branco"
    c.excluir(vid)
    assert c.buscar(vid) is None


def test_marca_obrigatoria(conn):
    c = VeiculoController(conn)
    with pytest.raises(ValueError):
        c.cadastrar("", None, "CHASSI1", 2020, "Preto", 90000.0)


def test_preco_negativo_invalido(conn):
    c = VeiculoController(conn)
    with pytest.raises(ValueError):
        c.cadastrar("Honda", None, "CHASSI1", 2020, "Preto", -1.0)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `pytest tests/test_veiculo.py -v`
Expected: FAIL.

- [ ] **Step 3: Reescrever `model/veiculo.py`**

```python
class Veiculo:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, marca, modelo_id, chassi, ano_fabricacao, cor, preco):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO veiculos (marca, modelo_id, chassi, ano_fabricacao, cor, preco) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (marca, modelo_id, chassi, ano_fabricacao, cor, preco),
        )
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM veiculos ORDER BY id")
        return cur.fetchall()

    def buscar(self, veiculo_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM veiculos WHERE id = ?", (veiculo_id,))
        return cur.fetchone()

    def atualizar(self, veiculo_id, marca, modelo_id, chassi, ano_fabricacao, cor, preco):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE veiculos SET marca = ?, modelo_id = ?, chassi = ?, "
            "ano_fabricacao = ?, cor = ?, preco = ? WHERE id = ?",
            (marca, modelo_id, chassi, ano_fabricacao, cor, preco, veiculo_id),
        )
        self.connection.commit()

    def excluir(self, veiculo_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM veiculos WHERE id = ?", (veiculo_id,))
        self.connection.commit()
```

- [ ] **Step 4: Reescrever `controller/veiculo_controller.py`**

```python
from model.veiculo import Veiculo


class VeiculoController:
    def __init__(self, connection):
        self.model = Veiculo(connection)

    def _validar(self, marca, preco):
        if not (marca or "").strip():
            raise ValueError("Marca é obrigatória.")
        if preco is not None and preco < 0:
            raise ValueError("Preço não pode ser negativo.")

    def cadastrar(self, marca, modelo_id, chassi, ano_fabricacao, cor, preco):
        self._validar(marca, preco)
        return self.model.criar(marca.strip(), modelo_id, chassi, ano_fabricacao, cor, preco)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, veiculo_id):
        row = self.model.buscar(veiculo_id)
        return dict(row) if row else None

    def atualizar(self, veiculo_id, marca, modelo_id, chassi, ano_fabricacao, cor, preco):
        self._validar(marca, preco)
        self.model.atualizar(veiculo_id, marca.strip(), modelo_id, chassi, ano_fabricacao, cor, preco)

    def excluir(self, veiculo_id):
        self.model.excluir(veiculo_id)
```

- [ ] **Step 5: Rodar e ver passar**

Run: `pytest tests/test_veiculo.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add model/veiculo.py controller/veiculo_controller.py tests/test_veiculo.py
git commit -m "refactor: veiculo model/controller como DAO SQLite"
```

---

## Task 5: CategoriaPeca (Model + Controller)

Tabela `categorias_peca(id, nome, descricao)`.

**Files:**
- Modify: `model/categoria_peca.py`, `controller/categoria_peca_controller.py`
- Create: `tests/test_categoria_peca.py`

- [ ] **Step 1: Escrever o teste**

```python
import pytest
from controller.categoria_peca_controller import CategoriaPecaController


def test_crud_categoria(conn):
    c = CategoriaPecaController(conn)
    cid = c.cadastrar("Freios", "Sistema de freios")
    assert c.buscar(cid)["nome"] == "Freios"
    assert len(c.listar()) == 1
    c.atualizar(cid, "Freios ABS", "Freios ABS")
    assert c.buscar(cid)["nome"] == "Freios ABS"
    c.excluir(cid)
    assert c.buscar(cid) is None


def test_nome_obrigatorio(conn):
    c = CategoriaPecaController(conn)
    with pytest.raises(ValueError):
        c.cadastrar("", "x")
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `pytest tests/test_categoria_peca.py -v`
Expected: FAIL.

- [ ] **Step 3: Reescrever `model/categoria_peca.py`**

```python
class CategoriaPeca:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, nome, descricao):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO categorias_peca (nome, descricao) VALUES (?, ?)",
            (nome, descricao),
        )
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM categorias_peca ORDER BY id")
        return cur.fetchall()

    def buscar(self, categoria_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM categorias_peca WHERE id = ?", (categoria_id,))
        return cur.fetchone()

    def atualizar(self, categoria_id, nome, descricao):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE categorias_peca SET nome = ?, descricao = ? WHERE id = ?",
            (nome, descricao, categoria_id),
        )
        self.connection.commit()

    def excluir(self, categoria_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM categorias_peca WHERE id = ?", (categoria_id,))
        self.connection.commit()
```

- [ ] **Step 4: Reescrever `controller/categoria_peca_controller.py`**

```python
from model.categoria_peca import CategoriaPeca


class CategoriaPecaController:
    def __init__(self, connection):
        self.model = CategoriaPeca(connection)

    def cadastrar(self, nome, descricao):
        if not (nome or "").strip():
            raise ValueError("Nome da categoria é obrigatório.")
        return self.model.criar(nome.strip(), descricao)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, categoria_id):
        row = self.model.buscar(categoria_id)
        return dict(row) if row else None

    def atualizar(self, categoria_id, nome, descricao):
        if not (nome or "").strip():
            raise ValueError("Nome da categoria é obrigatório.")
        self.model.atualizar(categoria_id, nome.strip(), descricao)

    def excluir(self, categoria_id):
        self.model.excluir(categoria_id)
```

- [ ] **Step 5: Rodar e ver passar**

Run: `pytest tests/test_categoria_peca.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add model/categoria_peca.py controller/categoria_peca_controller.py tests/test_categoria_peca.py
git commit -m "refactor: categoria_peca model/controller como DAO SQLite"
```

---

## Task 6: Peca (Model + Controller)

Tabela `pecas(id, nome, categoria_id, preco)`.

**Files:**
- Modify: `model/peca.py`, `controller/peca_controller.py`
- Create: `tests/test_peca.py`

- [ ] **Step 1: Escrever o teste**

```python
import pytest
from controller.categoria_peca_controller import CategoriaPecaController
from controller.peca_controller import PecaController


def test_crud_peca(conn):
    cat = CategoriaPecaController(conn).cadastrar("Freios", "x")
    c = PecaController(conn)
    pid = c.cadastrar("Pastilha", cat, 120.0)
    assert c.buscar(pid)["nome"] == "Pastilha"
    assert len(c.listar()) == 1
    c.atualizar(pid, "Pastilha Dianteira", cat, 150.0)
    assert c.buscar(pid)["preco"] == 150.0
    c.excluir(pid)
    assert c.buscar(pid) is None


def test_nome_obrigatorio(conn):
    c = PecaController(conn)
    with pytest.raises(ValueError):
        c.cadastrar("", None, 120.0)


def test_preco_negativo_invalido(conn):
    c = PecaController(conn)
    with pytest.raises(ValueError):
        c.cadastrar("Pastilha", None, -1.0)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `pytest tests/test_peca.py -v`
Expected: FAIL.

- [ ] **Step 3: Reescrever `model/peca.py`**

```python
class Peca:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, nome, categoria_id, preco):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO pecas (nome, categoria_id, preco) VALUES (?, ?, ?)",
            (nome, categoria_id, preco),
        )
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM pecas ORDER BY id")
        return cur.fetchall()

    def buscar(self, peca_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM pecas WHERE id = ?", (peca_id,))
        return cur.fetchone()

    def atualizar(self, peca_id, nome, categoria_id, preco):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE pecas SET nome = ?, categoria_id = ?, preco = ? WHERE id = ?",
            (nome, categoria_id, preco, peca_id),
        )
        self.connection.commit()

    def excluir(self, peca_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM pecas WHERE id = ?", (peca_id,))
        self.connection.commit()
```

- [ ] **Step 4: Reescrever `controller/peca_controller.py`**

```python
from model.peca import Peca


class PecaController:
    def __init__(self, connection):
        self.model = Peca(connection)

    def _validar(self, nome, preco):
        if not (nome or "").strip():
            raise ValueError("Nome da peça é obrigatório.")
        if preco is not None and preco < 0:
            raise ValueError("Preço não pode ser negativo.")

    def cadastrar(self, nome, categoria_id, preco):
        self._validar(nome, preco)
        return self.model.criar(nome.strip(), categoria_id, preco)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, peca_id):
        row = self.model.buscar(peca_id)
        return dict(row) if row else None

    def atualizar(self, peca_id, nome, categoria_id, preco):
        self._validar(nome, preco)
        self.model.atualizar(peca_id, nome.strip(), categoria_id, preco)

    def excluir(self, peca_id):
        self.model.excluir(peca_id)
```

- [ ] **Step 5: Rodar e ver passar**

Run: `pytest tests/test_peca.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add model/peca.py controller/peca_controller.py tests/test_peca.py
git commit -m "refactor: peca model/controller como DAO SQLite"
```

---

## Task 7: VeiculoCliente (Model + Controller)

Tabela `veiculo_cliente(id, cliente_id, marca, placa, ano)`.

**Files:**
- Modify: `model/veiculo_cliente.py`, `controller/veiculo_cliente_controller.py`
- Create: `tests/test_veiculo_cliente.py`

- [ ] **Step 1: Escrever o teste**

```python
import pytest
from controller.cliente_controller import ClienteController
from controller.veiculo_cliente_controller import VeiculoClienteController


def test_crud_veiculo_cliente(conn):
    cid = ClienteController(conn).cadastrar("Ana", "111", "9", "a@x.com")
    c = VeiculoClienteController(conn)
    vid = c.cadastrar(cid, "Fiat", "ABC1234", 2018)
    assert c.buscar(vid)["placa"] == "ABC1234"
    assert len(c.listar()) == 1
    assert len(c.listar_por_cliente(cid)) == 1
    c.atualizar(vid, cid, "Fiat", "ABC1234", 2019)
    assert c.buscar(vid)["ano"] == 2019
    c.excluir(vid)
    assert c.buscar(vid) is None


def test_cliente_obrigatorio(conn):
    c = VeiculoClienteController(conn)
    with pytest.raises(ValueError):
        c.cadastrar(None, "Fiat", "ABC1234", 2018)


def test_placa_obrigatoria(conn):
    cid = ClienteController(conn).cadastrar("Ana", "111", "9", "a@x.com")
    c = VeiculoClienteController(conn)
    with pytest.raises(ValueError):
        c.cadastrar(cid, "Fiat", "", 2018)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `pytest tests/test_veiculo_cliente.py -v`
Expected: FAIL.

- [ ] **Step 3: Reescrever `model/veiculo_cliente.py`**

```python
class VeiculoCliente:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, cliente_id, marca, placa, ano):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO veiculo_cliente (cliente_id, marca, placa, ano) VALUES (?, ?, ?, ?)",
            (cliente_id, marca, placa, ano),
        )
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM veiculo_cliente ORDER BY id")
        return cur.fetchall()

    def listar_por_cliente(self, cliente_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM veiculo_cliente WHERE cliente_id = ? ORDER BY id", (cliente_id,))
        return cur.fetchall()

    def buscar(self, vc_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM veiculo_cliente WHERE id = ?", (vc_id,))
        return cur.fetchone()

    def atualizar(self, vc_id, cliente_id, marca, placa, ano):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE veiculo_cliente SET cliente_id = ?, marca = ?, placa = ?, ano = ? WHERE id = ?",
            (cliente_id, marca, placa, ano, vc_id),
        )
        self.connection.commit()

    def excluir(self, vc_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM veiculo_cliente WHERE id = ?", (vc_id,))
        self.connection.commit()
```

- [ ] **Step 4: Reescrever `controller/veiculo_cliente_controller.py`**

```python
from model.veiculo_cliente import VeiculoCliente


class VeiculoClienteController:
    def __init__(self, connection):
        self.model = VeiculoCliente(connection)

    def _validar(self, cliente_id, placa):
        if not cliente_id:
            raise ValueError("Cliente é obrigatório.")
        if not (placa or "").strip():
            raise ValueError("Placa é obrigatória.")

    def cadastrar(self, cliente_id, marca, placa, ano):
        self._validar(cliente_id, placa)
        return self.model.criar(cliente_id, marca, placa.strip(), ano)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def listar_por_cliente(self, cliente_id):
        return [dict(r) for r in self.model.listar_por_cliente(cliente_id)]

    def buscar(self, vc_id):
        row = self.model.buscar(vc_id)
        return dict(row) if row else None

    def atualizar(self, vc_id, cliente_id, marca, placa, ano):
        self._validar(cliente_id, placa)
        self.model.atualizar(vc_id, cliente_id, marca, placa.strip(), ano)

    def excluir(self, vc_id):
        self.model.excluir(vc_id)
```

- [ ] **Step 5: Rodar e ver passar**

Run: `pytest tests/test_veiculo_cliente.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add model/veiculo_cliente.py controller/veiculo_cliente_controller.py tests/test_veiculo_cliente.py
git commit -m "refactor: veiculo_cliente model/controller como DAO SQLite"
```

---

## Task 8: Estoque (Model + Controller)

Tabelas `estoque_veiculos(veiculo_id, quantidade)` e `estoque_pecas(peca_id, quantidade)`. Usa UPSERT
(`ON CONFLICT`) para definir a quantidade por item.

**Files:**
- Modify: `model/estoque.py`, `controller/estoque_controller.py`
- Create: `tests/test_estoque.py`

- [ ] **Step 1: Escrever o teste**

```python
import pytest
from controller.veiculo_controller import VeiculoController
from controller.peca_controller import PecaController
from controller.estoque_controller import EstoqueController


def test_estoque_veiculo_upsert_e_total(conn):
    vid = VeiculoController(conn).cadastrar("Honda", None, "CH1", 2020, "Preto", 90000.0)
    e = EstoqueController(conn)
    e.definir_veiculo(vid, 3)
    assert e.buscar_veiculo(vid)["quantidade"] == 3
    e.definir_veiculo(vid, 5)  # upsert, não duplica
    assert e.buscar_veiculo(vid)["quantidade"] == 5
    assert e.total_veiculos() == 5
    assert len(e.listar_veiculos()) == 1


def test_estoque_peca(conn):
    pid = PecaController(conn).cadastrar("Pastilha", None, 120.0)
    e = EstoqueController(conn)
    e.definir_peca(pid, 10)
    assert e.buscar_peca(pid)["quantidade"] == 10


def test_quantidade_negativa_invalida(conn):
    vid = VeiculoController(conn).cadastrar("Honda", None, "CH1", 2020, "Preto", 90000.0)
    e = EstoqueController(conn)
    with pytest.raises(ValueError):
        e.definir_veiculo(vid, -1)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `pytest tests/test_estoque.py -v`
Expected: FAIL.

- [ ] **Step 3: Reescrever `model/estoque.py`**

```python
class Estoque:
    def __init__(self, connection):
        self.connection = connection

    def definir_veiculo(self, veiculo_id, quantidade):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO estoque_veiculos (veiculo_id, quantidade) VALUES (?, ?) "
            "ON CONFLICT(veiculo_id) DO UPDATE SET quantidade = excluded.quantidade",
            (veiculo_id, quantidade),
        )
        self.connection.commit()

    def definir_peca(self, peca_id, quantidade):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO estoque_pecas (peca_id, quantidade) VALUES (?, ?) "
            "ON CONFLICT(peca_id) DO UPDATE SET quantidade = excluded.quantidade",
            (peca_id, quantidade),
        )
        self.connection.commit()

    def buscar_veiculo(self, veiculo_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM estoque_veiculos WHERE veiculo_id = ?", (veiculo_id,))
        return cur.fetchone()

    def buscar_peca(self, peca_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM estoque_pecas WHERE peca_id = ?", (peca_id,))
        return cur.fetchone()

    def listar_veiculos(self):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT ev.veiculo_id, ev.quantidade, v.marca, v.chassi "
            "FROM estoque_veiculos ev JOIN veiculos v ON v.id = ev.veiculo_id "
            "ORDER BY ev.veiculo_id"
        )
        return cur.fetchall()

    def listar_pecas(self):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT ep.peca_id, ep.quantidade, p.nome "
            "FROM estoque_pecas ep JOIN pecas p ON p.id = ep.peca_id "
            "ORDER BY ep.peca_id"
        )
        return cur.fetchall()

    def total_veiculos(self):
        cur = self.connection.cursor()
        cur.execute("SELECT COALESCE(SUM(quantidade), 0) AS total FROM estoque_veiculos")
        return cur.fetchone()["total"]

    def total_pecas(self):
        cur = self.connection.cursor()
        cur.execute("SELECT COALESCE(SUM(quantidade), 0) AS total FROM estoque_pecas")
        return cur.fetchone()["total"]
```

- [ ] **Step 4: Reescrever `controller/estoque_controller.py`**

```python
from model.estoque import Estoque


class EstoqueController:
    def __init__(self, connection):
        self.model = Estoque(connection)

    def _validar_qtd(self, quantidade):
        if quantidade is None or quantidade < 0:
            raise ValueError("Quantidade não pode ser negativa.")

    def definir_veiculo(self, veiculo_id, quantidade):
        self._validar_qtd(quantidade)
        self.model.definir_veiculo(veiculo_id, quantidade)

    def definir_peca(self, peca_id, quantidade):
        self._validar_qtd(quantidade)
        self.model.definir_peca(peca_id, quantidade)

    def buscar_veiculo(self, veiculo_id):
        row = self.model.buscar_veiculo(veiculo_id)
        return dict(row) if row else None

    def buscar_peca(self, peca_id):
        row = self.model.buscar_peca(peca_id)
        return dict(row) if row else None

    def listar_veiculos(self):
        return [dict(r) for r in self.model.listar_veiculos()]

    def listar_pecas(self):
        return [dict(r) for r in self.model.listar_pecas()]

    def total_veiculos(self):
        return self.model.total_veiculos()

    def total_pecas(self):
        return self.model.total_pecas()
```

- [ ] **Step 5: Rodar e ver passar**

Run: `pytest tests/test_estoque.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add model/estoque.py controller/estoque_controller.py tests/test_estoque.py
git commit -m "refactor: estoque model/controller como DAO SQLite com upsert"
```

---

## Task 9: Venda (Model + Controller)

Tabelas `vendas(id, data, tipo, total)` e `venda_itens(id, venda_id, produto_id, tipo_produto,
quantidade, preco_unitario)`. `registrar_venda` insere a venda e seus itens numa transação, calculando
o total.

**Files:**
- Modify: `model/venda.py`, `controller/venda_controller.py`
- Create: `tests/test_venda.py`

- [ ] **Step 1: Escrever o teste**

```python
import pytest
from controller.venda_controller import VendaController


def test_registrar_venda_calcula_total(conn):
    c = VendaController(conn)
    itens = [
        {"produto_id": 1, "tipo_produto": "veiculo", "quantidade": 1, "preco_unitario": 90000.0},
        {"produto_id": 2, "tipo_produto": "peca", "quantidade": 2, "preco_unitario": 100.0},
    ]
    vid = c.registrar_venda("mista", itens)
    venda = c.buscar(vid)
    assert venda["total"] == 90200.0
    assert len(c.listar_itens(vid)) == 2
    assert c.total_vendas() == 90200.0
    assert len(c.listar()) == 1


def test_itens_obrigatorios(conn):
    c = VendaController(conn)
    with pytest.raises(ValueError):
        c.registrar_venda("veiculo", [])


def test_quantidade_invalida(conn):
    c = VendaController(conn)
    itens = [{"produto_id": 1, "tipo_produto": "peca", "quantidade": 0, "preco_unitario": 10.0}]
    with pytest.raises(ValueError):
        c.registrar_venda("peca", itens)


def test_excluir_venda_remove_itens(conn):
    c = VendaController(conn)
    itens = [{"produto_id": 1, "tipo_produto": "peca", "quantidade": 1, "preco_unitario": 10.0}]
    vid = c.registrar_venda("peca", itens)
    c.excluir(vid)
    assert c.buscar(vid) is None
    assert c.listar_itens(vid) == []
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `pytest tests/test_venda.py -v`
Expected: FAIL.

- [ ] **Step 3: Reescrever `model/venda.py`**

```python
class Venda:
    def __init__(self, connection):
        self.connection = connection

    def registrar(self, tipo, itens, total):
        """Insere a venda e seus itens numa transação. itens: lista de dicts."""
        cur = self.connection.cursor()
        try:
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
        cur = self.connection.cursor()
        cur.execute("DELETE FROM venda_itens WHERE venda_id = ?", (venda_id,))
        cur.execute("DELETE FROM vendas WHERE id = ?", (venda_id,))
        self.connection.commit()
```

- [ ] **Step 4: Reescrever `controller/venda_controller.py`**

```python
from model.venda import Venda


class VendaController:
    def __init__(self, connection):
        self.model = Venda(connection)

    def registrar_venda(self, tipo, itens):
        if not itens:
            raise ValueError("A venda deve ter ao menos um item.")
        total = 0.0
        for i in itens:
            if i["quantidade"] <= 0:
                raise ValueError("Quantidade do item deve ser maior que zero.")
            if i["preco_unitario"] < 0:
                raise ValueError("Preço unitário não pode ser negativo.")
            total += i["quantidade"] * i["preco_unitario"]
        return self.model.registrar(tipo, itens, total)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, venda_id):
        row = self.model.buscar(venda_id)
        return dict(row) if row else None

    def listar_itens(self, venda_id):
        return [dict(r) for r in self.model.listar_itens(venda_id)]

    def total_vendas(self):
        return self.model.total_vendas()

    def excluir(self, venda_id):
        self.model.excluir(venda_id)
```

- [ ] **Step 5: Rodar e ver passar**

Run: `pytest tests/test_venda.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add model/venda.py controller/venda_controller.py tests/test_venda.py
git commit -m "refactor: venda model/controller com itens e total transacional"
```

---

## Task 10: OrdemServico (Model + Controller)

Tabela `ordem_servico(id, cliente_id, veiculo_cliente_id, tipo_servico, entrada, saida,
valor_mao_de_obra, valor_peca)`. `criar` define `entrada = CURRENT_TIMESTAMP` e `saida = NULL` (OS
aberta); `fechar` define `saida = CURRENT_TIMESTAMP`.

**Files:**
- Modify: `model/ordem_servico.py`, `controller/ordem_servico_controller.py`
- Create: `tests/test_ordem_servico.py`

- [ ] **Step 1: Escrever o teste**

```python
import pytest
from controller.cliente_controller import ClienteController
from controller.veiculo_cliente_controller import VeiculoClienteController
from controller.ordem_servico_controller import OrdemServicoController


def _cliente_e_veiculo(conn):
    cid = ClienteController(conn).cadastrar("Ana", "111", "9", "a@x.com")
    vcid = VeiculoClienteController(conn).cadastrar(cid, "Fiat", "ABC1234", 2018)
    return cid, vcid


def test_crud_e_fechamento(conn):
    cid, vcid = _cliente_e_veiculo(conn)
    c = OrdemServicoController(conn)
    oid = c.cadastrar(cid, vcid, "Revisão", 200.0, 50.0)
    os_ = c.buscar(oid)
    assert os_["tipo_servico"] == "Revisão"
    assert os_["saida"] is None
    assert c.total_abertas() == 1
    c.fechar(oid)
    assert c.buscar(oid)["saida"] is not None
    assert c.total_abertas() == 0
    assert len(c.listar()) == 1
    c.excluir(oid)
    assert c.buscar(oid) is None


def test_cliente_e_veiculo_obrigatorios(conn):
    c = OrdemServicoController(conn)
    with pytest.raises(ValueError):
        c.cadastrar(None, None, "Revisão", 200.0, 50.0)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `pytest tests/test_ordem_servico.py -v`
Expected: FAIL.

- [ ] **Step 3: Reescrever `model/ordem_servico.py`**

```python
class OrdemServico:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO ordem_servico "
            "(cliente_id, veiculo_cliente_id, tipo_servico, entrada, saida, "
            "valor_mao_de_obra, valor_peca) "
            "VALUES (?, ?, ?, CURRENT_TIMESTAMP, NULL, ?, ?)",
            (cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca),
        )
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM ordem_servico ORDER BY id")
        return cur.fetchall()

    def buscar(self, os_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM ordem_servico WHERE id = ?", (os_id,))
        return cur.fetchone()

    def atualizar(self, os_id, cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE ordem_servico SET cliente_id = ?, veiculo_cliente_id = ?, "
            "tipo_servico = ?, valor_mao_de_obra = ?, valor_peca = ? WHERE id = ?",
            (cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca, os_id),
        )
        self.connection.commit()

    def fechar(self, os_id):
        cur = self.connection.cursor()
        cur.execute("UPDATE ordem_servico SET saida = CURRENT_TIMESTAMP WHERE id = ?", (os_id,))
        self.connection.commit()

    def total_abertas(self):
        cur = self.connection.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM ordem_servico WHERE saida IS NULL")
        return cur.fetchone()["total"]

    def excluir(self, os_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM ordem_servico WHERE id = ?", (os_id,))
        self.connection.commit()
```

- [ ] **Step 4: Reescrever `controller/ordem_servico_controller.py`**

```python
from model.ordem_servico import OrdemServico


class OrdemServicoController:
    def __init__(self, connection):
        self.model = OrdemServico(connection)

    def _validar(self, cliente_id, veiculo_cliente_id):
        if not cliente_id:
            raise ValueError("Cliente é obrigatório.")
        if not veiculo_cliente_id:
            raise ValueError("Veículo do cliente é obrigatório.")

    def cadastrar(self, cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca):
        self._validar(cliente_id, veiculo_cliente_id)
        return self.model.criar(
            cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca
        )

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, os_id):
        row = self.model.buscar(os_id)
        return dict(row) if row else None

    def atualizar(self, os_id, cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca):
        self._validar(cliente_id, veiculo_cliente_id)
        self.model.atualizar(
            os_id, cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca
        )

    def fechar(self, os_id):
        self.model.fechar(os_id)

    def total_abertas(self):
        return self.model.total_abertas()

    def excluir(self, os_id):
        self.model.excluir(os_id)
```

- [ ] **Step 5: Rodar e ver passar**

Run: `pytest tests/test_ordem_servico.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add model/ordem_servico.py controller/ordem_servico_controller.py tests/test_ordem_servico.py
git commit -m "refactor: ordem_servico model/controller como DAO SQLite"
```

---

## Task 11: Suíte completa verde + atualizar README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Rodar a suíte inteira**

Run: `pytest -v`
Expected: PASS em todos os testes (connection + 9 entidades).

- [ ] **Step 2: Atualizar a seção "Instalação" e estrutura do `README.md`**

Trocar referências a MySQL/PyMySQL por SQLite. Substituir o passo 3 de instalação:
```markdown
3. O banco de dados SQLite (`concessionaria.db`) é criado automaticamente na primeira execução
   (tabelas e usuários-semente via `database/connection.py`).
```
E na lista de dependências/estrutura, remover menções a `connection.py` "MySQL"; descrever como SQLite.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: README descreve SQLite e instalacao atualizada"
```

---

## Notas para a Fase 2 (não implementar agora)

- Views com `build() -> Control`, `MainShell` com `NavigationRail` filtrado por perfil, login sem
  múltiplo `ft.app`.
- Joins de exibição (veículo→nome do modelo, peça→nome da categoria) entram nas views.
- Dashboard com gráficos nativos do Flet consome `total_vendas()`, `total_veiculos()`,
  `total_abertas()` já disponíveis nos controllers.
