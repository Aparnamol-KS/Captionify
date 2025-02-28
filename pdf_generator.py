from fpdf import FPDF
import os
from datetime import datetime

class StylishPDF(FPDF):
    def header(self):
        """Custom header with a grey Courier title (left-aligned) and date (right-aligned)."""
        self.set_font("Courier", "B", 20)
        self.set_text_color(100, 100, 100)  # Grey Heading
        
        # Left-aligned heading
        self.cell(100, 10, "LECTURE TRANSCRIPTION", ln=False, align="L")
        
        # Right-aligned date
        self.set_font("Courier", "", 12)  # Regular style for the date
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Move cursor to the right to align the date
        self.set_x(150)
        self.cell(50, 10, current_date, ln=True, align="R")

        # Underline effect
        self.ln(5)
        self.set_draw_color(150, 150, 150)  # Grey underline
        self.set_line_width(0.8)
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        """Custom footer with page numbers."""
        self.set_y(-15)
        self.set_font("Courier", "I", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def generate_pdf(transcription_text, filename="transcription.pdf"):
    """Generates a well-styled PDF with formatted text."""
    if not transcription_text.strip():
        print("No content to generate PDF.")
        return None

    pdf = StylishPDF()
    
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Use Times New Roman font for content
    pdf.set_font("Times", size=12)
    pdf.set_text_color(30, 30, 30)
    
    # Justified text
    pdf.multi_cell(0, 8, transcription_text, align="J")
    
    pdf_path = os.path.join(os.getcwd(), filename)
    pdf.output(pdf_path, "F")
    
    print(f"📄 PDF saved as: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    sample_text = """World War or the Second World War (1 September 1939 to 2 September 1945) was a global conflict between two coalitions: the Allies and the Axis powers. Nearly all of the world's countries participated, with many nations mobilising all resources in pursuit of total war. Tanks and aircraft played major roles, enabling the strategic bombing of cities and delivery of the first and only nuclear weapons ever used in war. World War II was the deadliest conflict in history, resulting in 70 to 85 million deaths, more than half of which were civilians. Millions died in genocides, including the Holocaust, and by massacres, starvation, and disease. After the Allied victory, Germany, Austria, Japan, and Korea were occupied, and German and Japanese leaders were tried for war crimes."""
    
    generate_pdf(sample_text)
