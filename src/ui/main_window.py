from PySide6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, QApplication)
from PySide6.QtCore import Qt
from .mode_selection import ModeSelection
from logic import apply_patch, get_default_brawlhalla_path, verify_path


class MainWindow(QWidget):
    """Janela principal da aplicação."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Estado inicial
        self.file_path = ""
        self.exceptions = []

        self.setWindowTitle("Brawlhalla Background Patcher")
        self.resize(450, 300) # Aumentei um pouco a altura para os novos botões
        self.mode_selector = ModeSelection() # Instancia o widget de seleção de modo
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Header
        self.label_header = QLabel("Alterar Planos de Fundo")
        self.label_header.setAlignment(Qt.AlignCenter)
        self.label_header.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        # Seleção de Arquivo Principal
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
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.btn_start.clicked.connect(self.on_start_clicked)

        # Montagem do Layout
        layout.addWidget(self.label_header)
        layout.addWidget(self.open_file_button)
        layout.addWidget(self.file_path_label)
        layout.addSpacing(5)
        layout.addWidget(self.mode_selector)
        layout.addStretch()
        layout.addWidget(self.btn_start, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)

    # --- SLOTS ---

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Escolha o Fundo Principal", "", "Imagens (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.file_path = file_path
            file_name = file_path.split('/')[-1]
            self.file_path_label.setText(f"Principal: {file_name}")

    def on_start_clicked(self):
        if not self.file_path:
            self.label_header.setText("⚠️ SELECIONE O FUNDO PRIMEIRO!")
            self.label_header.setStyleSheet("color: red; font-weight: bold;")
            return
        
        # Tenta encontrar o caminho do jogo automaticamente
        game_path = get_default_brawlhalla_path()

        if not game_path or not verify_path(game_path):
            self.label_header.setText("⚠️ PASTA DO BRAWLHALLA NÃO ENCONTRADA!")
            self.label_header.setStyleSheet("color: red; font-weight: bold;")
            return

        # Puxando os dados do componente filho
        modo_excecao = self.mode_selector.get_mode()
        lista_de_arquivos = self.mode_selector.get_files_list()

        # Aplicando o patch com base nas escolhas do usuário
        try:
            total_alterado = apply_patch(
                game_path, 
                self.file_path, 
                modo_excecao, 
                lista_de_arquivos
            )

            # Feedback para o usuário 
            self.label_header.setText(f"✅ SUCESSO! {total_alterado} MAPAS ALTERADOS!")
            self.label_header.setStyleSheet("color: #2ecc71; font-weight: bold;")
            print(f"Patch aplicado com sucesso em {total_alterado} arquivos.")
            
        except Exception as e:
            self.label_header.setText(f"❌ ERRO CRÍTICO: {str(e)}")
            self.label_header.setStyleSheet("color: orange; font-weight: bold;")

        print("--- INICIANDO PATCH ---")
        print(f"Modo: {'EXCEÇÃO' if modo_excecao else 'ESPECÍFICO'}")
        print(f"Quantidade na lista: {len(lista_de_arquivos)}")
        print(f"Arquivo Principal: {self.file_path}")
        print(f"Caminho do Jogo: {game_path}")
        print("----------------------")
