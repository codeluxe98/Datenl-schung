from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devsecret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql://user:password@db/app')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('GMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('GMAIL_PASS')

mail = Mail(app)
db = SQLAlchemy(app)


# Ensure tables are created when the application starts
with app.app_context():
    db.create_all()


login_manager = LoginManager(app)
login_manager.login_view = 'login'

ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
fernet = Fernet(ENCRYPTION_KEY)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email_enc = db.Column(db.LargeBinary, nullable=False)
    phone_enc = db.Column(db.LargeBinary, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='Kunde')

    @property
    def email(self):
        return fernet.decrypt(self.email_enc).decode()

    @property
    def phone(self):
        return fernet.decrypt(self.phone_enc).decode()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegistrationForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=3)])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    phone = StringField('Telefon', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Registrieren')

class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Anmelden')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = generate_password_hash(form.password.data)
        user = User(username=form.username.data,
                    email_enc=fernet.encrypt(form.email.data.encode()),
                    phone_enc=fernet.encrypt(form.phone.data.encode()),
                    password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        flash('Registrierung erfolgreich. Bitte anmelden.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Ungültige Anmeldedaten')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash('Zugriff verweigert')
        return redirect(url_for('dashboard'))
    users = User.query.all()
    return render_template('admin.html', users=users)

BROKER_EMAILS = [
    'broker1@example.com',
    'broker2@example.com',
]

@app.route('/request_deletion')
@login_required
def request_deletion():
    for broker in BROKER_EMAILS:
        msg = Message('Löschungsanfrage',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[broker])
        msg.body = f"Bitte löschen Sie alle Daten zu {current_user.username}."
        mail.send(msg)
    flash('Löschungsanfragen wurden versendet.')
    return redirect(url_for('dashboard'))


def _ensure_db_ready(retries: int = 10, delay: int = 2) -> None:
    """Wait for the database connection before creating tables."""
    from sqlalchemy.exc import OperationalError
    import time

    for _ in range(retries):
        try:
            db.engine.connect()
            return
        except OperationalError:
            time.sleep(delay)
    raise RuntimeError("Datenbankverbindung konnte nicht hergestellt werden")


if __name__ == '__main__':
    _ensure_db_ready()
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
