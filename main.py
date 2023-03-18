# Project: Calculator

import sys

from main_window import MainWindow
from several import Display, Info, setupTheme, ButtonsGrid
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from variables import WINDOW_ICON_PATH



if __name__ == '__main__':
  
    # Cria a aplicação
    app = QApplication(sys.argv)
    setupTheme()
    window = MainWindow()

    # Define o ícone
    icon = QIcon(str(WINDOW_ICON_PATH))
    window.setWindowIcon(icon)
    app.setWindowIcon(icon)

    # Info
    info = Info('Sua conta')
    window.addWidgetToVLayout(info)

    # Display
    display = Display()
    window.addWidgetToVLayout(display)

    # Grid
    buttonsgrid = ButtonsGrid(display, info, window)
    window.vLayout.addLayout(buttonsgrid)

    # Executa tudo
    window.adjustFixedSize()
    window.show()
    app.exec()

    