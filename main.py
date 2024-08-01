# main.py

import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

class NewspaperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Newspaper Creator')

        layout = QVBoxLayout()

        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText('Enter the main title')
        layout.addWidget(QLabel('Main Title'))
        layout.addWidget(self.title_input)

        self.header_input = QLineEdit(self)
        self.header_input.setPlaceholderText('Enter the header')
        layout.addWidget(QLabel('Header'))
        layout.addWidget(self.header_input)

        self.article_title_input = QLineEdit(self)
        self.article_title_input.setPlaceholderText('Enter the first article title')
        layout.addWidget(QLabel('Article Title'))
        layout.addWidget(self.article_title_input)

        self.article_body_input = QTextEdit(self)
        self.article_body_input.setPlaceholderText('Enter the first article body text')
        layout.addWidget(QLabel('Article Body'))
        layout.addWidget(self.article_body_input)

        self.generate_button = QPushButton('Generate PDF', self)
        self.generate_button.clicked.connect(self.generate_pdf)
        layout.addWidget(self.generate_button)

        self.setLayout(layout)
        self.show()

    def generate_pdf(self):
        main_title = self.title_input.text()
        header = self.header_input.text()
        article_title = self.article_title_input.text()
        article_body = self.article_body_input.toPlainText()

        # Load template
        with open('template.json', 'r') as f:
            template = json.load(f)

        c = canvas.Canvas("newspaper.pdf", pagesize=A4)
        width, height = A4

        # Draw Main Title
        c.setFont(template["title"]["font"], template["title"]["size"])
        c.drawString(template["title"]["x"], template["title"]["y"], main_title)

        # Draw Header
        c.setFont(template["header"]["font"], template["header"]["size"])
        c.drawString(template["header"]["x"], template["header"]["y"], header)

        # Draw Articles
        for i, article in enumerate(template["articles"]):
            # Draw Article Title
            c.setFont(article["title"]["font"], article["title"]["size"])
            if i == 0:
                c.drawString(article["title"]["x"], article["title"]["y"], article_title)
            else:
                c.drawString(article["title"]["x"], article["title"]["y"], article["title"]["text"])

            # Draw Article Body
            c.setFont(article["body"]["font"], article["body"]["size"])
            if i == 0:
                c.drawString(article["body"]["x"], article["body"]["y"], article_body)
            else:
                c.drawString(article["body"]["x"], article["body"]["y"], article["body"]["text"])

            # Draw Article Image if present
            if "image" in article:
                img_path = article["image"]["path"]
                img_x = article["image"]["x"]
                img_y = article["image"]["y"]
                img_width = article["image"]["width"]
                img_height = article["image"]["height"]
                c.drawImage(img_path, img_x, img_y, img_width, img_height)

        c.save()

if __name__ == '__main__':
    app = QApplication([])
    ex = NewspaperApp()
    app.exec_()
