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
    ("operador.cadastro", "senha123", "cadastro"),
    ("operador.vendas", "senha123", "vendas"),
    ("operador.mecanico", "senha123", "mecanico"),
    ("operador.admin", "senha123", "admin"),
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
