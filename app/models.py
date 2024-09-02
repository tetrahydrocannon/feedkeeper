from app import db, login_manager
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    feed_url = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    author = db.Column(db.Text)
    published_at = db.Column(db.DateTime(timezone=True))
    link = db.Column(db.Text)
    keywords = db.Column(ARRAY(db.Text))
    raw_data = db.Column(JSONB)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)