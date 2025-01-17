import json
import requests
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

# Configuration constants
FONT_PATHS = {
    'Abibas': './assets/fonts/abibas/Abibas.ttf',
    'ArchivoBlack': './assets/fonts/ArchivoBlack-Regular.ttf',
    'Barlow': './assets/fonts/Barlow-Black.ttf',
    'RobotoThin': './assets/fonts/Roboto-Thin.ttf',
    'RobotoLight': './assets/fonts/Roboto-Light.ttf'

}
IMAGE_PATH = "./assets/images/cursorhand.jpg"
IMG_PATH = "assets/images/slkasjldaslñ.png"
PDF_OUTPUT = "TheAran'sPost_" + str(datetime.now()).split(" ")[0]+".pdf"
TEMPLATE_PATH = 'template.json'

page = 1

# Read content
with open('content.json', 'r') as f:
            content = json.load(f)

with open('api_key.txt', 'r') as file:
    # Read the entire file content
    API_KEY = file.read()

# Define the element class to organize columns' content
class Element():
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

def register_fonts():
    """Register custom fonts."""
    for font_name, font_path in FONT_PATHS.items():
        pdfmetrics.registerFont(TTFont(font_name, font_path))

def draw_paragraph(c, text, x, y, font="Helvetica", size=None, color=(0, 0, 0), alignment=1, weight=-1, height=-1, interline=1, max_rows=None):
    """Draw a paragraph on the canvas with the given specifications."""
    # Determine alignment
    align = {0: TA_LEFT, 2: TA_RIGHT, 3: TA_JUSTIFY}.get(alignment, TA_CENTER)

    # Set text color
    c.setFillColorRGB(*color)

    if size == None:
        current_font_size = adjust_font_size(c, text, font, size, color, interline, align, x, y, weight, height, max_rows) if size is None else size
    else:
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
    width, para_height = paragraph.wrap(weight, height)
    y = y - para_height + (current_font_size * 0.3)
    paragraph.drawOn(c, x, y)
    return y

def adjust_font_size(c, text, font, size, color, interline, align, x, y, weight, height, max_rows):
    """Adjust the font size to fit within the specified width and height."""
    min_font_size, current_font_size = 1, 200

    while current_font_size > min_font_size:
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
            weight = c._pagesize[0] - x
        if height == -1:
            height = c._pagesize[1] - y     

        width, para_height = paragraph.wrap(weight, height)
        lines = para_height / (current_font_size * interline)

        if width <= weight and (max_rows is None or lines <= max_rows):
            break

        current_font_size -= 0.5

    return current_font_size

def draw_dotted_line(c, x_start, x_end, y):
    """Draw a dotted line using small circles."""
    dot_radius, dot_spacing = 1, 2.8
    x = x_start
    while x < x_end:
        c.circle(y, x, dot_radius, stroke=0, fill=1)
        x += dot_spacing

def draw_static_elements(c, template, formatted_date):
    """Draw the static elements on the canvas."""
    c.setStrokeColorRGB(0,0,0)
    c.setLineWidth(2)
    c.line(22.72,828,572.28,828)
    c.drawImage(IMAGE_PATH, 22.72, 810, 15, 15)
    c.setFont("Helvetica", 21.6)
    c.drawString(40.72, 810, "0,00€")
    draw_dotted_line(c, 810, 828, 107)

    datels = formatted_date.split()
    datels[0] = datels[0][:-1]
    datn, restdate = datels[1], " ".join(datels[1:])

    c.setFont("Courier-Bold", 9)
    c.drawString(117, 818, datels[0])
    c.drawString(117, 810, restdate)
    restdate_len = stringWidth(restdate, "Courier-Bold", 9)

    draw_dotted_line(c, 810, 828, 117 + 10 + restdate_len)

    c.drawString(117 + 20 + restdate_len, 818, "DIRECCIÓ DEL DIARI")
    c.drawString(117 + 20 + restdate_len, 810, "MUNICIPI, NUMº de telf.")
    info_len = stringWidth("MUNICIPI, NUMº de telf.", "Courier-Bold", 9)

    draw_dotted_line(c, 810, 828, 137 + 10 + restdate_len + info_len)

    c.drawString(137 + 20 + restdate_len + info_len, 818, "DIRECTOR")
    c.drawString(137 + 20 + restdate_len + info_len, 810, "ARAN OLIVERAS")

    datelen = stringWidth(datels[0], "Times-Bold", 11)
    c.setFont("Times-Bold", 11)
    c.drawString(572.28 - datelen, 791, datels[0])

    width = stringWidth(datn, "Times-Roman", 56)
    c.setFont("Times-Roman", 56)
    c.drawString(572.28 - width, 750.45, datn)

    c.setFont(template["title"]["font"], template["title"]["size"])
    c.drawString(template["title"]["x"], template["title"]["y"], template["title"]["text"])

    c.setStrokeColorRGB(70/256,31/256,124/256)
    c.setLineWidth(6.5)
    c.line(22.72,743,572.28,743)

    c.setStrokeColorRGB(0,0,0)
    c.setLineWidth(1)
    c.line(22.72,20,280.28,20)
    c.line(315,20,572.28,20)


    draw_paragraph(c, str(page), 0, 23, alignment=1, weight=595, size=10)


def get_weather(city):
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    geo_response = requests.get(geo_url)
    geo_data = geo_response.json()
    if not geo_data:
        return None
    
    lat = geo_data[0]['lat']
    lon = geo_data[0]['lon']
    
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data['cod'] == '200' and 'list' in data:
        # Use data from the first item in the list for simplicity
        forecast = data['list'][0]
        weather = {
            'city': data['city']['name'],
            'max_temp': round(forecast['main']['temp_max'] - 273.15, 2),
            'min_temp': round(forecast['main']['temp_min'] - 273.15, 2),
            'avg_temp': round(forecast['main']['temp'] - 273.15, 2),
            'wind_speed': forecast['wind']['speed'],
            'rain': forecast.get('rain', {}).get('3h', 0),
            'icon': forecast['weather'][0]['icon']
        }
        return weather
    else:
        return None

def draw_weather_section(c, city, x, y):
    weather = get_weather(city)
    c.setFillColorRGB(212/255, 243/255, 255/255)
    c.rect(x, y, 130, 60, fill=1)
    icon_path = f"./assets/weather_icons/{weather['icon']}.png"
    c.drawImage(icon_path, x + 7, y + 26, 33, 33, mask='auto')
    
    draw_paragraph(c, city, x + 50, y + 54, alignment=0, weight=75, max_rows=1)
    #draw_paragraph(c, f"Max Temp: {weather['max_temp']}°C", x + 5, y + 25, alignment=0, size=8)
    #draw_paragraph(c, f"Min Temp: {weather['min_temp']}°C", x + 5, y + 15, alignment=0, size=8)
    draw_paragraph(c, f"{weather['avg_temp']}°C", x + 50, y + 38, alignment=0, weight=130, size=17, color=(142/255, 160/255, 165/255), font="RobotoLight")
    #draw_paragraph(c, f"Wind: {weather['wind_speed']} m/s", x + 70, y + 25, alignment=0, size=8)
    if weather['rain']:
        draw_paragraph(c, f"Rain: {weather['rain']} mm", x + 70, y + 15, alignment=3, weight=130, size=9)

def main():
    """Main function to generate the PDF."""
    register_fonts()

    try:
        with open(TEMPLATE_PATH, 'r') as f:
            template = json.load(f)
    except FileNotFoundError:
        print(f"Template file not found: {TEMPLATE_PATH}")
        return

    c = canvas.Canvas(PDF_OUTPUT, pagesize=A4)
    width, height = A4

    now = datetime.now()
    formatted_date = format_date(now, format='full', locale='ca').upper()

    draw_static_elements(c, template, formatted_date)

    lorem = ("Lorem Ipsum es simplemente el texto de relleno de las imprentas y archivos de texto. "
             "Lorem Ipsum ha sido el texto de relleno estándar de las industrias desde el año 1500, "
             "cuando un impresor (N. del T. persona que se dedica a la imprenta) desconocido usó una "
             "galería de textos y los mezcló de tal manera que logró hacer un libro de textos especimen. "
             "No sólo sobrevivió 500 años, sino que tambien ingresó como texto de relleno en documentos "
             "electrónicos, quedando esencialmente igual al original. Fue popularizado en los 60s con la "
             "creación de las hojas 'Letraset', las cuales contenian pasajes de Lorem Ipsum, y más "
             "recientemente con software de autoedición, como por ejemplo Aldus PageMaker, el cual incluye "
             "versiones de Lorem Ipsum.")

    title_y = draw_paragraph(c, "SUPERMAN: THE MAN OF TOMORROW", 22.72, 730, alignment=1, font="Barlow", weight=549.56, max_rows=2)

    c.setStrokeColorRGB(0,0,0)
    c.setLineWidth(1)
    c.line(22.72, title_y - 10, 572.28, title_y - 10)

    weight_image = 410
    height_image = 338.8
    x_image = 22.72
    y_image = title_y - 22.5 - height_image

    c.drawImage(IMG_PATH, x_image, y_image, weight_image, height_image)

    draw_paragraph(c, lorem, 22.72, y_image-10, alignment=3, weight=130, height=y_image-10-26, size=9)
    #draw_paragraph(c, lorem, 162.72, y_image-10, alignment=3, weight=130, size=9)
    #draw_paragraph(c, lorem, 302.72, y_image-10, alignment=3, weight=130, size=9)
    #draw_paragraph(c, lorem, 442.72, title_y-25, alignment=3, weight=130, size=9)


    # Weather section
    city = 'Barcelona'
    draw_weather_section(c, city, 443.72, 65)

    c.save()

if __name__ == "__main__":
    main()
