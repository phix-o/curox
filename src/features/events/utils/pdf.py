import io
from dataclasses import dataclass
from datetime import datetime
from typing import IO

import pendulum
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (CircleModuleDrawer,
                                               RoundedModuleDrawer)
from qrcode.main import QRCode
from reportlab.lib import colors
from reportlab.lib.pagesizes import A5 as PDFPageSize
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Table, TableStyle


def generate_qrcode(code: str):
    qr = QRCode(
        border=0,
        box_size=20,
        error_correction=qrcode.ERROR_CORRECT_H)
    qr.add_data(code)
    image = qr.make_image(image_factory=StyledPilImage,
                          fill_color='pink', back_color='white',
                          module_drawer=CircleModuleDrawer(),
                          eye_drawer=RoundedModuleDrawer())

    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')

    return image_bytes


unit = cm
padding = 0.5 * unit
canvas_width = PDFPageSize[0]
canvas_height = PDFPageSize[1]

def from_top_percent(percent: float) -> float:
    top = percent * canvas_height
    return canvas_height - top

def from_left_percent(percent: float) -> float:
    amount = abs(percent) * canvas_width
    if percent < 0:
        return canvas_width - amount

    return amount


@dataclass
class CanvasConfig:
    font_size = 12
    font_name = 'Courier'
    text_color = colors.black
    accent_color = colors.Color(red=0, green=0.1, blue=0.3, alpha=0.1)
    background = colors.white

Config = CanvasConfig()

def draw_text(canvas: Canvas,
              text: str,
              y: float,
              x: float | None = None,
              font_size = Config.font_size,
              font_name = Config.font_name,
              text_color = Config.text_color,
              restore_color = True):
    canvas.setFontSize(font_size)
    canvas.setFont(font_name, font_size)
    canvas.setFillColor(text_color)

    text_width = stringWidth(text, fontName=font_name, fontSize=font_size)
    x = x if x is not None else from_left_percent(0.5) - text_width / 2
    text_obj = canvas.beginText(x=x, y=y)
    text_obj.textOut(text)
    canvas.drawText(text_obj)

    canvas.setFont(Config.font_name, Config.font_size)
    if restore_color:
        canvas.setFillColor(Config.text_color)


def generate_pdf(file: str | IO[bytes],
                 code: str,
                 logo: io.BytesIO,
                 event_name: str,
                 event_venue: str,
                 event_date: datetime,
                 table_records: list[dict]):
    canvas = Canvas(file, pagesize=PDFPageSize)
    canvas.setFont(Config.font_name, Config.font_size)

    # Handle the QR Code
    qr_code = generate_qrcode(code)
    qr_code = ImageReader(qr_code)
    qr_code_image_w = 2 * unit
    qr_code_image_h = qr_code_image_w
    canvas.drawImage(qr_code,
                     x=from_left_percent(0.5) - qr_code_image_w / 2,
                     y=from_top_percent(1) + padding,
                     width=qr_code_image_w,
                     height=qr_code_image_h)

    # Handle the logo
    logo_img = ImageReader(logo)
    logo_w, logo_h = logo_img.getSize()
    logo_aspect = logo_w / logo_h

    # Ensure the logo is never more than 60% wide
    logo_w = min(logo_w, 0.6 * canvas_width)
    # Ensure the logo in never more than 10% high
    logo_h = min(logo_w / logo_aspect, 0.15 * canvas_height)

    logo_top = from_top_percent(0) - logo_h - padding
    canvas.drawImage(logo_img,
                     x=from_left_percent(0.5) - logo_w / 2,
                     y=logo_top,
                     preserveAspectRatio=True,
                     width=logo_w,
                     height=logo_h)

    # Draw the event name
    y_top = logo_top - 1.25 * unit
    draw_text(canvas,
              text=event_name,
              y=y_top,
              font_size=24)
    y_top -= 24

    # Draw the event venue
    leading_size = Config.font_size + 0.2 * unit
    draw_text(canvas,
              text=event_venue,
              y=y_top,
              font_name='Helvetica-Bold')
    y_top -= leading_size

    # Draw the event date and time
    text_color = Config.text_color
    text_alpha = 0.6
    text_color.alpha = text_alpha

    event_date = pendulum.instance(event_date)
    date = event_date.format('dddd, MMMM Do, YYYY')
    draw_text(canvas,
              text=date,
              y=y_top,
              text_color=text_color,
              restore_color=False)
    y_top -= leading_size

    time = event_date.format('h:mm A')
    draw_text(canvas,
              text=time,
              y=y_top)
    canvas.setFillColor(Config.text_color)
    y_top -= leading_size

    # Draw the ticket table
    table_data = [
        ['#', 'Ticket', 'Table', 'Amount'],
    ]

    total_price = 0
    max_name_width = 0
    for i, record in enumerate(table_records):
        price: int = record['price']
        total_price += price

        name = record['name']
        name_width = stringWidth(name,
                                 fontName=Config.font_name,
                                 fontSize=Config.font_size)
        if name_width > max_name_width:
            max_name_width = name_width

        table_name: str = record['table']
        table_data.append([f'{i+1}', name, table_name, f'{price}'])
    
    y_top -= 2 * unit
    y_top -= 0.1 * unit
    max_height = 1 * unit
    max_width = canvas_width - 2 * padding

    first_col = 0.75 * unit
    last_col = 2 * unit
    ticket_col = max_name_width + 0.5 * unit
    table_col = max_width - (first_col + ticket_col + last_col)
    header_color = colors.Color(red=0, green=0, blue=0.2)
    table = Table(data=table_data,
                  colWidths=[first_col, ticket_col, table_col, last_col],
                  style=TableStyle([('BACKGROUND', (0, 0), (-1, 0), header_color),
                                    ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
                                    ('ALIGN',      (0, 0), (0, -1), 'CENTER'),
                                    ('ALIGN',      (-1, 0),(-1, -1), 'RIGHT')]))

    _, table_h = table.wrapOn(canvas, max_width, max_height)

    table_x = padding
    table.drawOn(canvas, table_x, y_top)

    y_top -= table_h + 0.5 * unit

    price_container_width = canvas_width / 2
    price_container_height = Config.font_size + (0.5 * unit)
    canvas.setFillColor(Config.accent_color)
    canvas.rect(x=from_left_percent(0.5) - price_container_width / 2,
                y=y_top,
                width=price_container_width,
                height=price_container_height,
                stroke=0,
                fill=1)
    canvas.setFillColor(Config.background)


    draw_text(canvas,
              f'KES. {total_price}',
              y=y_top + Config.font_size - 0.1 * unit,
              font_name='Helvetica-Bold')

    canvas.save()

if __name__ == '__main__':
    event_name = 'OSS Charity Gala 2023'
    event_venue = 'Emara Ole Sereni'
    event_date = datetime.now()
    table_records = [
        {'name': 'Jane Doe', 'table': 'Table 3', 'price': 7000},
        {'name': 'John Doe', 'table': 'Table 4', 'price': 7000},
    ]

    logo_bytes = io.BytesIO()
    with open('./logo.png', 'rb') as f:
        logo_bytes = io.BytesIO(f.read())

    generate_pdf('ticket.pdf',
                 code='102345',
                 logo=logo_bytes,
                 event_name=event_name,
                 event_venue=event_venue,
                 event_date=event_date,
                 table_records=table_records)

