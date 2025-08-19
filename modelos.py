from aplicacao import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    tipo_usuario = db.Column(db.String(20), default='restrito')  # master, restrito
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Permissões específicas para usuários restritos
    pode_cadastrar_cliente = db.Column(db.Boolean, default=False)
    pode_cadastrar_funcionario = db.Column(db.Boolean, default=False)
    pode_cadastrar_cargo = db.Column(db.Boolean, default=False)
    pode_agendar = db.Column(db.Boolean, default=True)
    pode_ver_agendamentos = db.Column(db.Boolean, default=True)
    pode_ver_relatorios = db.Column(db.Boolean, default=False)
    
    # Relationships
    perfil_funcionario = db.relationship('Funcionario', backref='usuario', uselist=False)
    agendamentos_cliente = db.relationship('Agendamento', foreign_keys='Agendamento.cliente_id', backref='cliente')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_master(self):
        return self.tipo_usuario == 'master'

    def is_funcionario(self):
        return self.perfil_funcionario is not None

    def __repr__(self):
        return f'<Usuario {self.username}>'

class Cargo(db.Model):
    __tablename__ = 'cargos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    funcionarios = db.relationship('Funcionario', backref='cargo')

    def __repr__(self):
        return f'<Cargo {self.nome}>'
    
class Servico(db.Model):
    __tablename__ = 'servicos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Float, nullable=False)
    duracao_minutos = db.Column(db.Integer, nullable=False)
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Servico {self.nome}>'    

class Funcionario(db.Model):
    __tablename__ = 'funcionarios'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    cargo_id = db.Column(db.Integer, db.ForeignKey('cargos.id'), nullable=False)
    data_contratacao = db.Column(db.Date, default=datetime.utcnow().date)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    agendamentos = db.relationship('Agendamento', foreign_keys='Agendamento.funcionario_id', backref='funcionario')

    def __repr__(self):
        return f'<Funcionario {self.usuario.nome}>'

class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), nullable=False)
    data_agendamento = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='agendado')  # agendado, concluido, cancelado
    observacoes = db.Column(db.Text)
    servico = db.Column(db.String(200))
    duracao_minutos = db.Column(db.Integer, default=60)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Agendamento {self.id} - {self.cliente.nome}>'

class LogAuditoria(db.Model):
    __tablename__ = 'logs_auditoria'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    acao = db.Column(db.String(100), nullable=False)
    tabela = db.Column(db.String(50), nullable=False)
    registro_id = db.Column(db.Integer)
    valores_antigos = db.Column(db.Text)
    valores_novos = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))

    def __repr__(self):
        return f'<LogAuditoria {self.acao} em {self.tabela}>'

class ConfiguracaoEmpresa(db.Model):
    __tablename__ = 'configuracao_empresa'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_empresa = db.Column(db.String(200), nullable=False, default='JT Sistemas')
    logo_path = db.Column(db.String(500))
    whatsapp_token = db.Column(db.String(500))
    whatsapp_phone_id = db.Column(db.String(100))
    whatsapp_webhook_verify_token = db.Column(db.String(200))
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ConfiguracaoEmpresa {self.nome_empresa}>'
