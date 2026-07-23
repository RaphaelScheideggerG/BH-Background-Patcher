import sys
import shutil
import platform
import tempfile
from PIL import Image
from pathlib import Path


def get_default_brawlhalla_path():
    system = platform.system()
    home = Path.home()
    
    # Dicionário de caminhos padrão por OS usando pathlib
    paths = {
        "Windows": Path(r"C:\Program Files (x86)\Steam\steamapps\common\Brawlhalla"),
        "Linux": home / ".local" / "share" / "Steam" / "steamapps" / "common" / "Brawlhalla",
        "Darwin": home / "Library" / "Application Support" / "Steam" / "steamapps" / "common" / "Brawlhalla"
    }

    base_path = paths.get(system)
    if not base_path:
        return None

    # Verifica o caminho completo até a mapArt usando o operador /
    full_path = base_path / "mapArt" / "Backgrounds"
    
    # Verifica a existência do diretório diretamente pelo objeto Path
    if full_path.exists():
        return full_path
    return None


def get_all_backgrounds(bg_dir):
    """Varre a pasta final e retorna a lista de nomes de arquivos JPG que começam com BG_."""
    # Garante que bg_dir seja um objeto Path, mesmo se passarem string
    bg_dir = Path(bg_dir)
    
    if not bg_dir.exists():
        return []
    
    # .glob() busca direto por padrões, tornando o filtro mais rápido e limpo
    # .name pega apenas o nome do arquivo com a extensão (ex: "BG_Desert.jpg")
    return [f.name for f in bg_dir.glob("BG_*") if f.suffix.lower() == ".jpg"]


def apply_patch(game_path, source_img, mode_exception, target_list):
    """Aplica o patch copiando a imagem redimensionada para os arquivos de fundo do jogo. (Worker)"""
    bg_dir = Path(game_path)
    source_img = Path(source_img)

    make_backup(bg_dir)  # Faz backup se ainda não tiver sido feito

    # Redimensiona antes de copiar (resize_image deve retornar um objeto Path ou string)
    temp_path = Path(resize_image(source_img))
    to_replace = [] 

    try:
        all_maps = get_all_backgrounds(bg_dir)
        
        # Path(t).name extrai o nome do arquivo de forma segura, substituindo o os.path.basename
        clean_target_list = [Path(t).name for t in target_list]
        
        if mode_exception:
            # Substitui tudo, exceto os que estão na lista de exceção
            to_replace = [m for m in all_maps if m not in clean_target_list]
        else:
            # Substitui APENAS os que estão na lista de alvos
            to_replace = [m for m in all_maps if m in clean_target_list]

        for map_file in to_replace:
            dest = bg_dir / map_file
            # shutil aceita objetos Path nativamente a partir do Python 3.6
            shutil.copy(temp_path, dest)
    
    # Limpa o arquivo temporário criado
    finally:        
        if temp_path.exists():
            temp_path.unlink()

    return len(to_replace)


def verify_path(mapart_path):
    """Verifica se o caminho existe e é uma pasta válida do Brawlhalla."""
    mapart_path = Path(mapart_path)

    # Verifica se o caminho existe    
    if not mapart_path.exists():
        return False
    
    # Verifica se é o diretório correto olhando o nome da pasta final (mapArt/Backgrounds)
    if mapart_path.name == "Backgrounds":
        return True
    
    # Monta o subdiretório usando o operador /
    required_subdir = mapart_path / "mapArt" / "Backgrounds"
    return required_subdir.exists()


def run_patch_process(game_path, source_file, exception_mode, file_list):
    """
    Executor do patch (Controller)
    Recebe o caminho validado da UI e coordena o processo.
    """
    game_path = Path(game_path)
    
    # Garante que a UI não mandou um caminho inválido (extra de segurança)
    if not verify_path(game_path):
        raise NotADirectoryError("Estrutura de pastas inválida para o Brawlhalla.")

    # 2. Define exatamente onde é a pasta Backgrounds
    if game_path.name == "Backgrounds":
        bg_dir = game_path
    else:
        bg_dir = game_path / "mapArt" / "Backgrounds"

    # 3. Manda o operário trabalhar NA PASTA CERTA
    total = apply_patch(bg_dir, source_file, exception_mode, file_list)
    
    # execution log
    print("--- STARTING PATCH ---")
    print(f"Mode: {'EXCEPTION' if exception_mode else 'SPECIFIC'}")
    print(f"List quantity: {len(file_list)}")
    print(f"Main file: {source_file}")
    print(f"Target dir: {bg_dir}")
    print("----------------------") 

    return total, bg_dir


def resize_image(source_path, size=(2048, 1151)):
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
