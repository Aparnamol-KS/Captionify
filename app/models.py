from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'  # Explicitly define the table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Added admin field

    # Relationships
    captions = db.relationship('Caption', backref='user', lazy=True, cascade="all, delete")
    uploads = db.relationship('PDFUpload', backref='user', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', 'Admin: {self.is_admin}')"

class Caption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Caption('{self.text[:20]}...')"

class PDFUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"PDFUpload('{self.filename}')"

class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption_id = db.Column(db.Integer, db.ForeignKey('caption.id'), nullable=False)
    summary_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Summary('{self.summary_text[:30]}...')"
