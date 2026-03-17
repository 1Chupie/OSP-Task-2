from app import create_app, db

app = create_app()

# Initialise the database table
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
