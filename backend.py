"""Fachada única da camada de backend da Concessionária.

Ponto de entrada para o time de frontend: instancie `Backend()` e consuma os
atributos abaixo — cada um corresponde a uma opção do menu do sistema:

    Dashboard   -> backend.dashboard      (DashboardService)
    Clientes    -> backend.clientes       (ClienteController)
    Funcionários-> backend.funcionarios   (FuncionarioController)
    Usuários    -> backend.usuarios       (UsuarioController)
    Marcas      -> backend.marcas         (MarcaController)
    Categorias  -> backend.categorias     (CategoriaPecaController)
    Veículos    -> backend.veiculos       (VeiculoController)
    Vendas      -> backend.vendas         (VendaController)
    Financeiro  -> backend.financeiro     (FinanceiroService)
    Relatórios  -> backend.relatorios     (RelatorioService)
    Backup      -> backend.backup         (BackupService)
    (Sair é responsabilidade da camada de apresentação.)

Entidades de apoio também expostas: modelos, veículos do cliente, peças,
estoque, ordens de serviço, e autenticação (`auth`).
"""
from database.connection import create_connection, DB_FILE

from controller.login_controller import LoginController
from controller.cliente_controller import ClienteController
from controller.funcionario_controller import FuncionarioController
from controller.usuario_controller import UsuarioController
from controller.marca_controller import MarcaController
from controller.modelo_controller import ModeloController
from controller.categoria_peca_controller import CategoriaPecaController
from controller.veiculo_controller import VeiculoController
from controller.veiculo_cliente_controller import VeiculoClienteController
from controller.peca_controller import PecaController
from controller.estoque_controller import EstoqueController
from controller.venda_controller import VendaController
from controller.ordem_servico_controller import OrdemServicoController

from service import (
    DashboardService,
    FinanceiroService,
    RelatorioService,
    BackupService,
)


class Backend:
    """Fachada com conexão SQLite única, para uso na mesma thread."""

    def __init__(self, connection=None):
        self.connection = connection or create_connection()
        c = self.connection

        # Autenticação
        self.auth = LoginController(c)

        # Cadastros (CRUD)
        self.clientes = ClienteController(c)
        self.funcionarios = FuncionarioController(c)
        self.usuarios = UsuarioController(c)
        self.marcas = MarcaController(c)
        self.modelos = ModeloController(c)
        self.categorias = CategoriaPecaController(c)
        self.veiculos = VeiculoController(c)
        self.veiculos_cliente = VeiculoClienteController(c)
        self.pecas = PecaController(c)
        self.estoque = EstoqueController(c)
        self.vendas = VendaController(c)
        self.ordens_servico = OrdemServicoController(c)

        # Serviços derivados
        self.dashboard = DashboardService(c)
        self.financeiro = FinanceiroService(c)
        self.relatorios = RelatorioService(c)
        self.backup = BackupService(connection=c, db_path=DB_FILE)

    def fechar(self):
        """Fecha a conexão com o banco."""
        self.connection.close()
