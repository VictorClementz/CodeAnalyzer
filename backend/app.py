from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate, upgrade
from models import db
from routes.analyze import analyze_bp
from routes.auth import auth_bp 
from routes.projects import projects_bp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": [
        "http://localhost:5173",
        "https://codeanalyzer-f1xp.onrender.com"
    ]}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    expose_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)


#Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///codeanalyzer.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

db.init_app(app)
migrate = Migrate(app, db)

if not app.config.get('TESTING'):
    with app.app_context():
        try:
            upgrade()
        except Exception as e:
            print("Migration failed:", e)

app.register_blueprint(analyze_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(projects_bp)

@app.route('/')
def health_check():
    return {'status': 'running', 'message': 'Code Analyzer API'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', debug=False, port=port)