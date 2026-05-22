import os
import sys
import shutil
import platform
import tempfile
from PIL import Image
from pathlib import Path


def get_default_brawlhalla_path():
    system = platform.system()
    home = os.path.expanduser("~")
    
    # Dicionário de caminhos padrão por OS
    paths = {
        "Windows": r"C:\Program Files (x86)\Steam\steamapps\common\Brawlhalla",
        "Linux": os.path.join(home, ".local/share/Steam/steamapps/common/Brawlhalla"),
        "Darwin": os.path.join(home, "Library/Application Support/Steam/steamapps/common/Brawlhalla") # MacOS no platform é 'Darwin'
    }

    base_path = paths.get(system)
    if not base_path:
        return None

    # Verifica o caminho completo até a mapArt
    full_path = os.path.join(base_path, "mapArt", "Backgrounds")
    
    if os.path.exists(full_path):
        return full_path
    return None

def get_all_backgrounds(bg_dir):
    """Varre a pasta final e retorna a lista de arquivos JPG que começam com BG_."""
    if not os.path.exists(bg_dir):
        return []
    
    # MUDANÇA: Agora checa o início (startswith) e a extensão (.jpg)
    return [f for f in os.listdir(bg_dir) 
            if f.startswith("BG_") and f.lower().endswith(".jpg")]

def apply_patch(game_path, source_img, mode_exception, target_list):
    # Garante o diretório correto
    if game_path.endswith("Backgrounds"):
        bg_dir = game_path
    else:
        bg_dir = os.path.join(game_path, "mapArt", "Backgrounds")

    make_backup(bg_dir)  # Faz backup se ainda não tiver sido feito

    # Redimensiona antes de copiar, e guarda o caminho temporário
    temp_path = resize_image(source_img)
    to_replace = [] # inicializa a variável para garantir que esteja definida mesmo se ocorrer um erro antes do loop de substituição

    try:
        all_maps = get_all_backgrounds(bg_dir)
        # Pega apenas o nome final de cada arquivo que o usuário selecionou para facilitar a comparação (sem caminhos)
        clean_target_list = [os.path.basename(t) for t in target_list]
        
        if mode_exception:
            # Substitui tudo, exceto os que estão na lista de exceção
            to_replace = [m for m in all_maps if m not in clean_target_list]
        else:
            # Substitui APENAS os que estão na lista de alvos
            to_replace = [m for m in all_maps if m in clean_target_list]

        for map_file in to_replace:
            dest = os.path.join(bg_dir, map_file)
            shutil.copy(temp_path, dest)
    
    # Limpa o arquivo temporário criado
    finally:        
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return len(to_replace)

def verify_path(mapart_path):
    """Verifica se o caminho existe e é uma pasta válida do Brawlhalla."""
    if not os.path.exists(mapart_path):
        return False
    
    # Verifica se o diretório selecionado é diretamente a pasta "Backgrounds"
    if os.path.basename(mapart_path) == "Backgrounds":
        return True
    
    # Caso contrário, verifica se é a pasta do jogo com o subdiretório "mapArt/Backgrounds"
    required_subdir = os.path.join(mapart_path, "mapArt", "Backgrounds")
    return os.path.exists(required_subdir)

def run_patch_process(source_file, exception_mode, file_list):
    """
    Executa o patch
    Retorna o total de arquivos alterados ou levanta uma Exception com os detalhes.
    """
    # Busca o caminho automaticamente
    if not game_path:
        game_path = get_default_brawlhalla_path()
    
    # Validações de regra de negócio
    if not game_path:
        raise FileNotFoundError("Diretório do Brawlhalla não encontrado automaticamente.")
    
    if not verify_path(game_path):
        raise NotADirectoryError("O caminho do jogo existe, mas a estrutura de pastas é inválida.")

    total = apply_patch(game_path, source_file, exception_mode, file_list)
    
    # execution log
    print("--- STARTING PATCH ---")
    print(f"Mode: {'EXCEPTION' if exception_mode else 'SPECIFIC'}")
    print(f"List quantity: {len(file_list)}")
    print(f"Main file: {source_file}")
    print(f"Game path: {game_path}")
    print("----------------------") 

    return total, game_path

def resize_image(source_path, size=(1920, 1080)):
    """
    Redimensiona a imagem para o padrão do Brawlhalla.
    Retorna o caminho do arquivo temporário gerado.
    """
    with Image.open(source_path) as img:
        # Converte para RGB — necessário para salvar como JPG (remove alpha de PNGs)
        if img.mode != "RGB":
            img = img.convert("RGB")

        width, height = img.size

        if width < size[0] or height < size[1]:
            # Imagem menor que o necessário: força o tamanho exato (upscale)
            img = img.resize(size, Image.LANCZOS)
        elif (width, height) != size:
            # Imagem maior mas proporção diferente: reduz mantendo proporção
            img.thumbnail(size, Image.LANCZOS)

        # Cria um arquivo temporário que persiste até você deletar manualmente
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        img.save(tmp.name, format="JPEG", quality=95)
        tmp.close()
        return tmp.name  # Retorna o caminho, ex: /tmp/tmpXk29a1.jpg

# *
# Backup e restore
# *
def get_backup_dir():
    """Retorna o caminho da pasta de backup, criando-a se necessário."""
    if getattr(sys, "frozen", False): # importante para detectar se está rodando como .exe empacotado
        # Rodando como .exe empacotado
        base = Path(sys.executable).parent
    else:
        # Rodando em dev — pasta raiz do projeto
        base = Path(__file__).parent.parent

    backup_dir = base / "bhbp_backup"
    backup_dir.mkdir(exist_ok=True)
    return backup_dir

def make_backup(bg_dir):
    """
    Faz backup dos arquivos originais do jogo.
    Só executa se a pasta de backup estiver vazia — garante que é sempre o original.
    Retorna True se fez backup, False se já existia.
    """
    backup_dir = get_backup_dir()

    # Pasta não vazia = backup já existe, não sobrescreve
    if any(backup_dir.iterdir()):
        return False

    bg_path = Path(bg_dir)
    for file in bg_path.glob("BG_*.jpg"):
        shutil.copy(file, backup_dir / file.name)

    return True

def restore_backup(bg_dir):
    """
    Copia os arquivos do backup de volta para o diretório do jogo.
    Retorna o número de arquivos restaurados, ou levanta erro se backup vazio.
    """
    backup_dir = get_backup_dir()

    files = list(backup_dir.glob("BG_*.jpg"))
    if not files:
        raise FileNotFoundError("Nenhum backup encontrado. Faça um patch primeiro.")

    bg_path = Path(bg_dir)
    for file in files:
        shutil.copy(file, bg_path / file.name)

    return len(files)
