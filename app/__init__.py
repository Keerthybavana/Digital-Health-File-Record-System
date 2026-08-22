import os
from flask import Flask
from flask_login import LoginManager
from app.models import db, User

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Base configuration
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Configure directories
    upload_folder = os.path.join(base_dir, 'uploads')
    models_folder = os.path.join(base_dir, 'models_ml')
    qrcodes_folder = os.path.join(base_dir, 'app', 'static', 'qrcodes')
    
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(models_folder, exist_ok=True)
    os.makedirs(qrcodes_folder, exist_ok=True)
    
    app.config['SECRET_KEY'] = 'dev-health-secret-key-12345'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'digital_health.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['MODELS_FOLDER'] = models_folder
    app.config['QRCODES_FOLDER'] = qrcodes_folder
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Automatically update/regenerate all QR codes using the local network IP on startup
        try:
            import socket
            import qrcode
            from app.models import Document
            
            def get_local_ip():
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    s.connect(('10.254.254.254', 1))
                    ip = s.getsockname()[0]
                except Exception:
                    ip = '127.0.0.1'
                finally:
                    s.close()
                return ip
                
            base_url = os.environ.get('BASE_URL')
            if not base_url:
                local_ip = get_local_ip()
                base_url = f"http://{local_ip}:5000"
            
            docs = Document.query.all()
            if docs:
                print(f"\n--- [STARTUP] Regenerating {len(docs)} QR codes with Base URL: {base_url} ---")
                for doc in docs:
                    details_url = f"{base_url.rstrip('/')}/share/{doc.id}"
                    qr = qrcode.QRCode(version=1, box_size=5, border=2)
                    qr.add_data(details_url)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    
                    qr_filename = f"qr_{doc.id}.png"
                    qr_file_path = os.path.join(app.config['QRCODES_FOLDER'], qr_filename)
                    qr_img.save(qr_file_path)
                    
                    doc.qr_path = f"qrcodes/{qr_filename}"
                db.session.commit()
                print("--- [STARTUP] QR codes regenerated successfully! ---\n")
        except Exception as e:
            print(f"Failed to regenerate QR codes on startup: {e}")
        
    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
