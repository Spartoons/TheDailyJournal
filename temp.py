import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from babel.dates import format_date
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

def dotted_line(x_start, x_end, y, c):
    # Draw a dotted line using small circles
    dot_radius = 1
    dot_spacing = 2.8

    x = x_start
    while x < x_end:
        c.circle(y, x, dot_radius, stroke=0, fill=1)
        x += dot_spacing

# Load template
with open('template.json', 'r') as f:
    template = json.load(f)

c = canvas.Canvas("tempnews.pdf", pagesize=A4)
width, height = A4

# Add the title font
pdfmetrics.registerFont(TTFont('Abibas', './assets/fonts/abibas/Abibas.ttf'))

c.setStrokeColorRGB(0,0,0)
c.setLineWidth(2)
c.line(22.72,828,572.28,828)
c.drawImage("./assets/images/cursorhand.jpg", 22.72, 810, 15, 15)
c.setFont("Helvetica", 21.6)
c.drawString(40.72, 810, "0,00€")

dotted_line(810, 828, 107, c)

# Obtén la fecha y hora actual
now = datetime.now()

# Formatea la fecha en catalán
formatted_date = format_date(now, format='full', locale='ca')
formatted_date = formatted_date.upper()

datels = []
datels = formatted_date.split()
datels[0] = datels[0][:-1]
datn = datels[1]
restdate=" ".join(datels[1:])

c.setFont("Courier-Bold", 9)
c.drawString(117, 818, datels[0])
c.setFont("Courier-Bold", 9)
c.drawString(117, 810, restdate)
restdate_len = stringWidth(restdate, "Courier-Bold", 9)

dotted_line(810, 828, 117 + 10 + restdate_len, c)

c.setFont("Courier-Bold", 9)
c.drawString(117 + 20 + restdate_len, 818, "DIRECCIÓ DEL DIARI")
c.setFont("Courier-Bold", 9)
c.drawString(117 + 20 + restdate_len, 810, "MUNICIPI, NUMº de telf.")
info_len = stringWidth("MUNICIPI, NUMº de telf.", "Courier-Bold", 9)

dotted_line(810, 828, 137 + 10 + restdate_len + info_len, c)

c.setFont("Courier-Bold", 9)
c.drawString(137 + 20 + restdate_len + info_len, 818, "DIRECTOR")
c.setFont("Courier-Bold", 9)
c.drawString(137 + 20 + restdate_len + info_len, 810, "ARAN OLIVERAS")

datelen = stringWidth(datels[0], "Times-Bold", 11)
c.setFont("Times-Bold", 11)
c.drawString(572.28 - datelen, 791, datels[0])

width = stringWidth(datn, "Times-Roman", 56)
c.setFont("Times-Roman", 56)
c.drawString(572.28 - width, 750.45, datn)

# Draw Main Title
c.setFont(template["title"]["font"], template["title"]["size"])
c.drawString(template["title"]["x"], template["title"]["y"], template["title"]["text"])

c.setStrokeColorRGB(0,0,0)
c.setLineWidth(4)
c.line(22.72,743,572.28,743)

# Define styles
styles = getSampleStyleSheet()
styleN = styles['Normal']

lorem = "Lorem Ipsum es simplemente el texto de relleno de las imprentas y archivos de texto. Lorem Ipsum ha sido el texto de relleno estándar de las industrias desde el año 1500, cuando un impresor (N. del T. persona que se dedica a la imprenta) desconocido usó una galería de textos y los mezcló de tal manera que logró hacer un libro de textos especimen. No sólo sobrevivió 500 años, sino que tambien ingresó como texto de relleno en documentos electrónicos, quedando esencialmente igual al original. Fue popularizado en los 60s con la creación de las hojas 'Letraset', las cuales contenian pasajes de Lorem Ipsum, y más recientemente con software de autoedición, como por ejemplo Aldus PageMaker, el cual incluye versiones de Lorem Ipsum."
para = Paragraph(lorem)

# Draw Header
c.setFont(template["header"]["font"], template["header"]["size"])
c.drawString(template["header"]["x"], 600, "Header")

# Draw Articles
for i, article in enumerate(template["articles"]):
    # Draw Article Title
    c.setFont(article["title"]["font"], article["title"]["size"])
    if i == 0:
        c.drawString(article["title"]["x"], article["title"]["y"], "Article Title")
    else:
        c.drawString(article["title"]["x"], article["title"]["y"], article["title"]["text"])

    # Draw Article Body
    c.setFont(article["body"]["font"], article["body"]["size"])
    if i == 0:
        c.drawString(article["body"]["x"], article["body"]["y"], "lorem Ipsum")
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