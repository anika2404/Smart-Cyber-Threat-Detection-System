import os
import io
import tempfile
from datetime import datetime

import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors



def safe_plotly_write_image(fig, path, width=1200, height=700):
    """
    Save plotly figure as PNG using kaleido.
    """
    fig.write_image(path, format="png", width=width, height=height)


def add_title_page(pdf, title, subtitle):
    width, height = landscape(A4)
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(50, height - 80, title)

    pdf.setFont("Helvetica", 14)
    pdf.drawString(50, height - 120, subtitle)

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, height - 160, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def add_stats_block(pdf, stats):
    width, height = landscape(A4)
    y = height - 220

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "Summary Statistics")

    pdf.setFont("Helvetica", 12)
    y -= 35
    for k, v in stats.items():
        pdf.drawString(70, y, f"{k}: {v}")
        y -= 25


def add_image_page(pdf, image_path, title):
    width, height = landscape(A4)
    pdf.showPage()

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(40, height - 40, title)

    img = ImageReader(image_path)

    img_width = width - 80
    img_height = height - 100
    pdf.drawImage(img, 40, 40, width=img_width, height=img_height, preserveAspectRatio=True, mask='auto')


def generate_analysis_pdf(df, figures, label_col="label", normal_label="normal"):

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    # TITLE
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(50, height - 80, "AI DFIR Analysis Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 120,
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # STATS
    total = len(df)
    attacks = (df[label_col] != normal_label).sum() if label_col in df.columns else 0
    normal = total - attacks

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 180, "Summary Statistics")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(70, height - 220, f"Total Records: {total}")
    pdf.drawString(70, height - 250, f"Attack Records: {attacks}")
    pdf.drawString(70, height - 280, f"Normal Records: {normal}")

    # SAFE GRAPH SECTION (TEXT ONLY FOR NOW)
    import matplotlib.pyplot as plt

    with tempfile.TemporaryDirectory() as temp_dir:
     for i, (title, fig) in enumerate(figures, start=1):

        pdf.showPage()

        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(50, height - 50, f"{i}. {title}")

        img_path = os.path.join(temp_dir, f"fig_{i}.png")

        try:
            # ✅ Convert plotly → matplotlib-style image
            fig.write_image(img_path)  # works now if kaleido installed

        except:
            # 🔥 FALLBACK: draw simple matplotlib chart instead
            plt.figure()
            plt.text(0.5, 0.5, title, ha='center', va='center')
            plt.savefig(img_path)
            plt.close()

        # insert image
        if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
            img = ImageReader(img_path)
            pdf.drawImage(
                img,
                50, 80,
                width=width - 100,
                height=height - 150,
                preserveAspectRatio=True
            )

    pdf.save()
    buffer.seek(0)

    return buffer