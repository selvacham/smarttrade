import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QTextEdit, QVBoxLayout, QHBoxLayout, QComboBox, QSpinBox
)
from modules.angel_executor import AngelExecutor  # Assuming AngelExecutor is defined in modules/angel_executor.py

class BlitzHawkUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlitzHawk - Angel One Executor")
        self.setGeometry(100, 100, 400, 350)

        self.executor = AngelExecutor()  # Instantiate your executor object
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Login Button
        self.login_btn = QPushButton("Login to Angel")
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)

        # Symbol Input
        layout.addWidget(QLabel("Symbol"))
        self.symbol_input = QLineEdit()
        layout.addWidget(self.symbol_input)

        # Quantity Input
        layout.addWidget(QLabel("Quantity"))
        self.qty_input = QSpinBox()
        self.qty_input.setRange(1, 1000)
        layout.addWidget(self.qty_input)

        # CE/PE dropdown
        layout.addWidget(QLabel("Order Type"))
        self.order_type_dropdown = QComboBox()
        self.order_type_dropdown.addItems(["BUY", "SELL"])
        layout.addWidget(self.order_type_dropdown)

        # Submit Button
        self.submit_btn = QPushButton("Place Order")
        self.submit_btn.clicked.connect(self.place_order)
        layout.addWidget(self.submit_btn)

        # Log Output
        layout.addWidget(QLabel("Log"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def login(self):
        success = self.executor.login()
        self.log_output.append("Login successful" if success else "Login failed")

    def place_order(self):
        symbol = self.symbol_input.text()
        qty = self.qty_input.value()
        order_type = self.order_type_dropdown.currentText()

        result = self.executor.place_order(symbol, qty, order_type)
        self.log_output.append(f"Order Result: {result}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BlitzHawkUI()
    window.show()
    sys.exit(app.exec_())
