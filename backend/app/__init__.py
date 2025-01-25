from flask import Flask
from flask_cors import CORS
from .config import Config
from .database import db
from .models import ExperimentType, ExperimentResult
from .routes import main_bp 
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)  
    migrate = Migrate(app, db) 
    with app.app_context():
        db.create_all()

    app.register_blueprint(main_bp) 

    return app
