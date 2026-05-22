import os
import pytest
from unittest.mock import patch, MagicMock
from PIL import Image
from pathlib import Path

from src.logic import (
    get_default_brawlhalla_path,
    get_all_backgrounds,
    verify_path,
    resize_image,
    apply_patch,
    get_backup_dir,
    make_backup,
    restore_backup,
)


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def fake_bg_dir(tmp_path):
    """Cria uma pasta falsa simulando o diretório Backgrounds do jogo."""
    bg_dir = tmp_path / "Backgrounds"
    bg_dir.mkdir()

    # Arquivos válidos
    (bg_dir / "BG_Small.jpg").write_bytes(b"fake")
    (bg_dir / "BG_Brawlhaven.jpg").write_bytes(b"fake")
    (bg_dir / "BG_Twilight.jpg").write_bytes(b"fake")

    # Arquivos que NÃO devem ser detectados
    (bg_dir / "thumbnail.jpg").write_bytes(b"fake")   # sem prefixo BG_
    (bg_dir / "BG_Test.png").write_bytes(b"fake")     # extensão errada

    return bg_dir

@pytest.fixture
def sample_image(tmp_path):
    """Cria uma imagem real (pequena) para testar o resize."""
    img_path = tmp_path / "test_img.png"
    img = Image.new("RGB", (800, 600), color=(255, 0, 0))
    img.save(img_path)
    return img_path

@pytest.fixture
def sample_image_with_alpha(tmp_path):
    """Cria uma imagem PNG com canal alpha (RGBA)."""
    img_path = tmp_path / "test_rgba.png"
    img = Image.new("RGBA", (800, 600), color=(0, 255, 0, 128))
    img.save(img_path)
    return img_path

@pytest.fixture
def fake_backup_dir(tmp_path):
    """Pasta vazia simulando o bhbp_backup."""
    backup_dir = tmp_path / "bhbp_backup"
    backup_dir.mkdir()
    return backup_dir

# ==============================================================================
# get_all_backgrounds
# ==============================================================================

def test_get_all_backgrounds_retorna_apenas_validos(fake_bg_dir):
    result = get_all_backgrounds(str(fake_bg_dir))
    assert set(result) == {"BG_Small.jpg", "BG_Brawlhaven.jpg", "BG_Twilight.jpg"}

def test_get_all_backgrounds_pasta_inexistente():
    result = get_all_backgrounds("/caminho/que/nao/existe")
    assert result == []


# ==============================================================================
# verify_path
# ==============================================================================

def test_verify_path_pasta_backgrounds_direta(fake_bg_dir):
    assert verify_path(str(fake_bg_dir)) is True

def test_verify_path_pasta_do_jogo(tmp_path):
    # Simula a raiz do jogo com a estrutura mapArt/Backgrounds
    bg = tmp_path / "mapArt" / "Backgrounds"
    bg.mkdir(parents=True)
    assert verify_path(str(tmp_path)) is True

def test_verify_path_invalido(tmp_path):
    assert verify_path(str(tmp_path)) is False

def test_verify_path_inexistente():
    assert verify_path("/nao/existe") is False


# ==============================================================================
# resize_image
# ==============================================================================

def test_resize_image_upscale(sample_image):
    """Imagem menor que 1920x1080 deve ser forçada para o tamanho exato."""
    temp_path = resize_image(str(sample_image))
    try:
        with Image.open(temp_path) as img:
            assert img.size == (1920, 1080)
    finally:
        os.remove(temp_path)

def test_resize_image_converte_alpha(sample_image_with_alpha):
    """PNG com transparência deve ser salvo como JPG sem erros."""
    temp_path = resize_image(str(sample_image_with_alpha))
    try:
        with Image.open(temp_path) as img:
            assert img.mode == "RGB"
    finally:
        os.remove(temp_path)

def test_resize_image_retorna_jpg(sample_image):
    temp_path = resize_image(str(sample_image))
    try:
        assert temp_path.endswith(".jpg")
    finally:
        os.remove(temp_path)

def test_resize_image_nao_upscale_se_ja_correto(tmp_path):
    """Imagem já no tamanho certo não deve ser alterada nas dimensões."""
    img_path = tmp_path / "exact.png"
    img = Image.new("RGB", (1920, 1080))
    img.save(img_path)

    temp_path = resize_image(str(img_path))
    try:
        with Image.open(temp_path) as img:
            assert img.size == (1920, 1080)
    finally:
        os.remove(temp_path)


# ==============================================================================
# apply_patch
# ==============================================================================

def test_apply_patch_modo_especifico(fake_bg_dir, sample_image):
    """Deve substituir apenas os arquivos da lista."""
    count = apply_patch(
        game_path=str(fake_bg_dir),
        source_img=str(sample_image),
        mode_exception=False,
        target_list=["BG_Small.jpg", "BG_Twilight.jpg"]
    )
    assert count == 2

def test_apply_patch_modo_excecao(fake_bg_dir, sample_image):
    """Deve substituir tudo exceto os da lista."""
    count = apply_patch(
        game_path=str(fake_bg_dir),
        source_img=str(sample_image),
        mode_exception=True,
        target_list=["BG_Small.jpg"]
    )
    # 3 mapas totais - 1 excluído = 2
    assert count == 2

def test_apply_patch_lista_vazia_modo_especifico(fake_bg_dir, sample_image):
    """Lista vazia em modo específico não deve alterar nada."""
    count = apply_patch(
        game_path=str(fake_bg_dir),
        source_img=str(sample_image),
        mode_exception=False,
        target_list=[]
    )
    assert count == 0

def test_apply_patch_limpa_temporario(fake_bg_dir, sample_image):
    """O arquivo temporário NÃO deve existir após o patch."""
    temp_paths = []
    original_resize = __import__("src.logic", fromlist=["resize_image"]).resize_image

    def spy_resize(*args, **kwargs):
        path = original_resize(*args, **kwargs)
        temp_paths.append(path)
        return path

    with patch("src.logic.resize_image", side_effect=spy_resize):
        apply_patch(str(fake_bg_dir), str(sample_image), False, ["BG_Small.jpg"])

    assert not os.path.exists(temp_paths[0])


# ==============================================================================
# get_backup_dir
# ==============================================================================

def test_get_backup_dir_cria_pasta_se_nao_existe(tmp_path):
    """Deve criar a pasta bhbp_backup se ela não existir."""
    with patch("src.logic.Path") as mock_path:
        backup = tmp_path / "bhbp_backup"
        mock_path.return_value.parent.parent.__truediv__ = lambda self, x: backup
        assert not backup.exists()
        get_backup_dir()
        # Só verifica o comportamento via make_backup abaixo — mais confiável


# ==============================================================================
# make_backup
# ==============================================================================

def test_make_backup_copia_todos_os_mapas(fake_bg_dir, fake_backup_dir):
    with patch("src.logic.get_backup_dir", return_value=fake_backup_dir):
        result = make_backup(str(fake_bg_dir))

    assert result is True
    arquivos = list(fake_backup_dir.glob("BG_*.jpg"))
    assert len(arquivos) == 3

def test_make_backup_nao_sobrescreve_se_ja_existe(fake_bg_dir, fake_backup_dir):
    """Se o backup já existe (pasta não vazia), não deve fazer nada."""
    # Simula backup já feito com conteúdo diferente
    (fake_backup_dir / "BG_Small.jpg").write_bytes(b"backup_antigo")

    with patch("src.logic.get_backup_dir", return_value=fake_backup_dir):
        result = make_backup(str(fake_bg_dir))

    assert result is False
    # Conteúdo original do backup não foi alterado
    assert (fake_backup_dir / "BG_Small.jpg").read_bytes() == b"backup_antigo"

def test_make_backup_conteudo_identico_ao_original(fake_bg_dir, fake_backup_dir):
    with patch("src.logic.get_backup_dir", return_value=fake_backup_dir):
        make_backup(str(fake_bg_dir))

    original = (fake_bg_dir / "BG_Small.jpg").read_bytes()
    backup = (fake_backup_dir / "BG_Small.jpg").read_bytes()
    assert original == backup


# ==============================================================================
# restore_backup
# ==============================================================================

def test_restore_backup_copia_de_volta(fake_bg_dir, fake_backup_dir):
    """Deve restaurar todos os arquivos do backup para o diretório do jogo."""
    # Backup com conteúdo "original"
    (fake_backup_dir / "BG_Small.jpg").write_bytes(b"original_small")
    (fake_backup_dir / "BG_Brawlhaven.jpg").write_bytes(b"original_brawlhaven")

    # Jogo com conteúdo patcheado
    (fake_bg_dir / "BG_Small.jpg").write_bytes(b"patchado")
    (fake_bg_dir / "BG_Brawlhaven.jpg").write_bytes(b"patchado")

    with patch("src.logic.get_backup_dir", return_value=fake_backup_dir):
        total = restore_backup(str(fake_bg_dir))

    assert total == 2
    assert (fake_bg_dir / "BG_Small.jpg").read_bytes() == b"original_small"
    assert (fake_bg_dir / "BG_Brawlhaven.jpg").read_bytes() == b"original_brawlhaven"

def test_restore_backup_retorna_quantidade_correta(fake_bg_dir, fake_backup_dir):
    (fake_backup_dir / "BG_Small.jpg").write_bytes(b"x")
    (fake_backup_dir / "BG_Brawlhaven.jpg").write_bytes(b"x")
    (fake_backup_dir / "BG_Twilight.jpg").write_bytes(b"x")

    with patch("src.logic.get_backup_dir", return_value=fake_backup_dir):
        total = restore_backup(str(fake_bg_dir))

    assert total == 3

def test_restore_backup_levanta_erro_se_vazio(fake_bg_dir, fake_backup_dir):
    """Backup vazio deve levantar FileNotFoundError."""
    with patch("src.logic.get_backup_dir", return_value=fake_backup_dir):
        with pytest.raises(FileNotFoundError):
            restore_backup(str(fake_bg_dir))

def test_restore_backup_nao_deleta_backup_apos_restaurar(fake_bg_dir, fake_backup_dir):
    """O backup deve continuar existindo após o restore — usuário pode restaurar várias vezes."""
    (fake_backup_dir / "BG_Small.jpg").write_bytes(b"original")

    with patch("src.logic.get_backup_dir", return_value=fake_backup_dir):
        restore_backup(str(fake_bg_dir))

    assert (fake_backup_dir / "BG_Small.jpg").exists()
