import sys
from PyQt5.QtWidgets import QApplication
from pallet_calculator_app import PalletCalculatorApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PalletCalculatorApp()
    window.show()
    sys.exit(app.exec_())