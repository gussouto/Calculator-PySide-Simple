import qdarktheme
import re
import math

from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QPushButton, QGridLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import QLineEdit
from main_window import MainWindow
from variables import (BIG_FONT_SIZE, MEDIUM_FONT_SIZE, SMALL_FONT_SIZE, TEXT_MARGIN,
                       MINIMUM_WIDTH, PRIMARY_COLOR, DARKER_PRIMARY_COLOR, 
                       DARKEST_PRIMARY_COLOR, 
                            )

# Expressões regulares
NUM_OR_DOT_REGEX = re.compile(r'^[0-9.]$')

def isNumOrDot(string: str):
    return bool(NUM_OR_DOT_REGEX.search(string))

def convertToNumber(string:str):
    number = float(string)

    if number.is_integer():
        number = int(number)

    return number

def isValidNumber(string: str):
    valid = False
    try:
        float(string)
        valid = True

    except ValueError:
        valid = False
    
    return valid

def isEmpty(string: str):
    return len(string) == 0


# Display da Calculadora
class Display(QLineEdit):
    eqPressed = Signal()
    delPressed = Signal()
    clearPressed = Signal()
    inputPressed = Signal(str)
    opPressed = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configStyle()

    def configStyle(self):
        margins = [TEXT_MARGIN for _ in range(4)]
        fontDisplay = self.font()
        fontDisplay.setPixelSize(BIG_FONT_SIZE)
        self.setFont(fontDisplay)
        self.setPlaceholderText('Calculadora')  
        self.setStyleSheet('font-size: {BIG_FONT_SIZE}px;')
        self.setMinimumHeight(BIG_FONT_SIZE * 2)
        self.setMinimumWidth(MINIMUM_WIDTH)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setTextMargins(*margins)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        text = event.text().strip()
        key = event.key()
        KEYS = Qt.Key

        isEnter = key in [KEYS.Key_Enter, KEYS.Key_Return, KEYS.Key_Equal]
        isDelete = key in [KEYS.Key_Backspace, KEYS.Key_Delete, KEYS.Key_D]
        isEsc = key in [KEYS.Key_Escape, KEYS.Key_C]
        isOperator = key in [
            KEYS.Key_Plus, KEYS.Key_Minus, KEYS.Key_Slash,KEYS.Key_Asterisk,
            KEYS.Key_P,
            ]

        if isEnter:
            self.eqPressed.emit()
            return event.ignore()

        if isDelete:
            self.delPressed.emit()
            return event.ignore()

        if isEsc:
            self.clearPressed.emit()
            return event.ignore()

        if isOperator:
            if text.lower() == 'p':
                text = '^'
            self.opPressed.emit(text)
            return event.ignore()
        
        # Não passa daqui se não tiver texto        
        if isEmpty(text):
            return event.ignore()
        
        if isNumOrDot(text):
            self.inputPressed.emit(text)
            return event.ignore()


# Informações acima do display no canto direito
class Info(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setStyleSheet('font-size: {SMALL_FONT_SIZE}px;')
        self.setAlignment(Qt.AlignmentFlag.AlignRight)


# Tema da calculadora
qss = f"""
    QPushButton[cssClass="specialButton"] {{
        color: #fff;
        background: {PRIMARY_COLOR};
    }}
    QPushButton[cssClass="specialButton"]:hover {{
        color: #fff;
        background: {DARKER_PRIMARY_COLOR};
    }}
    QPushButton[cssClass="specialButton"]:pressed {{
        color: #fff;
        background: {DARKEST_PRIMARY_COLOR};
    }}   
"""

def setupTheme():
    qdarktheme.setup_theme(
        theme='dark',
        corner_shape='rounded',
        custom_colors={
            "[dark]": {
                "primary": f"{PRIMARY_COLOR}",
            },
            "[light]":{
                "primary": f"{PRIMARY_COLOR}",
            },
        },
        additional_qss = qss
    )


# Botões da calculadora
class Button(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configStyle()

    def configStyle(self):
        font = self.font()
        font.setPixelSize(MEDIUM_FONT_SIZE)
        self.setFont(font)
        self.setMinimumSize(75, 75)
        

class ButtonsGrid(QGridLayout):
    def __init__(self, display: Display, info: 'Info', window: 'MainWindow',
                  *args, **kwargs
    )-> None:
        super().__init__(*args, **kwargs)

        self._gridMask = [
            ['C', 'D', '^', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['N', '0', '.', '='],
        ]
        self.display = display
        self.info = info
        self.window = window
        self._equation = ''
        self._equationInitialValue = 'Sua conta'
        self._left = None
        self._right = None
        self._op = None

        self.equation = self._equationInitialValue
        self._makeGrid()
        
    @property
    def equation(self):
        return self._equation
    
    @equation.setter
    def equation(self, value):
        self._equation = value
        self.info.setText(value)


    def _makeGrid(self):
        self.display.eqPressed.connect(self._equal)
        self.display.delPressed.connect(self._backspace)
        self.display.clearPressed.connect(self._clear)
        self.display.inputPressed.connect(self._insertToDisplay)
        self.display.opPressed.connect(self._configLeftOp)
        
        for i, row in enumerate(self._gridMask):
            for j, buttonText in enumerate(row):
                button = Button(buttonText)

                if not isNumOrDot(buttonText) and not isEmpty(buttonText):
                    button.setProperty('cssClass', 'specialButton')
                    self._configSpecialButton(button)

                self.addWidget(button, i, j)
                slot = self._makeSlot(self._insertToDisplay, buttonText)
                self._connectButtonClicked(button, slot)
               

    def _connectButtonClicked(self, button, slot):
        button.clicked.connect(slot) 

# Botões especiais da calculadora
    def _configSpecialButton(self, button):
        text = button.text()

        if text == 'C':
            self._connectButtonClicked(button, self._clear)
        
        if text == 'D':
            self._connectButtonClicked(button, self._backspace)
        
        if text == 'N':
            self._connectButtonClicked(button, self._invertNumber)
              
        if text in '+-*/^':
            self._connectButtonClicked(
                button, 
                self._makeSlot(self._configLeftOp, text)
            )
            
        if text == '=':
            self._connectButtonClicked(button, self._equal)       

    @Slot()      
    def _makeSlot(self, func, *args, **kwargs):
        @Slot(bool)
        def realSlot(_):
            func(*args, **kwargs)
        return realSlot

    @Slot()
    def _invertNumber(self):
        displayText = self.display.text()
        

        if not isValidNumber(displayText):
            return
      
        number = convertToNumber(displayText) * -1
        self.display.setText(str(number))

        self.display.setFocus()

    @Slot()
    def _insertToDisplay(self, text):
        newDisplayValue = self.display.text() + text

        if not isValidNumber(newDisplayValue):
            return

        self.display.insert(text)
        self.display.setFocus()

    @Slot()
    def _clear(self):
        self._left = None
        self._right = None
        self._op = None
        self.equation = self._equationInitialValue
        self.display.clear()
        self.display.setFocus()

    @Slot() 
    def _configLeftOp(self, text):
        displayText = self.display.text()
        self.display.clear()
        self.display.setFocus()

        if not isValidNumber(displayText) and self._left is None:
            self._showError('Você não digitou nada!')
            return
        
        if self._left is None:
            self._left = convertToNumber(displayText)

        self._op = text
        self.equation = f'{self._left} {self._op} ???'

    @Slot()
    def _equal(self):
        displayText = self.display.text()

        if not isValidNumber(displayText):
            self._showError('Conta incompleta!')
            return
        
        if self._op == None:
            self._showError('Coloque o operador!')
            return
          
        self._right = convertToNumber(displayText)
        self.equation = f'{self._left} {self._op} {self._right}'
        result = 'error'

        try:
            if '^' in self.equation and isinstance (self._left, int | float):
                result = math.pow(self._left, self._right)
            else:
                result = eval(self.equation)
        except ZeroDivisionError:
            self._showError('Divisão por zero!')
        except OverflowError:
            self._showError('Essa conta não pode ser realizada!')

        self.display.clear()
        self.info.setText(f'{self.equation} = {result}')
        self._left = result
        self._right = None
        self.display.setFocus()

        if result == 'error':
            self._left = None

    @Slot()
    def _backspace(self):
        self.display.backspace()
        self.display.setFocus()
  
    def _showError(self, text):
        msgBox = self.window.makeMsgBox()
        msgBox.setText(text)
        msgBox.setIcon(msgBox.Icon.Critical)
        msgBox.exec()



