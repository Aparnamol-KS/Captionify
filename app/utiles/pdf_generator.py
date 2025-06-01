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
    UPLOAD_FOLDER = os.path.join(current_app.root_path, 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    pdf.output(pdf_path, "F")
    print(f"📄 PDF saved as: {pdf_path}") 
    return pdf_path  











if __name__ == "__main__":
    sample_text = """World War or the Second World War (1 September 1939 to 2 September 1945) was a global conflict 
    between two coalitions: the Allies and the Axis powers. Nearly all of the world's countries participated, with many 
    nations mobilising all resources in pursuit of total war. Tanks and aircraft played major roles, enabling the 
    strategic bombing of cities and delivery of the first and only nuclear weapons ever used in war. World War II was 
    the deadliest conflict in history, resulting in 70 to 85 million deaths, more than half of which were civilians. 
    Millions died in genocides, including the Holocaust, and by massacres, starvation, and disease. After the Allied 
    victory, Germany, Austria, Japan, and Korea were occupied, and German and Japanese leaders were tried for war crimes."""
    
    generate_pdf(sample_text)  # Generate the sample PDF
