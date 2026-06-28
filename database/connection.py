import sqlite3
from pathlib import Path

from database.security import hash_password, is_password_hash

DB_FILE = Path(__file__).parent.parent / "concessionaria.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('cadastro','vendas','mecanico','admin'))
);
CREATE TABLE IF NOT EXISTS funcionarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cargo TEXT,
    cpf TEXT UNIQUE,
    telefone TEXT,
    email TEXT,
    salario REAL,
    data_admissao TEXT
);
CREATE TABLE IF NOT EXISTS marcas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL
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
    numero_serie TEXT UNIQUE,
    marca_id INTEGER,
    FOREIGN KEY (marca_id) REFERENCES marcas(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS veiculos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    marca_id INTEGER,
    modelo_id INTEGER,
    chassi TEXT UNIQUE,
    ano_fabricacao INTEGER,
    cor TEXT,
    preco REAL CHECK (preco >= 0),
    FOREIGN KEY (marca_id) REFERENCES marcas(id) ON DELETE SET NULL,
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
    preco REAL CHECK (preco >= 0),
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
    modelo_id INTEGER PRIMARY KEY,
    quantidade INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0),
    FOREIGN KEY (modelo_id) REFERENCES modelos(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS estoque_pecas (
    peca_id INTEGER PRIMARY KEY,
    quantidade INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0),
    FOREIGN KEY (peca_id) REFERENCES pecas(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo TEXT NOT NULL CHECK (tipo IN ('veiculo','peca','mista')),
    total REAL NOT NULL CHECK (total >= 0)
);
CREATE TABLE IF NOT EXISTS venda_itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venda_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    tipo_produto TEXT NOT NULL CHECK (tipo_produto IN ('veiculo','peca')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario REAL NOT NULL CHECK (preco_unitario >= 0),
    FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS ordem_servico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    veiculo_cliente_id INTEGER NOT NULL,
    tipo_servico TEXT,
    entrada TIMESTAMP,
    saida TIMESTAMP,
    valor_mao_de_obra REAL CHECK (valor_mao_de_obra >= 0),
    valor_peca REAL CHECK (valor_peca >= 0),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL,
    FOREIGN KEY (veiculo_cliente_id) REFERENCES veiculo_cliente(id) ON DELETE SET NULL
);
"""

DEFAULT_USERS = [
    ("operador.cadastro", "senha123", "cadastro"),
    ("operador.vendas", "senha123", "vendas"),
    ("operador.mecanico", "senha123", "mecanico"),
    ("operador.admin", "senha123", "admin"),
]


def create_schema(conn):
    """Cria todas as tabelas (idempotente)."""
    conn.executescript(SCHEMA_SQL)
    _migrar_estoque_para_modelo(conn)
    _migrar_constraints(conn)


def _migrar_estoque_para_modelo(conn):
    """Migra ``estoque_veiculos`` do esquema antigo (veiculo_id) para o novo (modelo_id).

    Agrega as quantidades por modelo e reaponta os itens de venda de veículo
    (``venda_itens.produto_id``) de veiculo_id para modelo_id. Idempotente:
    não faz nada se a tabela já estiver no formato novo.
    """
    cur = conn.cursor()
    colunas = [r["name"] for r in cur.execute("PRAGMA table_info(estoque_veiculos)").fetchall()]
    if "veiculo_id" not in colunas:
        return  # já migrado (ou banco novo)

    cur.executescript(
        "CREATE TABLE estoque_veiculos_new ("
        "    modelo_id INTEGER PRIMARY KEY,"
        "    quantidade INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0),"
        "    FOREIGN KEY (modelo_id) REFERENCES modelos(id) ON DELETE CASCADE"
        ");"
    )
    cur.execute(
        "INSERT INTO estoque_veiculos_new (modelo_id, quantidade) "
        "SELECT v.modelo_id, SUM(ev.quantidade) FROM estoque_veiculos ev "
        "JOIN veiculos v ON v.id = ev.veiculo_id "
        "WHERE v.modelo_id IS NOT NULL GROUP BY v.modelo_id"
    )
    cur.execute(
        "UPDATE venda_itens SET produto_id = "
        "COALESCE((SELECT modelo_id FROM veiculos WHERE id = venda_itens.produto_id), produto_id) "
        "WHERE tipo_produto = 'veiculo'"
    )
    cur.executescript(
        "DROP TABLE estoque_veiculos;"
        "ALTER TABLE estoque_veiculos_new RENAME TO estoque_veiculos;"
    )
    conn.commit()


def _table_sql(conn, table_name):
    cur = conn.cursor()
    row = cur.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row["sql"] if row else ""


def _extract_create_table_sql(table_name):
    marker = f"CREATE TABLE IF NOT EXISTS {table_name}"
    start = SCHEMA_SQL.index(marker)
    end = SCHEMA_SQL.index(");", start) + 2
    return SCHEMA_SQL[start:end].replace("CREATE TABLE IF NOT EXISTS", "CREATE TABLE", 1)


def _rebuild_table(conn, table_name, create_sql, columns):
    cur = conn.cursor()
    temp_name = f"{table_name}_new"
    cur.execute(f"DROP TABLE IF EXISTS {temp_name}")
    cur.execute(create_sql.replace(f"CREATE TABLE {table_name}", f"CREATE TABLE {temp_name}", 1))
    cols = ", ".join(columns)
    cur.execute(f"INSERT INTO {temp_name} ({cols}) SELECT {cols} FROM {table_name}")
    cur.execute(f"DROP TABLE {table_name}")
    cur.execute(f"ALTER TABLE {temp_name} RENAME TO {table_name}")


def _migrar_constraints(conn):
    """Recria tabelas antigas para aplicar CHECKs adicionados ao schema."""
    targets = [
        ("users", "CHECK (role IN", ["id", "username", "password", "role"]),
        ("veiculos", "CHECK (preco >= 0)", ["id", "marca_id", "modelo_id", "chassi", "ano_fabricacao", "cor", "preco"]),
        ("pecas", "CHECK (preco >= 0)", ["id", "nome", "categoria_id", "preco"]),
        ("estoque_veiculos", "CHECK (quantidade >= 0)", ["modelo_id", "quantidade"]),
        ("estoque_pecas", "CHECK (quantidade >= 0)", ["peca_id", "quantidade"]),
        ("vendas", "CHECK (tipo IN", ["id", "data", "tipo", "total"]),
        ("venda_itens", "CHECK (tipo_produto IN", ["id", "venda_id", "produto_id", "tipo_produto", "quantidade", "preco_unitario"]),
        ("ordem_servico", "CHECK (valor_mao_de_obra >= 0)", ["id", "cliente_id", "veiculo_cliente_id", "tipo_servico", "entrada", "saida", "valor_mao_de_obra", "valor_peca"]),
    ]
    missing = [(name, cols) for name, marker, cols in targets if marker not in _table_sql(conn, name)]
    if not missing:
        return

    conn.commit()
    conn.execute("PRAGMA foreign_keys = OFF;")
    try:
        for table_name, columns in missing:
            _rebuild_table(conn, table_name, _extract_create_table_sql(table_name), columns)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.execute("PRAGMA foreign_keys = ON;")


def seed_users(conn):
    """Insere os usuários-semente, ignorando duplicados."""
    cur = conn.cursor()
    cur.executemany(
        "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
        [(username, hash_password(password), role) for username, password, role in DEFAULT_USERS],
    )
    _migrar_senhas_plaintext(conn)
    conn.commit()


def _migrar_senhas_plaintext(conn):
    cur = conn.cursor()
    rows = cur.execute("SELECT id, password FROM users").fetchall()
    for row in rows:
        if not is_password_hash(row["password"]):
            cur.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (hash_password(row["password"]), row["id"]),
            )


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
