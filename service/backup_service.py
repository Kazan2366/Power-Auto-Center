"""BackupService — cópia do banco SQLite para um arquivo datado.

Se uma `connection` for fornecida, usa a API de backup online do sqlite3
(consistente mesmo com a conexão em uso); caso contrário copia o arquivo .db.
"""
import datetime
import shutil
import sqlite3
from pathlib import Path

from database.connection import DB_FILE


class BackupService:
    def __init__(self, connection=None, db_path=None, dest_dir=None):
        self.connection = connection
        self.db_path = Path(db_path) if db_path else Path(DB_FILE)
        self.dest_dir = Path(dest_dir) if dest_dir else self.db_path.parent.parent / "backups"

    def criar_backup(self, dest_dir=None) -> str:
        destino_dir = Path(dest_dir) if dest_dir else self.dest_dir
        destino_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        destino = destino_dir / f"concessionaria-{ts}.db"
        if self.connection is not None:
            destino_conn = sqlite3.connect(str(destino))
            try:
                self.connection.backup(destino_conn)
            finally:
                destino_conn.close()
        else:
            shutil.copy2(self.db_path, destino)
        return str(destino)

    def listar_backups(self, dest_dir=None) -> list:
        destino_dir = Path(dest_dir) if dest_dir else self.dest_dir
        if not destino_dir.exists():
            return []
        return sorted(str(p) for p in destino_dir.glob("concessionaria-*.db"))
