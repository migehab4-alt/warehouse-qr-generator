import os
import time
import pandas as pd
import qrcode
from PIL import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

INPUT_XLSX = "Pallet_Labels.xlsx"
OUTPUT_DIR = "output_labels"
QR_DIR = os.path.join(OUTPUT_DIR, "qr_png")
PDF_PATH = os.path.join(OUTPUT_DIR, "QR_Labels_30x8cm.pdf")

LABEL_W_CM = 30
LABEL_H_CM = 8
QR_SIZE_CM = 5.8

def ensure_dirs():
    os.makedirs(QR_DIR, exist_ok=True)

def create_excel_if_missing():
    if os.path.exists(INPUT_XLSX):
        return
    df = pd.DataFrame({
        "Label_ID": [
            "JA-A1-GF-S1-P1",
            "JA-A1-GF-S1-P2"
        ]
    })
    df.to_excel(INPUT_XLSX, index=False)

def read_excel():
    df = pd.read_excel(INPUT_XLSX, dtype=str)
    df["Label_ID"] = df["Label_ID"].fillna("").str.strip()
    return df[df["Label_ID"] != ""]

def make_qr(data, path):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((1000, 1000), Image.NEAREST)
    img.save(path)

def build_pdf(df):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="center",
        alignment=TA_CENTER,
        fontSize=22
    ))

    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=(LABEL_W_CM*cm, LABEL_H_CM*cm),
        leftMargin=1*cm,
        rightMargin=1*cm,
        topMargin=0.5*cm,
        bottomMargin=0.5*cm
    )

    story = []
    for _, row in df.iterrows():
        label = row["Label_ID"]
        qr_path = os.path.join(QR_DIR, f"{label}.png")
        make_qr(label, qr_path)

        story.append(Paragraph(label, styles["center"]))
        story.append(Spacer(1, 0.2*cm))
        img = RLImage(qr_path, QR_SIZE_CM*cm, QR_SIZE_CM*cm)
        img.hAlign = "CENTER"
        story.append(img)
        story.append(PageBreak())

    doc.build(story)

def main():
    ensure_dirs()
    create_excel_if_missing()
    df = read_excel()
    build_pdf(df)
    print("✅ DONE: PDF + QR generated")

if __name__ == "__main__":
    main()
