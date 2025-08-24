from fpdf import FPDF
import os
from datetime import datetime
from flask import current_app

class StylishPDF(FPDF):
    def header(self):
        self.set_font("Courier", "B", 20)
        self.set_text_color(100, 100, 100)
        self.cell(100, 10, "LECTURE TRANSCRIPTION", ln=False, align="L")
        self.set_font("Courier", "", 12)  
        current_date = datetime.now().strftime("%B %d, %Y")
        self.set_x(150)
        self.cell(50, 10, current_date, ln=True, align="R")
        self.ln(5)
        self.set_draw_color(150, 150, 150) 
        self.set_line_width(0.8)
        self.line(10, 30, 200, 30) 
        self.ln(10) 

    def footer(self):
        self.set_y(-15)  
        self.set_font("Courier", "I", 10) 
        self.set_text_color(100, 100, 100)  
        self.cell(0, 10, f"Page {self.page_no()}", align="C") 

# def generate_pdf(transcription_text, filename="transcription.pdf"):
#     if not transcription_text.strip():
#         print("No content to generate PDF.")
#         return None
#     pdf = StylishPDF()
#     pdf.set_auto_page_break(auto=True, margin=20)  
#     pdf.alias_nb_pages()  
#     pdf.add_page() 
#     pdf.set_font("Times", size=12) 
#     pdf.set_text_color(30, 30, 30)
#     pdf.multi_cell(0, 8, transcription_text, align="J")
#     UPLOAD_FOLDER = os.path.join(current_app.root_path, 'uploads')
#     os.makedirs(UPLOAD_FOLDER, exist_ok=True)  
#     pdf_path = os.path.join(UPLOAD_FOLDER, filename)
#     pdf.output(pdf_path, "F")
#     print(f"📄 PDF saved as: {pdf_path}") 
#     return pdf_path  




def generate_pdf(transcription_text, filename="transcription.pdf"):
    if not transcription_text.strip():
        print("No content to generate PDF.")
        return None
    pdf = StylishPDF()
    pdf.set_auto_page_break(auto=True, margin=20)  
    pdf.alias_nb_pages()  
    pdf.add_page() 
    pdf.set_font("Times", size=12) 
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 8, transcription_text, align="J")

    # Handle both inside and outside Flask
    try:
        base_path = current_app.root_path
    except RuntimeError:
        base_path = os.getcwd()  # fallback for testing

    UPLOAD_FOLDER = os.path.join(base_path, 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    pdf.output(pdf_path, "F")
    print(f"📄 PDF saved as: {pdf_path}") 
    return pdf_path







if __name__ == "__main__":
    sample_text = """So today we’re going to start by revisiting the concept of quadratic equations, 
    which we’ve already seen in earlier classes. Remember, a standard quadratic equation 
    takes the form \(ax^2 + bx + c = 0\), where \(a\), \(b\), and \(c\) are real numbers and \(a \neq 0\). Now, 
    the most common method we use to solve this is the quadratic formula, which 
    is given by \(x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}\). [...]"""
    
    generate_pdf(sample_text)  # Generate the sample PDF
