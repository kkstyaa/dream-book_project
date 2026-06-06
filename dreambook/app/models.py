from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    avatar_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    #связи
    dreams = db.relationship('Dream', backref='author', lazy=True)
    statistics = db.relationship('Statistic', backref='user', lazy=True)
    emotion_stats = db.relationship('EmotionStat', backref='user', lazy=True)
    symbol_stats = db.relationship('SymbolStat', backref='user', lazy=True)
    generation_requests = db.relationship('GenerationRequest', backref='user', lazy=True)
    user_images = db.relationship('UserImage', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.user_id)


class Dream(db.Model):
    __tablename__ = 'dreams'

    dream_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    dream_date = db.Column(db.Date, nullable=False)
    mood = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # связи
    dream_symbols = db.relationship('DreamSymbol', backref='dream', lazy=True)
    generated_image = db.relationship('GeneratedImage', backref='dream', uselist=False)
    user_image = db.relationship('UserImage', backref='dream', uselist=False)

    def __repr__(self):
        return f'<Dream {self.title}>'

class Symbol(db.Model):
    __tablename__ = 'symbols'

    symbol_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    #связи
    dream_symbols = db.relationship('DreamSymbol', backref='symbol', lazy=True)
    symbol_stats = db.relationship('SymbolStat', backref='symbol', lazy=True)


class DreamSymbol(db.Model):
    __tablename__ = 'dream_symbols'

    dream_id = db.Column(db.Integer, db.ForeignKey('dreams.dream_id'), primary_key=True)
    symbol_id = db.Column(db.Integer, db.ForeignKey('symbols.symbol_id'), primary_key=True)


class Statistic(db.Model):
    __tablename__ = 'statistics'

    statistic_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    period = db.Column(db.String(50), nullable=False)
    data = db.Column(db.JSON, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class EmotionStat(db.Model):
    __tablename__ = 'emotion_stats'

    emotion_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    period = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    avg_mood = db.Column(db.Float, nullable=True)
    dream_count = db.Column(db.Integer, default=0)


class SymbolStat(db.Model):
    __tablename__ = 'symbol_stats'

    sym_stats_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    symbol_id = db.Column(db.Integer, db.ForeignKey('symbols.symbol_id'), nullable=False)
    period = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    frequency = db.Column(db.Integer, default=0)


class GenerationRequest(db.Model):
    __tablename__ = 'generation_requests'

    gen_req_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.now)

    generated_images = db.relationship('GeneratedImage', backref='request', lazy=True)


class GeneratedImage(db.Model):
    __tablename__ = 'generated_images'

    gen_img_id = db.Column(db.Integer, primary_key=True)
    dream_id = db.Column(db.Integer, db.ForeignKey('dreams.dream_id'), nullable=False, unique=True)
    gen_req_id = db.Column(db.Integer, db.ForeignKey('generation_requests.gen_req_id'))
    image_url = db.Column(db.String(500), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.now)


class UserImage(db.Model):
    __tablename__ = 'user_images'

    image_id = db.Column(db.Integer, primary_key=True)
    dream_id = db.Column(db.Integer, db.ForeignKey('dreams.dream_id'), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.now)