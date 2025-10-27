import os
import csv
from fpdf import FPDF
from datetime import datetime

# --------------------------
# 🧾 Save CSV report
# --------------------------
def save_csv(results, output_dir="uploads/outputs"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(output_dir, f"resume_rank_report_{timestamp}.csv")

    with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Rank", "Resume Name", "Score", "Match %", "Top Skills", "Summary"])
        for i, row in enumerate(results, start=1):
            writer.writerow([
                i,
                row.get("filename", ""),
                round(row.get("score", 0), 3),
                f"{row.get('match', 0)}%",
                ", ".join(row.get("skills", [])),
                row.get("summary", "")
            ])

    return csv_path


# --------------------------
# 🧾 Generate PDF report
# --------------------------
def save_pdf(results, output_dir="uploads/outputs"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = os.path.join(output_dir, f"resume_rank_report_{timestamp}.pdf")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 10, "AI Resume Ranker Report", ln=True, align="C")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(8)

    for i, row in enumerate(results, start=1):
        pdf.set_font("Helvetica", "B", size=11)
        pdf.cell(0, 8, f"{i}. {row.get('filename', 'Unknown')}", ln=True)
        pdf.set_font("Helvetica", size=10)

        # Prepare safe text (avoid unicode errors)
        score_text = f"Score: {round(row.get('score', 0), 3)} ({row.get('match', 0)}%)"
        summary_text = row.get("summary", "")
        skills_text = ", ".join(row.get("skills", []))

        # Replace non-latin characters safely
        score_text = score_text.encode("latin-1", "replace").decode("latin-1")
        summary_text = summary_text.encode("latin-1", "replace").decode("latin-1")
        skills_text = skills_text.encode("latin-1", "replace").decode("latin-1")

        pdf.cell(0, 6, f"{score_text}", ln=True)
        pdf.multi_cell(0, 6, f"Top Skills: {skills_text}")
        pdf.multi_cell(0, 6, f"Summary: {summary_text}")
        pdf.ln(5)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

    pdf.output(pdf_path)
    return pdf_path
