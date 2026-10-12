import re
import streamlit as st
import pandas as pd
import fitz
import base64

from io import StringIO
from io import BytesIO

from datetime import datetime
from datetime import timedelta
from streamlit_pdf_viewer import pdf_viewer

from PIL import Image as PILImage

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image
)

from reportlab.lib import colors
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="Aplikasi Pembuat SKP Karantina Tumbuhan Riau",
    layout="wide"
)

HEADER_IMAGE = "Header.png"  # Ganti dengan path gambar header Anda
STEMPEL_PATH = "Stempel.png" 

# ==================================================
# STYLE PDF
# ==================================================

styles = getSampleStyleSheet()

style_wrap = ParagraphStyle(
    name="WrapStyle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=11
)

style_judul = ParagraphStyle(
    "JudulLaporan",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=14,
    alignment=1,
    spaceAfter=10
)

style_sub_judul = ParagraphStyle(
    "SubJudul",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9,
    leading=14,
    alignment=1
)

# ==================================================
# BACA FILE KARANTINA
# ==================================================

def baca_laporan(file):
    """
    Baca file teks/CSV yang mungkin memiliki delimiter koma, tab, atau titik-koma.
    Mencari header baris yang kolom pertamanya mengandung 'No.' atau variasinya.
    Setelah menemukan header, baca dengan pandas (auto-detect delimiter).
    """
    isi = file.getvalue().decode(
        "utf-8",
        errors="ignore"
    )

    baris = isi.splitlines()

    header_idx = None
    header_line = None

    for i, line in enumerate(baris):
