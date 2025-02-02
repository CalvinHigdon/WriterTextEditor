from PyQt6.QtWidgets import *
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
import threading
import requests
import regex as re
import sys
from document import Document

class QMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        font = QtGui.QFont() 
        font.setFamily("Consolas")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)

        window = QWidget()

        leftLayout = QVBoxLayout()
        layout = QHBoxLayout()

        # self.toolBar = QToolBar()
        # self.toolBar.setMovable(False)
        # self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        self.create_actions()
        self.create_menus()

        self.document = Document()

        self.textBox = QTextEdit()
        self.textBox.setFont(font)
        # self.setStyleSheet(QStringLiteral("font: 12pt \"Nyala\";"))

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.textBox)
        self.scrollArea.setLayout(QVBoxLayout())

        self.threadCountButton = QPushButton("Print Thread Count")
        self.threadCountButton.clicked.connect(lambda: print(threading.active_count()))

        self.displayText = QLabel(alignment=Qt.AlignmentFlag.AlignTop)
        self.displayText.setFont(font)
        self.displayText.setWordWrap(True)

        self.scrollArea2 = QScrollArea()
        self.scrollArea2.setWidgetResizable(True)
        self.scrollArea2.setWidget(self.displayText)
        self.scrollArea2.setLayout(QVBoxLayout())

        leftLayout.addWidget(self.scrollArea)
        leftLayout.addWidget(self.threadCountButton)
        layout.addLayout(leftLayout)
        layout.addWidget(self.scrollArea2)
        self.setStyleSheet("background-color: #333; color: #fff;")

        window.setLayout(layout)
        self.setCentralWidget(window)

        self.textBox.textChanged.connect(self.on_text_changed)
        self.textBox.selectionChanged.connect(self.on_selection_changed)

    def create_actions(self):
        self.openAction = QtGui.QAction("Open", self)
        self.openAction.triggered.connect(self.open_file)
        self.saveAction = QtGui.QAction("Save", self)
        self.saveAction.triggered.connect(self.save)
        self.saveAsAction = QtGui.QAction("Save As", self)
        self.saveAsAction.triggered.connect(self.save_as)

    def create_menus(self):
        self.fileMenu = self.menuBar().addMenu("File")
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
                
    def on_text_changed(self):
        self.th = threading.Thread(target=self.update_text)
        self.th.start()

    def on_selection_changed(self):
        cursor = self.textBox.textCursor()
        line = cursor.block().text()

        match1 = re.match(r'[\S]+', line[:cursor.positionInBlock()], flags=re.RegexFlag.REVERSE)
        match2 = re.match(r'[\S]+', line[cursor.positionInBlock():])
        match1 = match1.group(0) if match1 else ""
        match2 = match2.group(0) if match2 else ""
        match = re.sub(r'[^\w\sa-z]', '', match1 + match2)
        if match:
            self.update_text(match)
    
    def update_text(self, word=None):
        if word:
            mostRecent = word
        else:
            cleanText = re.sub(r'[^\w\sa-z]', '', self.textBox.textCursor().block().text().lower())
            mostRecent = cleanText.split()[-1]

        print("Requesting rhymes for:", mostRecent)
        parameter = {'rel_rhy': mostRecent}
        response = requests.get('https://api.datamuse.com/words', parameter)
        rhymes = response.json()
        rhymes = [word['word'] for word in rhymes]
        if len(rhymes) != 0:
            self.displayText.setText('\n'.join(rhymes))
        else:
            if not self.displayText.text():
                self.displayText.setText("No rhymes found for " + mostRecent)

    def open_file(self):
        fileName = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt)")
        if fileName[0]:
            with open(fileName[0], 'r') as file:
                self.document.load(fileName[0])
                self.textBox.setText(self.document.content)
    
    def save(self):
        self.document.content = self.textBox.toPlainText()
        self.document.updateModified()
        if self.document.file_name:
            self.document.save(self.document.file_name)
        else:
            self.save_as()

    def save_as(self):
        self.document.content = self.textBox.toPlainText()
        self.document.updateModified()
        fileName = QFileDialog.getSaveFileName(self, "Save File", "filename", "Text Files (*.txt)")
        print(fileName)
        if fileName[0]:
            self.document.save(fileName[0])
            self.document.file_name = fileName[0]
            

if __name__ == '__main__':
    # sys.argv contains the list of command-line arguments passed to a Python script
    # could be used to create command-line interface for the application, enabling scripting
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.resize(1600, 900)
    window.show()
    sys.exit(app.exec())
