from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
# Importe os novos tipos de campo e validadores aqui
from wtforms import (StringField, PasswordField, SelectField, TextAreaField, 
                     DateTimeField, IntegerField, BooleanField, FloatField, SubmitField)
from wtforms.validators import (DataRequired, Email, Length, EqualTo, Optional, 
                                NumberRange, ValidationError)
from wtforms.widgets import DateTimeInput

# Importe o novo modelo 'Servico' para usar no AgendamentoForm
from modelos import Cargo, Funcionario, Servico

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Senha', validators=[DataRequired()])

class CadastroUsuarioForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    nome = StringField('Nome Completo', validators=[DataRequired(), Length(min=2, max=100)])
    telefone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar Senha', 
                             validators=[DataRequired(), EqualTo('password', message='Senhas devem ser iguais')])
    tipo_usuario = SelectField('Tipo de Usuário', 
                              choices=[('restrito', 'Usuário Restrito')],
                              default='restrito')
    
    # Permissões para usuários restritos
    pode_cadastrar_cliente = BooleanField('Pode Cadastrar Clientes')
    pode_cadastrar_funcionario = BooleanField('Pode Cadastrar Funcionários')
    pode_cadastrar_cargo = BooleanField('Pode Cadastrar Cargos')
    pode_agendar = BooleanField('Pode Agendar', default=True)
    pode_ver_agendamentos = BooleanField('Pode Ver Agendamentos', default=True)
    pode_ver_relatorios = BooleanField('Pode Ver Relatórios')

class UsuarioEditForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    nome = StringField('Nome Completo', validators=[DataRequired(), Length(min=2, max=100)])
    telefone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    ativo = BooleanField('Ativo', default=True)
    pode_cadastrar_cliente = BooleanField('Pode Cadastrar Clientes')
    pode_cadastrar_funcionario = BooleanField('Pode Cadastrar Funcionários')
    pode_cadastrar_cargo = BooleanField('Pode Cadastrar Cargos')
    pode_agendar = BooleanField('Pode Agendar')
    pode_ver_agendamentos = BooleanField('Pode Ver Agendamentos')
    pode_ver_relatorios = BooleanField('Pode Ver Relatórios')
    submit = SubmitField('Salvar')

class CadastroClienteForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    nome = StringField('Nome Completo', validators=[DataRequired(), Length(min=2, max=100)])
    telefone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar Senha', 
                             validators=[DataRequired(), EqualTo('password', message='Senhas devem ser iguais')])

class FuncionarioForm(FlaskForm):
    usuario_id = SelectField('Usuário', coerce=int, validators=[DataRequired()])
    cargo_id = SelectField('Cargo', coerce=int, validators=[DataRequired()])
    
    def __init__(self, *args, **kwargs):
        super(FuncionarioForm, self).__init__(*args, **kwargs)
        # Populate choices dynamically
        from modelos import Usuario
        self.usuario_id.choices = [(u.id, f"{u.nome} ({u.username})") 
                                 for u in Usuario.query.filter(
                                     Usuario.ativo == True,
                                     Usuario.perfil_funcionario == None
                                 ).all()]
        self.cargo_id.choices = [(c.id, c.nome) 
                               for c in Cargo.query.all()]

class CargoForm(FlaskForm):
    nome = StringField('Nome do Cargo', validators=[DataRequired(), Length(min=2, max=100)])
    descricao = TextAreaField('Descrição', validators=[Optional(), Length(max=500)])

class AgendamentoForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    funcionario_id = SelectField('Funcionário', coerce=int, validators=[DataRequired()])
    data_agendamento = DateTimeField('Data e Hora', 
                                    validators=[DataRequired()],
                                    widget=DateTimeInput())
    # O campo de servico agora deve ser um SelectField para o novo modelo de Servico
    servico_id = SelectField('Serviço', coerce=int, validators=[DataRequired()])
    observacoes = TextAreaField('Observações', validators=[Optional(), Length(max=500)])
    
    def __init__(self, *args, **kwargs):
        super(AgendamentoForm, self).__init__(*args, **kwargs)
        # Populate choices dynamically
        from modelos import Usuario
        clientes = Usuario.query.filter(
            Usuario.ativo == True,
            Usuario.tipo_usuario == 'restrito',
            Usuario.perfil_funcionario == None
        ).all()
        
        self.cliente_id.choices = [(u.id, f"{u.nome} ({u.email})") for u in clientes]
        self.funcionario_id.choices = [(f.id, f"{f.usuario.nome} - {f.cargo.nome}") 
                                      for f in Funcionario.query.filter_by(ativo=True).all()]
        self.servico_id.choices = [(s.id, f"{s.nome} - R$ {s.preco:.2f}")
                                  for s in Servico.query.filter_by(ativo=True).all()]

class AtualizarStatusAgendamentoForm(FlaskForm):
    status = SelectField('Status', 
                         choices=[('agendado', 'Agendado'), 
                                  ('concluido', 'Concluído'), 
                                  ('cancelado', 'Cancelado')],
                         validators=[DataRequired()])
    observacoes = TextAreaField('Observações', validators=[Optional(), Length(max=500)])

class ConfiguracaoBotWhatsAppForm(FlaskForm):
    whatsapp_token = StringField('Token de Acesso do WhatsApp', 
                                 validators=[Optional(), Length(max=500)])
    whatsapp_phone_id = StringField('ID do Telefone', 
                                   validators=[Optional(), Length(max=100)])
    whatsapp_webhook_verify_token = StringField('Token de Verificação do Webhook', 
                                               validators=[Optional(), Length(max=200)])

class ConfiguracaoEmpresaForm(FlaskForm):
    nome_empresa = StringField('Nome da Empresa', 
                               validators=[DataRequired(), Length(min=2, max=200)])
    logo = FileField('Logo da Empresa', 
                     validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 
                                             'Apenas imagens são permitidas!')])

# Nova classe de formulário para serviços
class ServicoForm(FlaskForm):
    nome = StringField('Nome do Serviço', validators=[DataRequired(), Length(min=2, max=100)])
    descricao = TextAreaField('Descrição', validators=[Length(max=500)])
    preco = FloatField('Preço (R$)', validators=[DataRequired(), NumberRange(min=0.01)])
    duracao_minutos = IntegerField('Duração (minutos)', validators=[DataRequired(), NumberRange(min=1)])
    ativo = BooleanField('Ativo', default=True)
    submit = SubmitField('Salvar Serviço')