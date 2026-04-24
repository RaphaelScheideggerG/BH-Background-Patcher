import os
import shutil
import platform


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
    
    all_maps = get_all_backgrounds(bg_dir)
    
    # --- O AJUSTE DE ELITE ---
    # Pegamos apenas o nome final de cada arquivo que o usuário selecionou
    # Ex: 'C:/Downloads/BG_Small.jpg' vira 'BG_Small.jpg'
    clean_target_list = [os.path.basename(t) for t in target_list]
    
    if mode_exception:
        # Substitui tudo, exceto os que estão na lista de exceção
        to_replace = [m for m in all_maps if m not in clean_target_list]
    else:
        # Substitui APENAS os que estão na lista de alvos
        to_replace = [m for m in all_maps if m in clean_target_list]

    for map_file in to_replace:
        dest = os.path.join(bg_dir, map_file)
        shutil.copy(source_img, dest)
        
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
    # 1. Busca o caminho automaticamente
    game_path = get_default_brawlhalla_path()
    
    # 2. Validações de regra de negócio
    if not game_path:
        raise FileNotFoundError("Diretório do Brawlhalla não encontrado automaticamente.")
    
    if not verify_path(game_path):
        raise NotADirectoryError("O caminho do jogo existe, mas a estrutura de pastas é inválida.")

    total = apply_patch(game_path, source_file, exception_mode, file_list)
    
    # log de execução
    print("--- INICIANDO PATCH ---")
    print(f"Modo: {'EXCEÇÃO' if exception_mode else 'ESPECÍFICO'}")
    print(f"Quantidade na lista: {len(file_list)}")
    print(f"Arquivo Principal: {source_file}")
    print(f"Caminho do Jogo: {game_path}")
    print("----------------------") 

    return total, game_path