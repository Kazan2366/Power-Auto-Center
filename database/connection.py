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
    preco REAL,
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
    modelo_id INTEGER PRIMARY KEY,
    quantidade INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (modelo_id) REFERENCES modelos(id) ON DELETE CASCADE
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
    ("operador.cadastro", "senha123", "cadastro"),
    ("operador.vendas", "senha123", "vendas"),
    ("operador.mecanico", "senha123", "mecanico"),
    ("operador.admin", "senha123", "admin"),
]


def create_schema(conn):
    """Cria todas as tabelas (idempotente)."""
    conn.executescript(SCHEMA_SQL)
    _migrar_estoque_para_modelo(conn)


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
        "    quantidade INTEGER NOT NULL DEFAULT 0,"
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
