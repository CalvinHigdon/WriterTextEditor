from PyQt6 import QtWidgets
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
import threading
import requests
import regex as re
import sys

class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        font = QtGui.QFont() 
        font.setFamily("Consolas")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)

        layout = QtWidgets.QHBoxLayout(self)
        leftLayout = QtWidgets.QVBoxLayout()

        self.textBox = QtWidgets.QTextEdit()
        self.textBox.setFont(font)
        # self.setStyleSheet(QtWidgets.QStringLiteral("font: 12pt \"Nyala\";"))

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.textBox)
        self.scrollArea.setLayout(QtWidgets.QVBoxLayout())

        self.threadCountButton = QtWidgets.QPushButton("Print Thread Count")
        self.threadCountButton.clicked.connect(lambda: print(threading.active_count()))

        self.displayText = QtWidgets.QLabel(alignment=Qt.AlignmentFlag.AlignTop)
        self.displayText.setFont(font)
        self.displayText.setWordWrap(True)

        self.scrollArea2 = QtWidgets.QScrollArea()
        self.scrollArea2.setWidgetResizable(True)
        self.scrollArea2.setWidget(self.displayText)
        self.scrollArea2.setLayout(QtWidgets.QVBoxLayout())

        leftLayout.addWidget(self.scrollArea)
        leftLayout.addWidget(self.threadCountButton)
        layout.addLayout(leftLayout)
        layout.addWidget(self.scrollArea2)
        self.setStyleSheet("background-color: #333; color: #fff;")


        self.textBox.textChanged.connect(self.on_text_changed)
        self.textBox.selectionChanged.connect(self.on_selection_changed)

        self.randomboolean = True
                
    def on_text_changed(self):
        # if hasattr(self, 'th') and self.th.is_alive():
        #     self.join()
        self.th = threading.Thread(target=self.update_text)
        self.th.start()
        self.randomboolean = False

    def on_selection_changed(self):
        if (self.randomboolean):
            return
        print("\nSelection changed")
        cursor = self.textBox.textCursor()
        print("Cursor at:" + str(cursor.positionInBlock()))
        line = cursor.block().text()
        print("Line: " + line[:cursor.positionInBlock()] + "|" + line[cursor.positionInBlock():])

        match1 = re.findall(r'\b\w+', line[:cursor.positionInBlock()])
        match2 = re.search(r'\w+\b', line[cursor.positionInBlock():])
        print("Match1: " + str(match1))
        print("Match2: " + str(match2))

        match = str(re.findall(r'\b\w+', line[:cursor.positionInBlock()])[-1])
        match += str(re.search(r'\w+\b', line[cursor.positionInBlock():]).group(0))

        print("Match: " + str(match))

        # print("Match Later: " + str(matchLater))
        # print("Match Earlier: " + str(matchEarlier))
        
    
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
        self.displayText.setText('\n'.join(rhymes))
        



if __name__ == '__main__':
    # sys.argv contains the list of command-line arguments passed to a Python script
    # could be used to create command-line interface for the application, enabling scripting
    app = QtWidgets.QApplication(sys.argv)

    window = Window()
    window.resize(1600, 900)
    window.show()
    sys.exit(app.exec())
