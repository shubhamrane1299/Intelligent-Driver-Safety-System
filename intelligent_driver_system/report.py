from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def export_pdf():

    pdf = SimpleDocTemplate(
        "driver_report.pdf"
    )

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "Driver Safety Report",
            styles['Title']
        )
    )

    conn = sqlite3.connect("data/users.db")

    cur = conn.cursor()

    cur.execute("""
    SELECT username,state,time
    FROM logs
    ORDER BY id DESC
    LIMIT 100
    """)

    rows = cur.fetchall()

    for row in rows:

        content.append(
            Paragraph(
                f"{row[0]} | {row[1]} | {row[2]}",
                styles['Normal']
            )
        )

    pdf.build(content)

    conn.close()

    print("PDF SAVED")