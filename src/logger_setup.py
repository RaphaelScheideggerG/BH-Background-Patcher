import sys
import logging
from pathlib import Path

def _get_base_dir():
    """Detecta se está rodando como .exe ou script de desenvolvimento."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent

# Configura o caminho do log ao lado da pasta de backup
BASE_DIR = _get_base_dir()
LOG_FILE = BASE_DIR / "bhbp_app.log"

# Define o formato padrão das mensagens
log_formatter = logging.Formatter(
    fmt="%(asctime)s - [%(levelname)s] - [%(name)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Configura o manipulador de arquivo (File Handler)
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8", mode="a")
file_handler.setFormatter(log_formatter)

# Configura o manipulador de console (Stream Handler) para você continuar vendo no terminal em Dev
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)

# Configura o Logger Raiz do seu projeto
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

def get_logger(module_name):
    """Retorna um logger customizado com o nome do componente atual."""
    return logging.getLogger(module_name)
