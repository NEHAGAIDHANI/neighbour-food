from app import app
from models import db

def rebuild_db():
    with app.app_context():
       with app.app_context():
        db.drop_all()  # WARNING: deletes old data
        db.create_all() # creates fresh tables including 'role'

if __name__ == "__main__":
    rebuild_db()