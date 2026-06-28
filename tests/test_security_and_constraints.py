import sqlite3

import pytest

from controller.login_controller import LoginController


def test_login_seed_com_hash_sucesso_e_senha_errada(conn):
    auth = LoginController(conn)

    ok = auth.authenticate("operador.admin", "senha123")
    assert ok["success"] is True
    assert ok["role"] == "admin"

    erro = auth.authenticate("operador.admin", "errada")
    assert erro == {"success": False, "message": "Usuario ou senha invalidos!"}


def test_senhas_seed_nao_ficam_em_texto_puro(conn):
    rows = conn.execute("SELECT password FROM users").fetchall()
    assert rows
    assert all(row["password"].startswith("pbkdf2_sha256$") for row in rows)
    assert all(row["password"] != "senha123" for row in rows)


def test_check_role_invalido_no_schema(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("x", "hash", "papel_invalido"),
        )


def test_check_venda_tipo_produto_invalido_no_schema(conn):
    venda_id = conn.execute(
        "INSERT INTO vendas (tipo, total) VALUES (?, ?)",
        ("peca", 10.0),
    ).lastrowid
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO venda_itens "
            "(venda_id, produto_id, tipo_produto, quantidade, preco_unitario) "
            "VALUES (?, ?, ?, ?, ?)",
            (venda_id, 1, "servico", 1, 10.0),
        )


def test_check_ordem_servico_valores_negativos_no_schema(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO ordem_servico "
            "(cliente_id, veiculo_cliente_id, tipo_servico, valor_mao_de_obra, valor_peca) "
            "VALUES (?, ?, ?, ?, ?)",
            (1, 1, "Revisao", -1.0, 0.0),
        )
