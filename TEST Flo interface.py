import sys
from PyQt6.QtWidgets import QApplication, QWidget, QCheckBox, QGroupBox, QHBoxLayout, QVBoxLayout,  QSpinBox, QLabel

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Create checkboxes
        self.spinbox1 = QSpinBox(self)
        self.spinbox2 = QSpinBox(self)
        self.spinbox3 = QSpinBox(self)
        self.spinbox4 = QSpinBox(self)
        self.spinbox5 = QSpinBox(self)
        self.spinbox6 = QSpinBox(self)
        self.checkbox3 = QCheckBox('Random', self)
        self.checkbox4 = QCheckBox('Olders win', self)
        self.checkbox5 = QCheckBox('Youngers win', self)

        self.spinbox1.setRange(0, 100)
        V = QLabel('Food Value:')
        C = QLabel('Fight Cost:')
        N = QLabel('Initial Population:')
        M = QLabel('Maximum Population:')
        D = QLabel('Initial Dove Fraction:')
        G = QLabel('Simulation Length:')
        
        # Create layouts
        hbox1 = QHBoxLayout()
        hbox1.addWidget(V)
        hbox1.addWidget(self.spinbox1)
        hbox1.addWidget(C)
        hbox1.addWidget(self.spinbox2)
        hbox1.addWidget(N)
        hbox1.addWidget(self.spinbox3)
        hbox1.addWidget(M)
        hbox1.addWidget(self.spinbox4)
        hbox1.addWidget(D)
        hbox1.addWidget(self.spinbox5)
        hbox1.addWidget(G)
        hbox1.addWidget(self.spinbox6)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.checkbox3)
        hbox2.addWidget(self.checkbox4)
        hbox2.addWidget(self.checkbox5)

        hbox3 = QHBoxLayout()
        # Create group boxes
        groupbox1 = QGroupBox('General settings', self)
        groupbox1.setStyleSheet('QGroupBox{border: 2px solid black;}')
        groupbox1.setLayout(hbox1)

        groupbox2 = QGroupBox('Limitation of population', self)
        groupbox2.setStyleSheet('QGroupBox{border: 2px solid black;}')
        groupbox2.setLayout(hbox2)

        groupbox3 = QGroupBox('Other model additions', self)
        groupbox3.setStyleSheet('QGroupBox{border: 2px solid black;}')
        groupbox3.setLayout(hbox3)

        vbox = QVBoxLayout()
        vbox.addWidget(groupbox1)
        vbox.addWidget(groupbox2)
        vbox.addWidget(groupbox3)

        # Set the main layout
        self.setLayout(vbox)

        self.setGeometry(100, 100, 200, 100)
        self.setWindowTitle('Checkboxes')
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
