# from app import db
# from flask_login import current_user
# from app.models import PDFUpload
# from pdf_generator import generate_pdf

# def save_pdf_to_db(transcription_text, filename="transcription.pdf"):
#     """Saves a generated PDF into the database."""
#     pdf_path = generate_pdf(transcription_text, filename)
#     if not pdf_path:
#         return None  # No content to save

#     with open(pdf_path, "rb") as file:
#         pdf_data = file.read()  # Read PDF as binary data

#     new_pdf = PDFUpload(
#         filename=filename,
#         pdf_data=pdf_data,
#         user_id=current_user.id
#     )
    
#     db.session.add(new_pdf)
#     db.session.commit()
    
#     print(f"📄 PDF '{filename}' saved in the database for user {current_user.username}.")
#     return new_pdf.id  # Return the database ID for reference
