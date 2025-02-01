from PyQt6.QtWidgets import *
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
import threading
import requests
import regex as re
import sys

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

        self.toolBar = QToolBar()
        self.toolBar.setMovable(False)

        self.toolBar.addAction("New")
        self.toolBar.addAction("Open")
        self.toolBar.addAction("Save")
        self.toolBar.addAction("Print")
        self.toolBar.addAction("Undo")
        self.toolBar.addAction("Redo")

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)


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
                
    def on_text_changed(self):
        # if hasattr(self, 'th') and self.th.is_alive():
        #     self.join()
        self.th = threading.Thread(target=self.update_text)
        self.th.start()

    def on_selection_changed(self):
        print("\nSelection changed")
        cursor = self.textBox.textCursor()
        print("Cursor at:" + str(cursor.positionInBlock()))
        line = cursor.block().text()
        print("Line: " + line[:cursor.positionInBlock()] + "|" + line[cursor.positionInBlock():])

        match1 = re.match(r'[\S]+', line[:cursor.positionInBlock()], flags=re.RegexFlag.REVERSE)
        match2 = re.match(r'[\S]+', line[cursor.positionInBlock():])
        match1 = match1.group(0) if match1 else ""
        match2 = match2.group(0) if match2 else ""
        print("Match1: " + str(match1))
        print("Match2: " + str(match2))
        match = re.sub(r'[^\w\sa-z]', '', match1 + match2)
        print("Match: " + str(match))

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
        



if __name__ == '__main__':
    # sys.argv contains the list of command-line arguments passed to a Python script
    # could be used to create command-line interface for the application, enabling scripting
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.resize(1600, 900)
    window.show()
    sys.exit(app.exec())
