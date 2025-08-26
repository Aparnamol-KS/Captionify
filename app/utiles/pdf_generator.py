import re
import io
import datetime
import matplotlib
matplotlib.use("Agg")
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
from flask import current_app
import os

def render_formula(formula, fontsize=14, dpi=200):
    """Render LaTeX formula into an image (PNG in memory)."""
    fig, ax = plt.subplots(figsize=(0.01, 0.01))
    ax.axis("off")
    ax.text(0.5, 0.5, f"${formula}$", fontsize=fontsize, ha="center", va="center")
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=dpi, transparent=True, pad_inches=0.05)
    plt.close(fig)
    buf.seek(0)
    return ImageReader(buf), buf

def safe_render_formula(formula, fontsize=14, dpi=200):
    try:
        return render_formula(formula, fontsize, dpi)
    except Exception as e:
        print(f"⚠️ LaTeX render failed: {formula} | Error: {e}")
        # fallback: return plain text instead of image
        buf = io.BytesIO()
        fig, ax = plt.subplots(figsize=(2, 0.5))
        ax.axis("off")
        ax.text(0.5, 0.5, formula, fontsize=fontsize, ha="center", va="center")
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=dpi, transparent=True, pad_inches=0.05)
        plt.close(fig)
        buf.seek(0)
        return ImageReader(buf), buf


def add_header(c, width, height, title="Lecture Notes"):
    """Draw fixed header with title and date."""
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 40, title)

    today = datetime.datetime.now().strftime("%d %B %Y")
    c.setFont("Helvetica", 10)
    c.drawRightString(width - inch, height - 55, f"Generated on: {today}")

    # Line under header
    c.setStrokeColorRGB(0.3, 0.3, 0.3)
    c.line(inch, height - 65, width - inch, height - 65)

def add_footer(c, width):
    """Add footer with page numbers."""
    c.setFont("Helvetica", 9)
    page_num = c.getPageNumber()
    c.drawCentredString(width / 2, 25, f"Page {page_num}")

def generate_pdf(text, filename="lecture_notes.pdf"):
    # --- Step 1: Create PDF ---
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    add_header(c, width, height)

    x_margin, y_margin = inch, height - 90
    line_height = 20
    cursor_y = y_margin

    # Split transcript by LaTeX math \( ... \)
    parts = re.split(r"(\\\(.*?\\\))", text)

    for part in parts:
        if not part.strip():
            continue

        if part.startswith("\\(") and part.endswith("\\)"):
            # Block formula
            formula = part[2:-2].strip()
            img, buf = safe_render_formula(formula, fontsize=14)
            iw, ih = img.getSize()
            scale = 0.5
            iw *= scale
            ih *= scale

            if iw > width - 2*inch:
                factor = (width - 2*inch) / iw
                iw *= factor
                ih *= factor

            x_center = (width - iw) / 2
            c.drawImage(img, x_center, cursor_y - ih, width=iw, height=ih, mask="auto")
            cursor_y -= ih + line_height
        else:
            # Paragraph text with word wrapping
            words = part.split()
            x = x_margin
            for word in words:
                word_width = c.stringWidth(word + " ", "Helvetica", 12)
                if x + word_width > width - inch:
                    x = x_margin
                    cursor_y -= line_height
                c.setFont("Helvetica", 12)
                c.drawString(x, cursor_y, word + " ")
                x += word_width
            cursor_y -= line_height * 1.2  # more space between paragraphs

        # Page break
        if cursor_y < inch:
            add_footer(c, width)
            c.showPage()
            add_header(c, width, height)
            cursor_y = height - 90

    add_footer(c, width)
    c.save()

    # --- Step 2: Move into uploads folder ---
    try:
        base_path = current_app.root_path
    except RuntimeError:
        base_path = os.getcwd()

    print(f"✅ PDF created: {filename}")
    UPLOAD_FOLDER = os.path.join(base_path, 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    os.replace(filename, pdf_path)   # move file from current dir to uploads

    print(f"📄 PDF saved as: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    sample_text = r"""
In today's lecture, we will explore some fundamental concepts in mathematics 
that are frequently used in physics and computer science. 

Let us begin with the quadratic equation, which is generally written as 
\(a x^2 + b x + c = 0\). The solutions of this equation are given by the quadratic 
formula: \(x = \frac{-b \pm \sqrt{b^2 - 4 a c}}{2 a}\). 

Now, moving to coordinate geometry, the distance between two points 
\((x_1, y_1)\) and \((x_2, y_2)\) in the Cartesian plane is calculated using 
the distance formula \(\sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}\). Another related 
concept is the slope of a line, defined as \(m = \frac{y_2 - y_1}{x_2 - x_1}\).  

In trigonometry, we often deal with identities such as 
\(\sin^2 \theta + \cos^2 \theta = 1\). These identities are very useful when 
simplifying expressions. For example, the double-angle identity is written as 
\(\cos(2\theta) = \cos^2 \theta - \sin^2 \theta\). 

In calculus, the derivative of a function describes its rate of change. For instance, 
the derivative of \(f(x) = x^2\) is given by \(f'(x) = 2x\). Similarly, the integral of a 
function gives us the area under its curve. For example, 
\(\int x^2 dx = \frac{x^3}{3} + C\).  

Finally, let us recall Euler's famous identity, which beautifully links five of the 
most important numbers in mathematics: \(e^{i \pi} + 1 = 0\). This equation is 
often considered the most elegant formula ever discovered. 
"""

    generate_pdf(sample_text)
