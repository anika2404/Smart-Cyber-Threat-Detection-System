import io
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
)

NEON_COLORS = ["#00d4ff", "#00ff88", "#ff2d55", "#ffb800", "#7b2fff", "#ff6b35"]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="black", size=10),
    margin=dict(l=40, r=40, t=60, b=40),
)


def fig_to_image(fig, width=1200, height=650):
    fig.update_layout(width=width, height=height)
    img_bytes = fig.to_image(format="png", engine="kaleido")
    return io.BytesIO(img_bytes)


def create_analysis_pdf(df: pd.DataFrame, label_col="label", normal_label="normal"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    total = len(df)
    attacks = (df[label_col] != normal_label).sum() if label_col in df.columns else 0
    normal = total - attacks

    story.append(Paragraph("AI DFIR Tool - Analysis Report", styles["Title"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    summary_data = [
        ["Metric", "Value"],
        ["Total Records", str(total)],
        ["Attack Records", str(attacks)],
        ["Normal Records", str(normal)],
    ]

    summary_table = Table(summary_data, colWidths=[2.5 * inch, 2.5 * inch])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00d4ff")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3 * inch))

    if label_col in df.columns:
        vc = df[label_col].value_counts().reset_index()
        vc.columns = ["label", "count"]

        fig1 = px.bar(
            vc,
            x="label",
            y="count",
            color="label",
            color_discrete_sequence=NEON_COLORS,
            title="Attack Type Distribution"
        )
        fig1.update_layout(**PLOTLY_LAYOUT)
        img1 = fig_to_image(fig1)
        story.append(Paragraph("1. Attack Type Distribution", styles["Heading2"]))
        story.append(Image(img1, width=7.0 * inch, height=3.8 * inch))
        story.append(Spacer(1, 0.2 * inch))

        fig2 = px.pie(
            vc,
            names="label",
            values="count",
            hole=0.45,
            color_discrete_sequence=NEON_COLORS,
            title="Traffic Composition"
        )
        fig2.update_layout(**PLOTLY_LAYOUT)
        img2 = fig_to_image(fig2)
        story.append(Paragraph("2. Traffic Composition", styles["Heading2"]))
        story.append(Image(img2, width=7.0 * inch, height=3.8 * inch))
        story.append(PageBreak())

    if "bytes" in df.columns and label_col in df.columns:
        sample_df = df.sample(min(1500, len(df)), random_state=42)
        fig3 = px.box(
            sample_df,
            x=label_col,
            y="bytes",
            color=label_col,
            color_discrete_sequence=NEON_COLORS,
            title="Bytes Transferred per Category"
        )
        fig3.update_layout(**PLOTLY_LAYOUT)
        img3 = fig_to_image(fig3)
        story.append(Paragraph("3. Bytes Transferred per Category", styles["Heading2"]))
        story.append(Image(img3, width=7.0 * inch, height=3.8 * inch))
        story.append(Spacer(1, 0.2 * inch))

    if "dst_port" in df.columns:
        top_ports = df.groupby("dst_port").size().nlargest(10).reset_index(name="hits")
        fig4 = px.bar(
            top_ports,
            x="dst_port",
            y="hits",
            color="hits",
            color_continuous_scale=["#001a35", "#00d4ff"],
            title="Top 10 Targeted Ports"
        )
        fig4.update_layout(**PLOTLY_LAYOUT)
        img4 = fig_to_image(fig4)
        story.append(Paragraph("4. Top 10 Targeted Ports", styles["Heading2"]))
        story.append(Image(img4, width=7.0 * inch, height=3.8 * inch))
        story.append(Spacer(1, 0.2 * inch))

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols[:10]].corr()
        fig5 = go.Figure(go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale="Blues"
        ))
        fig5.update_layout(title="Feature Correlation Heatmap", **PLOTLY_LAYOUT)
        img5 = fig_to_image(fig5)
        story.append(Paragraph("5. Correlation Heatmap", styles["Heading2"]))
        story.append(Image(img5, width=7.0 * inch, height=4.2 * inch))

    doc.build(story)
    buffer.seek(0)
    return buffer