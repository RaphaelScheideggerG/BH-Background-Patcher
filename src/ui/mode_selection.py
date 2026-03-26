# src/ui/mode_selection.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QRadioButton, QLabel, QFileDialog, QPushButton
from PySide6.QtCore import Qt


class ModeSelection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.exceptions = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self) # O (self) aqui já define o layout no widget
        
        self.exeption_mode = QRadioButton("Modo Exceção (Substituir tudo, exceto estes)")
        self.exeption_mode.setChecked(True)
        
        self.especific_mode = QRadioButton("Modo Específico (Substituir apenas estes)")

        # Botão de seleção para a lista secundária
        self.select_list_button = QPushButton("📂 Selecionar Lista de Arquivos (Opcional)")
        self.select_list_button.clicked.connect(self.select_list_files)

        # Contador de arquivos na lista secundária
        self.counter_label = QLabel("Arquivos na lista: 0")
        self.counter_label.setAlignment(Qt.AlignCenter)

        
        layout.addWidget(self.exeption_mode)
        layout.addWidget(self.especific_mode)
        layout.addSpacing(10)
        layout.addWidget(self.select_list_button)
        layout.addWidget(self.counter_label)

    def get_mode(self):
        """Método para a MainWindow 'perguntar' qual modo está ativo."""
        return self.exeption_mode.isChecked() # True para Exceção
    
    def get_files_list(self):
        """Retorna a lista de arquivos selecionados para o pai."""
        return self.exceptions
    
    def select_list_files(self):
        """Abre o seletor para a lista secundária (Exceções ou Específicos)."""
        titulo = "Selecionar Exceções" if self.exeption_mode.isChecked() else "Selecionar Alvos"
        arquivos, _ = QFileDialog.getOpenFileNames(
            self, titulo, ".", "Imagens (*.png *.jpg *.jpeg)"
        )
        if arquivos:
            self.exceptions = arquivos
            txt = "Exceções" if self.exeption_mode.isChecked() else "Alvos"
            self.counter_label.setText(f"{txt} na lista: {len(self.exceptions)}")