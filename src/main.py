import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


the_app = QApplication(sys.argv)

# Define o tema da aplicação
the_app.setStyle("Fusion")

# Cra a janela principal
desktop = MainWindow()
desktop.show()

# Loop de eventos do Qt
sys.exit(the_app.exec())
