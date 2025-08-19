import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from db_agendamento import get_database_url

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = get_database_url()
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

@login_manager.user_loader
def load_user(user_id):
    from modelos import Usuario
    return Usuario.query.get(int(user_id))

with app.app_context():
    # Import models to ensure tables are created
    import modelos
    
    # Create all tables
    db.create_all()
    
    # Create default master user and company settings
    from modelos import Usuario, Cargo, ConfiguracaoEmpresa
    from werkzeug.security import generate_password_hash
    
    # Create default master user if it doesn't exist
    master_user = Usuario.query.filter_by(username='master').first()
    if not master_user:
        master_user = Usuario(
            username='master',
            email='master@jtsistemas.com',
            password_hash=generate_password_hash('master123'),
            tipo_usuario='master',
            nome='Administrador Master',
            ativo=True
        )
        db.session.add(master_user)
        db.session.commit()
        logging.info("Default master user created: master/master123")
    
    # Create default company configuration
    config = ConfiguracaoEmpresa.query.first()
    if not config:
        config = ConfiguracaoEmpresa(
            nome_empresa='JT Sistemas',
            logo_path=None,
            whatsapp_token='',
            whatsapp_phone_id='',
            whatsapp_webhook_verify_token=''
        )
        db.session.add(config)
    
    # Create default positions if they don't exist
    default_positions = [
        {'nome': 'Gerente', 'descricao': 'Gerente geral'},
        {'nome': 'Atendente', 'descricao': 'Atendimento ao cliente'},
        {'nome': 'Especialista', 'descricao': 'Especialista técnico'}
    ]
    
    for pos_data in default_positions:
        cargo = Cargo.query.filter_by(nome=pos_data['nome']).first()
        if not cargo:
            cargo = Cargo(
                nome=pos_data['nome'],
                descricao=pos_data['descricao']
            )
            db.session.add(cargo)
    
    db.session.commit()

# Import routes after app creation
import rotas
