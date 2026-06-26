-- Schema canônico (SQLite) — espelho de database/connection.py SCHEMA_SQL.
-- O runtime cria as tabelas automaticamente via create_connection().
-- Este arquivo é apenas documentação/referência.

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
