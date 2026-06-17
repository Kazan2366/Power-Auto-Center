import pytest

from database.connection import create_connection


@pytest.fixture
def conn():
    """Conexão SQLite em memória com schema + usuários-semente."""
    connection = create_connection(":memory:")
    yield connection
    connection.close()
