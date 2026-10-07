import sys
import shutil
import platform
import tempfile
from PIL import Image, ImageOps
from pathlib import Path
from logger_setup import get_logger

logger = get_logger(__name__)


def get_default_brawlhalla_path():
    system = platform.system()
    home = Path.home()

    paths = {
        "Windows": [
            Path(r"C:\Program Files (x86)\Steam\steamapps\common\Brawlhalla")
        ],
        "Linux": [
            home / ".local" / "share" / "Steam" / "steamapps" / "common" / "Brawlhalla",
            home / "snap" / "steam" / "common" / ".local" / "share" /
            "Steam" / "steamapps" / "common" / "Brawlhalla",
        ],
        "Darwin": [
            home / "Library" / "Application Support" / "Steam" /
            "steamapps" / "common" / "Brawlhalla"
        ]
    }

    candidate_paths = paths.get(system)

    if not candidate_paths:
        logger.warning("Sistema operacional não suportado: %s", system)
        return None

    for base_path in candidate_paths:
        full_path = base_path / "mapArt" / "Backgrounds"

        if full_path.exists():
            logger.info(
                "Instalação do Brawlhalla encontrada: %s",
                full_path
            )
            return full_path

        logger.debug(
            "Caminho não encontrado: %s",
            full_path
        )

    logger.info("Nenhuma instalação padrão do Brawlhalla foi encontrada.")
    return None

def get_all_backgrounds(bg_dir):
    """Varre a pasta final e retorna a lista de nomes de arquivos JPG que começam com BG_."""
    bg_dir = Path(bg_dir)

    if not bg_dir.exists():
        logger.warning("Diretório de backgrounds não encontrado: %s", bg_dir)
        return []

    backgrounds = [
        f.name
        for f in bg_dir.glob("BG_*")
        if f.suffix.lower() == ".jpg"
    ]

    logger.info(
        "Backgrounds encontrados em %s: %d",
        bg_dir,
        len(backgrounds)
    )

    return backgrounds


def apply_patch(game_path, source_img, mode_exception, target_list):
    """Aplica o patch copiando a imagem redimensionada para os arquivos de fundo do jogo."""
    bg_dir = Path(game_path)
    source_img = Path(source_img)

    logger.info("Iniciando aplicação do patch.")
    logger.info("Diretório alvo: %s", bg_dir)
    logger.info("Imagem principal: %s", source_img)

    backup_created = make_backup(bg_dir)

    if backup_created:
        logger.info("Backup criado com sucesso.")
    else:
        logger.info("Nenhum novo backup criado. Backups existentes foram preservados.")

    temp_path = Path(resize_image(source_img))
    to_replace = []

    try:
        all_maps = get_all_backgrounds(bg_dir)

        clean_target_list = [Path(t).name for t in target_list]

        if mode_exception:
            logger.info("Modo selecionado: EXCEPTION")
            to_replace = [
                m for m in all_maps
                if m not in clean_target_list
            ]
        else:
            logger.info("Modo selecionado: SPECIFIC")
            to_replace = [
                m for m in all_maps
                if m in clean_target_list
            ]

        logger.info("Arquivos selecionados para substituição: %d", len(to_replace))

        for map_file in to_replace:
            dest = bg_dir / map_file
            shutil.copy(temp_path, dest)

        logger.info("Patch aplicado com sucesso em %d mapas.", len(to_replace))

    finally:
        if temp_path.exists():
            temp_path.unlink()
            logger.info("Arquivo temporário removido: %s", temp_path)

    return len(to_replace)


def verify_path(mapart_path):
    """Verifica se o caminho existe e é uma pasta válida do Brawlhalla."""
    mapart_path = Path(mapart_path)

    if not mapart_path.exists():
        logger.warning("Caminho informado não existe: %s", mapart_path)
        return False

    if mapart_path.name == "Backgrounds":
        logger.info("Diretório válido de Backgrounds: %s", mapart_path)
        return True

    required_subdir = mapart_path / "mapArt" / "Backgrounds"

    if required_subdir.exists():
        logger.info("Estrutura válida do Brawlhalla encontrada em: %s", mapart_path)
        return True

    logger.warning("Estrutura inválida para o Brawlhalla: %s", mapart_path)
    return False


def run_patch_process(game_path, source_file, exception_mode, file_list):
    """
    Executor do patch (Controller)
    Recebe o caminho validado da UI e coordena o processo.
    """
    game_path = Path(game_path)

    logger.info("--- STARTING PATCH ---")
    logger.info("Modo: %s", "EXCEPTION" if exception_mode else "SPECIFIC")
    logger.info("Quantidade na lista: %d", len(file_list))
    logger.info("Arquivo principal: %s", source_file)
    logger.info("Caminho recebido: %s", game_path)

    if not verify_path(game_path):
        logger.error("Patch abortado: estrutura de pastas inválida.")
        raise NotADirectoryError(
            "Estrutura de pastas inválida para o Brawlhalla."
        )

    if game_path.name == "Backgrounds":
        bg_dir = game_path
    else:
        bg_dir = game_path / "mapArt" / "Backgrounds"

    logger.info("Diretório final de Backgrounds: %s", bg_dir)

    total = apply_patch(
        bg_dir,
        source_file,
        exception_mode,
        file_list
    )

    logger.info("Patch finalizado. Total de mapas alterados: %d", total)
    logger.info("--- PATCH FINISHED ---")

    return total, bg_dir


def resize_image(source_path, size=(2048, 1151)):
    """
    Redimensiona mantendo a proporção e corta o excesso
    para preencher exatamente o tamanho desejado.
    """
    source_path = Path(source_path)

    logger.info(
        "Processando imagem: %s | Tamanho alvo: %s",
        source_path,
        size
    )

    with Image.open(source_path) as img:
        if img.mode != "RGB":
            logger.info(
                "Convertendo imagem de %s para RGB.",
                img.mode
            )
            img = img.convert("RGB")

        width, height = img.size
        original_size = (width, height)

        if original_size != size:
            logger.info(
                "Redimensionando imagem de %s para %s com preservação de proporção e corte.",
                original_size,
                size
            )
            img = ImageOps.fit(
                img,
                size,
                method=Image.Resampling.LANCZOS
            )

        tmp = tempfile.NamedTemporaryFile(
            suffix=".jpg",
            delete=False
        )

        img.save(
            tmp.name,
            format="JPEG",
            quality=95
        )

        tmp.close()

        logger.info(
            "Imagem processada com sucesso: %s",
            tmp.name
        )

        return tmp.name


# *
# Backup e restore
# *

def get_backup_dir():
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent.parent

    backup_dir = base / "bhbp_backup"
    backup_dir.mkdir(exist_ok=True)

    logger.info("Diretório de backup utilizado: %s", backup_dir.resolve())

    return backup_dir

def make_backup(bg_dir):
    """
    Faz backup dos arquivos originais do jogo.
    Arquivos que já possuem backup não são sobrescritos.
    Retorna True se algum backup foi criado, False caso contrário.
    """
    backup_dir = get_backup_dir()
    bg_path = Path(bg_dir)

    backup_created = False
    backup_count = 0

    for file in bg_path.glob("BG_*.jpg"):
        backup_file = backup_dir / file.name

        if not backup_file.exists():
            shutil.copy(file, backup_file)
            backup_created = True
            backup_count += 1

            logger.info(
                "Backup criado: %s",
                backup_file
            )
        else:
            logger.info(
                "Backup preservado: %s",
                backup_file
            )

    logger.info(
        "Processo de backup finalizado. Novos backups: %d",
        backup_count
    )

    return backup_created


def restore_backup(bg_dir):
    """
    Copia os arquivos do backup de volta para o diretório do jogo.
    Retorna o número de arquivos restaurados, ou levanta erro se backup vazio.
    """
    backup_dir = get_backup_dir()

    files = list(backup_dir.glob("BG_*.jpg"))

    if not files:
        logger.warning("Tentativa de restore sem backup disponível.")
        raise FileNotFoundError(
            "Nenhum backup encontrado. Faça um patch primeiro."
        )

    bg_path = Path(bg_dir)

    logger.info(
        "Iniciando restauração de %d arquivos para %s.",
        len(files),
        bg_path
    )

    for file in files:
        shutil.copy(file, bg_path / file.name)

    logger.info(
        "Restore concluído. Arquivos restaurados: %d",
        len(files)
    )

    return len(files)
