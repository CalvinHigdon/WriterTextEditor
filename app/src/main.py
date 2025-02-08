from PyQt6.QtWidgets import *
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
import threading
import requests
import regex as re
import sys
from pprint import pprint
from wordTools import WordTools
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
        self.wordList = []
        self.sortBy = "SCORE"
        self.wordTools = WordTools()

        leftLayout = QVBoxLayout()
        rightLayout = QVBoxLayout()
        rightHeader = QHBoxLayout()
        layout = QHBoxLayout()

        self.create_actions()
        self.create_menus()

        self.document = Document()

        self.textBox = QTextEdit()
        self.textBox.setFont(font)
        # self.setStyleSheet(QStringLiteral("font: 12pt \"Nyala\";"))

    # Left Layout
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
#"Return rhymes for <WORD> filtered by [ONE] sorted by [TWO]:"
#[ONE]: All, Nouns, Adjectives, Verbs, Prepositions, Articles
#[TWO]: Default, Alphabetical, Best Rhyme

    # Right Layout
        # Right Header
        self.TRLabel1 = QLabel("Returning rhymes for ")
        self.TRWordLabel = QLabel("NONE")
        self.TRLabel2 = QLabel("filtered by ")
        self.TRLabel3 = QLabel("sorted by ")
        self.TRLabel4 = QLabel("...")

        self.filterByComboBox = QComboBox()
        self.filterByComboBox.addItem("ALL")
        self.filterByComboBox.addItem("NOUNS")
        self.filterByComboBox.addItem("ADJECTIVES")
        self.filterByComboBox.addItem("VERBS")
        self.filterByComboBox.addItem("PREPOSITIONS")
        self.filterByComboBox.addItem("ARTICLES")

        self.sortByComboBox = QComboBox()
        # self.sortByComboBox.addItem("Relevance")
        self.sortByComboBox.addItem("SCORE")
        self.sortByComboBox.addItem("ALPHABETICAL")
        self.sortByComboBox.addItem("SYLLABLES")
        # self.sortByComboBox.currentIndex = 0


        rightHeader.addWidget(self.TRLabel1)
        rightHeader.addWidget(self.TRWordLabel)
        rightHeader.addWidget(self.TRLabel2)
        rightHeader.addWidget(self.filterByComboBox)
        rightHeader.addWidget(self.TRLabel3)
        rightHeader.addWidget(self.sortByComboBox)
        rightHeader.addWidget(self.TRLabel4)

        rightLayout.addLayout(rightHeader)
        rightLayout.addWidget(self.scrollArea2)

        # Add layouts to main layout
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)

        window.setLayout(layout)
        self.setStyleSheet("background-color: #333; color: #fff;")
        self.setCentralWidget(window)

        self.textBox.textChanged.connect(self.on_text_changed)
        self.textBox.selectionChanged.connect(self.on_selection_changed)
        self.sortByComboBox.currentIndexChanged.connect(self.disp_result)

    def create_actions(self):
        self.newAction = QtGui.QAction("New", self)
        self.newAction.triggered.connect(self.new_file)
        self.openAction = QtGui.QAction("Open", self)
        self.openAction.triggered.connect(self.open_file)
        self.saveAction = QtGui.QAction("Save", self)
        self.saveAction.triggered.connect(self.save)
        self.saveAsAction = QtGui.QAction("Save As", self)
        self.saveAsAction.triggered.connect(self.save_as)

    def create_menus(self):
        self.fileMenu = self.menuBar().addMenu("File")
        self.fileMenu.addAction(self.newAction)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu = self.menuBar().addMenu("Edit")
                
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
        self.TRWordLabel.setText(mostRecent.upper())
        parameter = {'rel_rhy': mostRecent, 'md': 'p'}
        response = requests.get('https://api.datamuse.com/words', parameter)
        res = response.json()
        # pprint(res)
        if len(res) != 0:
            self.wordList = res
            self.disp_result()
            # self.displayText.setText('\n'.join(self.get_words(res)))
        else:
            if not self.displayText.text():
                self.displayText.setText("No rhymes found for " + mostRecent)

    def disp_result(self):
        # rhymes.sort( key=lambda x: x['word'], reverse=False)
        # pprint(self.wordList)
        if self.sortByComboBox.currentText() == "SCORE":
            self.wordList.sort(key=lambda x: x['score'])
        elif self.sortByComboBox.currentText() == "ALPHABETICAL":
            self.wordList.sort(key=lambda x: x['word'])
        elif self.sortByComboBox.currentText() == "SYLLABLES":
            self.wordList.sort(key=lambda x: x['numSyllables'])
        self.displayText.setText('\n'.join(self.get_words(self.wordList)))
        return self.get_words(self.wordList)
    
    def get_words(self, response):
        return self.wordTools.get_intersection([word['word'] for word in response])
        # return [word['word'] for word in response]

    def new_file(self):
        self.document = Document()
        self.textBox.setText(self.document.content)

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
