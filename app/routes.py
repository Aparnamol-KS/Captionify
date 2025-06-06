from flask import Blueprint, render_template,send_file, flash, redirect, current_app, url_for, send_from_directory, request
from app.forms import RegistrationForm, LoginForm
from app.models import PDFUpload, User, Caption, Summary
from app import db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from app.utiles.transcriber import SpeechTranscriber
from app.utiles.pdf_generator import generate_pdf
from app.utiles.summarizer import TextSummarizer 
from io import BytesIO
from datetime import datetime
from difflib import SequenceMatcher
import os

from app import socketio 
main = Blueprint('main', __name__)  # Define Blueprint


# Initialize global variables
transcriber = None
summarizer = None  # Lazy loading


def initialize_services():
    global transcriber
    if transcriber is None:
        transcriber = SpeechTranscriber(socketio)
initialize_services()

# Home page
@main.route('/')
def home():
    return render_template("home.html")

@main.route('/live_transcription/start_recording', methods=['GET'])
def start_recording():
    if transcriber:
        transcriber.start_recording()
        return jsonify({"status": "Recording started"})
    else:
        return jsonify({"status": "Error", "message": "Transcriber not initialized"}), 500
    

@main.route('/live_transcription/stop_recording', methods=['GET'])
@login_required
def stop_recording():
    """Stops recording and stores the transcription in the database."""
    if transcriber:
        full_text = transcriber.stop_recording()

        if not full_text.strip():
            flash("No transcription recorded!", "warning")
            return jsonify({"status": "No transcription recorded."})

        # Fetch all captions for the user
        user_captions = Caption.query.filter_by(user_id=current_user.id).all()

        # Find a caption with similar text (similarity > 90%)
        existing_caption = None
        for caption in user_captions:
            if text_similarity(full_text, caption.text) > 0.9:
                existing_caption = caption
                break

        if existing_caption:
            # Update the existing transcription
            existing_caption.text = full_text
            existing_caption.timestamp = datetime.utcnow()  # Update timestamp
            
        else:
            # Create a new transcription entry
            new_caption = Caption(
                text=full_text,
                user_id=current_user.id,
                timestamp=datetime.utcnow()
            )
            db.session.add(new_caption)

        db.session.commit()  # Commit changes to database

        return jsonify({
            "status": "Recording stopped",
            "message": "Transcription saved!",
            "transcription": full_text
        })

    else:
        flash("Error: Transcriber not initialized!", "danger")
        return jsonify({
            "status": "Error",
            "message": "Transcriber not initialized"
        }), 500



@main.route('/edit_caption/<int:caption_id>', methods=['POST'])
@login_required
def edit_caption(caption_id):
    """Updates the transcription text in the database or creates a new one if not found."""
    new_text = request.form.get("edited_text")

    if not new_text or not new_text.strip():
        flash("Edited text cannot be empty!", "warning")
        return redirect(url_for("main.live_transcription"))  # Adjust as needed

    # Try to fetch the caption from the database
    caption = Caption.query.get(caption_id)

    if caption:
        # Ensure only the owner can edit
        if caption.user_id != current_user.id:
            flash("Unauthorized action!", "danger")
            return redirect(url_for("main.live_transcription"))

        # Update existing caption
        caption.text = new_text
        caption.timestamp = datetime.utcnow()  # Update timestamp
        flash("Transcription updated successfully!", "success")

    else:
        # If caption does not exist, create a new one
        new_caption = Caption(
            text=new_text,
            user_id=current_user.id,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_caption)
        flash("New transcription saved!", "success")

    db.session.commit()  # Save changes

    return redirect(url_for("main.live_transcription"))  # Adjust as needed

@main.route('/add_caption', methods=['POST'])
@login_required
def add_caption():
    """Creates a new caption if none exists."""
    new_text = request.form.get("edited_text")

    if not new_text or not new_text.strip():
        flash("Caption text cannot be empty!", "warning")
        return redirect(url_for("main.live_transcription"))

    # Create and store new caption
    new_caption = Caption(text=new_text, user_id=current_user.id)
    db.session.add(new_caption)
    db.session.commit()

    flash("Caption saved successfully!", "success")
    return redirect(url_for("main.live_transcription"))


@main.route('/live_transcription/make_pdf', methods=['POST'])
def save_pdf():
    """Generate a PDF from transcription text and store it in the database."""
    transcription_text = request.form.get("transcription_text")

    if not transcription_text or not transcription_text.strip():
        flash("No transcription available to save.", "warning")
        return redirect(url_for("main.live_transcription"))  # Redirect back with error

    # Generate the PDF using existing function
    timestamp = datetime.now().strftime("%Y%m%d")
    pdf_filename = f"{timestamp}_transcription.pdf"

    pdf_path = generate_pdf(transcription_text, pdf_filename)  # Call your existing function

    if pdf_path and os.path.exists(pdf_path):
        # Read PDF as binary data
        with open(pdf_path, "rb") as pdf_file:
            pdf_binary = pdf_file.read()

        # Store the PDF in the database
        new_pdf = PDFUpload(
            filename=pdf_filename,
            pdf_data=pdf_binary,
            user_id=current_user.id
        )
        db.session.add(new_pdf)
        db.session.commit()

        flash("PDF successfully generated and stored in database!", "success")

        # Optional: Serve the stored PDF for download
        return send_file(
            BytesIO(pdf_binary),    
            as_attachment=True,
            download_name=pdf_filename,
            mimetype="application/pdf"
        )

    flash("Error generating PDF.", "danger")
    return redirect(url_for("main.live_transcription"))

@main.route('/summary/make_pdf', methods=['POST'])
def save_summary_pdf():
    """Generate a PDF from summarized transcription text and store it in the database."""
    summary_text = request.form.get("summary_text")

    if not summary_text or not summary_text.strip():
        flash("No Summary available to save.", "warning")
        return redirect(url_for("main.summary"))  # Redirect back with error

    # Generate a filename that indicates it's a summary
    timestamp = datetime.now().strftime("%Y%m%d")
    pdf_filename = f"{timestamp}_summary.pdf"

    # Generate PDF using the existing function
    pdf_path = generate_pdf(summary_text, pdf_filename)

    if pdf_path and os.path.exists(pdf_path):
        # Read PDF as binary data
        with open(pdf_path, "rb") as pdf_file:
            pdf_binary = pdf_file.read()

        # Store the summarized PDF in the database
        new_pdf = PDFUpload(
            filename=pdf_filename,
            pdf_data=pdf_binary,
            user_id=current_user.id
        )
        db.session.add(new_pdf)
        db.session.commit()

        flash("Summarized PDF successfully generated and stored in database!", "success")

        # Optional: Serve the stored PDF for download
        return send_file(
            BytesIO(pdf_binary),
            as_attachment=True,
            download_name=pdf_filename,
            mimetype="application/pdf"
        )

    flash("Error generating summarized PDF.", "danger")
    return redirect(url_for("main.summary"))

@main.route('/live_transcription')
@login_required
def live_transcription():
    """Renders the live transcription page and fetches the latest caption if available."""
    caption = Caption.query.filter_by(user_id=current_user.id).order_by(Caption.timestamp.desc()).first()  # Get the latest caption

    return render_template("live_transcription.html", caption=caption)  

@main.route('/summary', methods=['POST', 'GET'])
@login_required

def summary():
    if request.method == 'POST':
        transcript = request.form.get("transcript", "").strip()

        global summarizer  
        if summarizer is None:
            summarizer = TextSummarizer()

        if not transcript:
            flash("No text provided for summarization.", "warning")
            return redirect(url_for("main.summary"))

        # Perform summarization
        summary_text = summarizer.summarize(transcript)  
        print("✅ Summary generated successfully!")  

        # Fetch all captions for the user
        user_captions = Caption.query.filter_by(user_id=current_user.id).all()

        # Find a caption with similar text (similarity > 90%)
        existing_caption = None
        for caption in user_captions:
            if text_similarity(transcript, caption.text) > 0.9:
                existing_caption = caption
                break

        if not existing_caption:
            flash("No matching caption found! Creating a new one...", "info")
            existing_caption = Caption(text=transcript, user_id=current_user.id)
            db.session.add(existing_caption)
            db.session.commit()

        # Save summary to the database
        new_summary = Summary(caption_id=existing_caption.id, summary_text=summary_text)
        db.session.add(new_summary)
        db.session.commit()

        flash("Summary saved successfully!", "success")
        return render_template("summary.html", summary=summary_text)

    return render_template("summary.html", summary="No summary available.")
def text_similarity(text1, text2):
    """Returns a similarity ratio between two texts."""
    return SequenceMatcher(None, text1, text2).ratio()

# Registration page
@main.route('/registration', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        is_admin = True if form.username.data == "Aparna" else False

        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully!', 'success')
        return redirect(url_for('main.login'))  
    
    return render_template("register.html", title='Register', form=form)


# Login page
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template("login.html", title='Login', form=form)


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
       
       # Update current user's details instead of creating a new user
        current_user.username = name
        current_user.email = email

        # Commit changes to the database
        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))  # Reload the profile page

    return render_template("profile.html", user=current_user) 

# Logout route
@main.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

# Index page
@main.route('/index')
def index():
    return render_template("index.html")

@main.route('/pdfs')
@login_required
def pdfs():
    pdf_files = PDFUpload.query.filter_by(user_id=current_user.id).all()  
    return render_template("pdfs.html", pdfs=pdf_files)

@main.route('/summary_list')
@login_required
def summary_list():
    summaries = db.session.query(Summary, Caption.timestamp).join(Caption).filter(Caption.user_id == current_user.id).order_by(Summary.id.desc()).all()
    return render_template("summary_list.html", summaries=summaries)

@main.route('/summary_list/<int:summary_id>')
def view_summary(summary_id):
    summary = Summary.query.get_or_404(summary_id)
    caption = Caption.query.get_or_404(summary.caption_id)  # Get corresponding caption
    return render_template('summary_detail.html', summary=summary, caption=caption)



@main.route('/view_pdf/<int:pdf_id>')
@login_required
def view_pdf(pdf_id):
    pdf = PDFUpload.query.get_or_404(pdf_id)  # Fetch the PDF from the database
    
    # Ensure the correct directory where PDFs are stored
    pdf_directory = os.path.join(current_app.root_path, 'uploads')  
    
    # Check if file exists
    if not os.path.exists(os.path.join(pdf_directory, pdf.filename)):
        return "File not found", 404
    
    # Serve the PDF file
    return send_from_directory(pdf_directory, pdf.filename)


 


# Error Handlers
@main.app_errorhandler(404)  
def page_not_found(e):
    return render_template("404.html"), 404

@main.app_errorhandler(500)  
def internal_server_error(e):
    return render_template("500.html"), 500


