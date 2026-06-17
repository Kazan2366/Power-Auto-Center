from database.connection import create_connection

class LoginController:
    def __init__(self, connection):
        self.connection = connection
    
    def authenticate(self, username: str, password: str) -> dict:
        """Autentica usuário e retorna role se bem-sucedido."""
        try:
            cur = self.connection.cursor()
            cur.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?;",
                (username, password)
            )
            user = cur.fetchone()
            
            if user:
                return {
                    "success": True,
                    "role": user["role"],
                    "username": user["username"]
                }
            else:
                return {
                    "success": False,
                    "message": "Usuário ou senha inválidos!"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao autenticar: {str(e)}"
            }