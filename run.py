from app import create_app, db

app = create_app()  # Create the Flask app

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables are created at startup
    app.run(debug=True)