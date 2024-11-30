from fpdf import FPDF
import csv


def save_to_excel(data):
    with open("schedule.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)


def save_to_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for row in data:
        pdf.cell(200, 10, txt=" | ".join(row), ln=True)

    pdf.output("schedule.pdf")
