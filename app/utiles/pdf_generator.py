from fpdf import FPDF
import os
from datetime import datetime
from flask import current_app

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

        # Underline effect for separation
        self.ln(5)
        self.set_draw_color(150, 150, 150)  # Grey underline
        self.set_line_width(0.8)
        self.line(10, 30, 200, 30)  # Draws a horizontal line
        self.ln(10)  # Adds space after the header

    def footer(self):
        """Custom footer with page numbers."""
        self.set_y(-15)  # Position the footer 15 units from the bottom
        self.set_font("Courier", "I", 10)  # Italic font style
        self.set_text_color(100, 100, 100)  # Grey text
        self.cell(0, 10, f"Page {self.page_no()}", align="C")  # Display the page number


def generate_pdf(transcription_text, filename="transcription.pdf"):
    """
    Generates a well-styled PDF with formatted text.

    Args:
        transcription_text (str): The text content to be added to the PDF.
        filename (str, optional): The name of the output PDF file. Defaults to "transcription.pdf".

    Returns:
        str: The file path of the saved PDF.
    """
    
    # Check if the provided text is empty
    if not transcription_text.strip():
        print("No content to generate PDF.")
        return None

    # Create an instance of the custom PDF class
    pdf = StylishPDF()
    
    pdf.set_auto_page_break(auto=True, margin=20)  # Enables automatic page breaks
    pdf.alias_nb_pages()  # Allows displaying total pages
    pdf.add_page()  # Adds a new page
    
    # Set font and text color for the main content
    pdf.set_font("Times", size=12)  # Use Times New Roman for the text
    pdf.set_text_color(30, 30, 30)  # Dark text for better readability
    
    # Add the transcription text with justification
    pdf.multi_cell(0, 8, transcription_text, align="J")  # Justified text with 8pt line spacing
    
    # Define the upload folder path
    UPLOAD_FOLDER = os.path.join(current_app.root_path, 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create directory if it does not exist
    
    # Construct the full file path for the PDF
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Save the generated PDF file
    pdf.output(pdf_path, "F")
    
    print(f"📄 PDF saved as: {pdf_path}")  # Output file path for reference
    return pdf_path  # Return the path of the saved PDF file


# Sample execution for testing purposes
if __name__ == "__main__":
    sample_text = """World War or the Second World War (1 September 1939 to 2 September 1945) was a global conflict 
    between two coalitions: the Allies and the Axis powers. Nearly all of the world's countries participated, with many 
    nations mobilising all resources in pursuit of total war. Tanks and aircraft played major roles, enabling the 
    strategic bombing of cities and delivery of the first and only nuclear weapons ever used in war. World War II was 
    the deadliest conflict in history, resulting in 70 to 85 million deaths, more than half of which were civilians. 
    Millions died in genocides, including the Holocaust, and by massacres, starvation, and disease. After the Allied 
    victory, Germany, Austria, Japan, and Korea were occupied, and German and Japanese leaders were tried for war crimes."""
    
    generate_pdf(sample_text)  # Generate the sample PDF
