from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        UPLOAD_FOLDER=os.path.join(os.path.dirname(__file__), 'static/qrcodes'),
        DATABASE_URL=os.environ.get('DATABASE_URL'),
        BASE_URL=os.environ.get('BASE_URL')
    )
    
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app