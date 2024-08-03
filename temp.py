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
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

def draw_par(c, text, x, y, font="Helvetica", size=None, color=(0, 0, 0), alignment=1, weight=-1, height=-1, interline=1, max_rows=None):

    # Determine alignment
    if alignment == 0:
        align = TA_LEFT
    elif alignment == 2:
        align = TA_RIGHT
    elif alignment == 3:
        align = TA_JUSTIFY
    else:
        align = TA_CENTER

    # Set text color
    c.setFillColorRGB(color[0], color[1], color[2])

    # Adjust the font size to fit within the specified width
    if size is None:
        max_font_size = 200
        min_font_size = 1
        current_font_size = max_font_size
        leading=current_font_size * interline

        while current_font_size > min_font_size:
            # Create a style for the paragraph
            style = ParagraphStyle(
                name='CustomStyle',
                fontName=font,
                fontSize=current_font_size,
                leading=current_font_size * interline,
                textColor=color,
                alignment=align,
                leftIndent=0,
                rightIndent=0,
                spaceBefore=0,
                spaceAfter=0,
                borderPadding=0,
                allowOrphans=0,
                allowWidows=0
            )

            # Create a Paragraph object
            paragraph = Paragraph(text, style)

            # Wrap the paragraph to fit within the specified width and height
            if weight == -1:
                weight = c._pagesize[0] - x  # Default to the right edge of the page
            if height == -1:
                height = c._pagesize[1] - y  # Default to the top edge of the page

            width, para_height = paragraph.wrap(weight, height)
            lines = para_height / (current_font_size * interline)

            # Check if the paragraph fits within the specified width and height
            if width <= weight and (max_rows is None or lines <= max_rows):
                break

            # Reduce font size if the text doesn't fit
            current_font_size -= 0.5

    else:
        # Use the specified font size
        current_font_size = size

        style = ParagraphStyle(
            name='CustomStyle',
            fontName=font,
            fontSize=current_font_size,
            leading=current_font_size * interline,
            textColor=color,
            alignment=align,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=0,
            spaceAfter=0,
            borderPadding=0,
            allowOrphans=0,
            allowWidows=0
        )

        paragraph = Paragraph(text, style)
        if weight == -1:
            weight = c._pagesize[0] - x  # Default to the right edge of the page
        if height == -1:
            height = c._pagesize[1] - y  # Default to the top edge of the page

        width, para_height = paragraph.wrap(weight, height)

    # Draw the paragraph
    paragraph.drawOn(c, x, y-para_height+(current_font_size*0.3))

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
pdfmetrics.registerFont(TTFont('ArchivoBlack','./assets/fonts/ArchivoBlack-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Barlow','./assets/fonts/Barlow-Black.ttf'))

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

c.setStrokeColorRGB(70/256,31/256,124/256)
c.setLineWidth(6.5)
c.line(22.72,743,572.28,743)

# Define styles
styles = getSampleStyleSheet()
styleN = styles['Normal']

lorem = "Lorem Ipsum es simplemente el texto de relleno de las imprentas y archivos de texto. Lorem Ipsum ha sido el texto de relleno estándar de las industrias desde el año 1500, cuando un impresor (N. del T. persona que se dedica a la imprenta) desconocido usó una galería de textos y los mezcló de tal manera que logró hacer un libro de textos especimen. No sólo sobrevivió 500 años, sino que tambien ingresó como texto de relleno en documentos electrónicos, quedando esencialmente igual al original. Fue popularizado en los 60s con la creación de las hojas 'Letraset', las cuales contenian pasajes de Lorem Ipsum, y más recientemente con software de autoedición, como por ejemplo Aldus PageMaker, el cual incluye versiones de Lorem Ipsum."

# Draw Header
c.setFont(template["header"]["font"], template["header"]["size"])
c.drawString(template["header"]["x"], 600, "Header")

# Draw Image
img_path = "assets/images/slkasjldaslñ.png"
img_x = 234.87
img_y = 101.7
img_width = 337.4
img_height = 338.8
c.drawImage(img_path, img_x, img_y, img_width, img_height)

draw_par(c,"SUPERMAN: THE MAN OF TOMORROW", 22.72, 733, alignment=1, font="Barlow", weight=549.56, max_rows=2)

c.save()