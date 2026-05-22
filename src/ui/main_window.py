from PySide6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from .mode_selection import ModeSelection
from logic import run_patch_process, restore_backup, get_default_brawlhalla_path, verify_path


class MainWindow(QWidget):
    """Janela principal da aplicação."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.file_path = ""
        self.exceptions = []

        self.setWindowTitle("Brawlhalla Background Patcher")
        self.resize(450, 300)
        self.mode_selector = ModeSelection()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Header
        self.label_header = QLabel("Alterar Planos de Fundo")
        self.label_header.setAlignment(Qt.AlignCenter)
        self.label_header.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        # Seleção de Arquivo
        self.open_file_button = QPushButton("🖼️ Selecionar Fundo Principal")
        self.open_file_button.clicked.connect(self.select_file)
        
        self.file_path_label = QLabel("Nenhum arquivo selecionado")
        self.file_path_label.setStyleSheet("color: gray;")
        self.file_path_label.setAlignment(Qt.AlignCenter)

        # Botão START
        self.btn_start = QPushButton("START")
        self.btn_start.setFixedSize(150, 45)
        self.btn_start.setStyleSheet("""
            QPushButton {
                font-weight: bold; 
                background-color: #2ecc71; 
                color: white; 
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        self.btn_start.clicked.connect(self.on_start_clicked)

        # Botão RESTORE
        self.btn_restore = QPushButton("↩ Restaurar Original")
        self.btn_restore.setFixedHeight(28)
        self.btn_restore.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                color: #aaaaaa;
                border: 1px solid #aaaaaa;
                border-radius: 4px;
                padding: 0 8px;
                background-color: transparent;
            }
            QPushButton:hover { color: white; border-color: white; }
        """)
        self.btn_restore.clicked.connect(self.on_restore_clicked)

        # Botão DONATE
        self.btn_donate = QPushButton("☕ Donate")
        self.btn_donate.setFixedHeight(28)
        self.btn_donate.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                color: #f39c12;
                border: 1px solid #f39c12;
                border-radius: 4px;
                padding: 0 8px;
                background-color: transparent;
            }
            QPushButton:hover { color: white; border-color: white; }
        """)
        self.btn_donate.clicked.connect(self.on_donate_clicked)

        # Linha de baixo: restore | donate | START
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.btn_restore, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_start, alignment=Qt.AlignRight | Qt.AlignVCenter)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_donate, alignment=Qt.AlignVCenter)

        # Montagem
        layout.addWidget(self.label_header)
        layout.addWidget(self.open_file_button)
        layout.addWidget(self.file_path_label)
        layout.addSpacing(5)
        layout.addWidget(self.mode_selector)
        layout.addStretch()
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    # --- SLOTS ---

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Escolha o Fundo Principal", "", "Imagens (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.file_path = file_path
            self.file_path_label.setText(f"Principal: {file_path.split('/')[-1]}")

    def on_start_clicked(self):
        if not self.file_path:
            self.update_status("⚠️ SELECIONE O FUNDO PRIMEIRO!", "orange")
            return

        try:
            game_path = self._get_game_path()
            if not game_path:
                return  # usuário cancelou ou pasta inválida, status já foi atualizado


            modo_excecao = self.mode_selector.get_mode()
            lista_de_arquivos = self.mode_selector.get_files_list()

            total, final_path = run_patch_process(
                self.file_path, 
                modo_excecao, 
                lista_de_arquivos
            )
            self.update_status(f"✅ SUCESSO! {total} MAPAS ALTERADOS!", "#2ecc71")

        except FileNotFoundError as e:
            self.update_status(f"⚠️ {str(e)}", "orange")
        except Exception as e:
            self.update_status(f"❌ ERRO CRÍTICO: {str(e)}", "red")

    def on_restore_clicked(self):
        try:
            game_path = self._get_game_path()
            if not game_path:
                return

            total = restore_backup(game_path)
            self.update_status(f"↩ {total} MAPAS RESTAURADOS!", "#3498db")

        except FileNotFoundError as e:
            self.update_status(f"⚠️ {str(e)}", "orange")
        except Exception as e:
            self.update_status(f"❌ ERRO AO RESTAURAR: {str(e)}", "red")

    def on_donate_clicked(self):
        QDesktopServices.openUrl(QUrl("https://ko-fi.com/SEU_USUARIO"))

    def update_status(self, text, color):
        self.label_header.setText(text)
        self.label_header.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _get_game_path(self):
        """
        Tenta encontrar o diretório automaticamente.
        Se não achar, abre o diálogo nativo para o usuário selecionar.
        Retorna o caminho ou None se o usuário cancelar.
        """
        path = get_default_brawlhalla_path()
        if path:
            return path

        # Não encontrou automaticamente — abre diálogo
        selected = QFileDialog.getExistingDirectory(
            self,
            "Selecione a pasta do Brawlhalla",
            "",
            QFileDialog.ShowDirsOnly
        )

        if not selected:
            # Usuário fechou o diálogo sem selecionar
            return None

        if not verify_path(selected):
            self.update_status("⚠️ Pasta inválida. Selecione a pasta do jogo.", "orange")
            return None

        return selected
