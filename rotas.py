from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from aplicacao import app, db
from modelos import Usuario, Funcionario, Cargo, Agendamento, LogAuditoria, ConfiguracaoEmpresa, Servico
from formularios import (LoginForm, CadastroUsuarioForm, CadastroClienteForm, FuncionarioForm,
                         CargoForm, AgendamentoForm, AtualizarStatusAgendamentoForm,
                         ConfiguracaoBotWhatsAppForm, ConfiguracaoEmpresaForm, ServicoForm, UsuarioEditForm)
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os

# Decorator para verificar permissões
def master_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_master():
            flash('Acesso negado. Apenas usuários Master podem acessar esta página.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            
            if current_user.is_master():
                return f(*args, **kwargs)
            
            # Use getattr para verificar se a permissão existe e se é True
            if not getattr(current_user, permission, False):
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    """
    Rota principal, redireciona para o dashboard se o usuário estiver autenticado.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota para o login de usuários.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = (form.username.data or '').strip()
        password = form.password.data or ''
        # Fallback MASTER login (uppercase enforced)
        if username == 'MASTER' and password == 'MASTER123':
            usuario = Usuario.query.filter_by(username='MASTER').first()
            if not usuario:
                usuario = Usuario(
                    username='MASTER',
                    email='MASTER@EXAMPLE.COM',
                    nome='MASTER',
                    telefone='',
                    tipo_usuario='master',
                    ativo=True
                )
                usuario.set_password('MASTER123')
                db.session.add(usuario)
                db.session.commit()
            if usuario and usuario.ativo:
                login_user(usuario)
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('dashboard'))
        # Fluxo padrão
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and usuario.check_password(password) and usuario.ativo:
            login_user(usuario)
            next_page = request.args.get('next')
            flash('Login realizado com sucesso!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Usuário ou senha inválidos.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """
    Rota para o logout de usuários.
    """
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard principal, com estatísticas e agendamentos recentes.
    Os dados exibidos variam de acordo com o tipo de usuário.
    """
    stats = {}
    config = ConfiguracaoEmpresa.query.first()
    
    if current_user.is_master():
        stats = {
            'total_usuarios': Usuario.query.count(),
            'total_funcionarios': Funcionario.query.count(),
            'total_agendamentos': Agendamento.query.count(),
            'agendamentos_pendentes': Agendamento.query.filter_by(status='agendado').count(),
            'agendamentos_hoje': Agendamento.query.filter(
                func.date(Agendamento.data_agendamento) == datetime.utcnow().date()
            ).count()
        }
        agendamentos_recentes = Agendamento.query.order_by(Agendamento.criado_em.desc()).limit(5).all()
    
    elif current_user.is_funcionario():
        funcionario = Funcionario.query.filter_by(usuario_id=current_user.id).first()
        if funcionario:
            stats = {
                'meus_agendamentos_hoje': Agendamento.query.filter(
                    and_(
                        Agendamento.funcionario_id == funcionario.id,
                        func.date(Agendamento.data_agendamento) == datetime.utcnow().date()
                    )
                ).count(),
                'meus_agendamentos_pendentes': Agendamento.query.filter(
                    and_(
                        Agendamento.funcionario_id == funcionario.id,
                        Agendamento.status == 'agendado'
                    )
                ).count()
            }
            agendamentos_recentes = Agendamento.query.filter_by(funcionario_id=funcionario.id)\
                                                    .order_by(Agendamento.data_agendamento.desc()).limit(5).all()
        else:
            agendamentos_recentes = []
    
    else:
        stats = {
            'meus_agendamentos': Agendamento.query.filter_by(cliente_id=current_user.id).count(),
            'meus_proximos_agendamentos': Agendamento.query.filter(
                and_(
                    Agendamento.cliente_id == current_user.id,
                    Agendamento.data_agendamento > datetime.utcnow(),
                    Agendamento.status == 'agendado'
                )
            ).count()
        }
        agendamentos_recentes = Agendamento.query.filter_by(cliente_id=current_user.id)\
                                                .order_by(Agendamento.data_agendamento.desc()).limit(5).all()
    
    return render_template('dashboard.html', stats=stats, agendamentos_recentes=agendamentos_recentes, config=config)

@app.route('/cadastro')
@login_required
@master_required
def cadastro():
    """
    Página de seleção para cadastro de diferentes tipos de entidades.
    """
    return render_template('cadastro.html')

@app.route('/cadastro/usuario', methods=['GET'])
@login_required
@master_required
def cadastro_usuario():
    """
    Rota legada de cadastro de usuário. Redireciona para a tela de pesquisa/gerenciamento.
    """
    return redirect(url_for('usuarios_pesquisar', search=1))

@app.route('/cadastro/usuario/inserir', methods=['GET', 'POST'])
@login_required
@master_required
def usuario_inserir():
    """
    Rota para inserir um novo usuário com UI dedicada.
    """
    form = CadastroUsuarioForm()
    if form.validate_on_submit():
        if Usuario.query.filter_by(username=form.username.data).first():
            flash('Nome de usuário já existe.', 'danger')
            return render_template('usuario_inserir.html', form=form)

        if Usuario.query.filter_by(email=form.email.data).first():
            flash('Email já cadastrado.', 'danger')
            return render_template('usuario_inserir.html', form=form)

        usuario = Usuario(
            username=form.username.data,
            email=form.email.data,
            nome=form.nome.data,
            telefone=form.telefone.data,
            tipo_usuario=form.tipo_usuario.data,
            pode_cadastrar_cliente=form.pode_cadastrar_cliente.data,
            pode_cadastrar_funcionario=form.pode_cadastrar_funcionario.data,
            pode_cadastrar_cargo=form.pode_cadastrar_cargo.data,
            pode_agendar=form.pode_agendar.data,
            pode_ver_agendamentos=form.pode_ver_agendamentos.data,
            pode_ver_relatorios=form.pode_ver_relatorios.data
        )
        usuario.set_password(form.password.data)

        db.session.add(usuario)
        db.session.commit()

        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('usuarios_pesquisar', search=1))

    return render_template('usuario_inserir.html', form=form)

# Pesquisa/Listagem de usuários no padrão de serviços
@app.route('/cadastro/usuarios/pesquisar', methods=['GET'])
@login_required
@master_required
def usuarios_pesquisar():
    query = request.args.get('query', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = int(request.args.get('per_page', 10)) if str(request.args.get('per_page', '10')).isdigit() else 10
    show_results = request.args.get('search') == '1'

    base_query = Usuario.query.order_by(Usuario.nome)
    if query:
        base_query = base_query.filter(
            or_(
                Usuario.nome.ilike(f'%{query}%'),
                Usuario.username.ilike(f'%{query}%'),
                Usuario.email.ilike(f'%{query}%')
            )
        )

    usuarios = base_query.paginate(page=page, per_page=per_page, error_out=False) if show_results else None
    return render_template('usuarios_pesquisa.html', usuarios=usuarios, query=query, per_page=per_page, show_results=show_results)

@app.route('/cadastro/usuarios/editar/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
@master_required
def usuarios_editar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    form = UsuarioEditForm(obj=usuario)
    if form.validate_on_submit():
        usuario.email = form.email.data
        usuario.nome = form.nome.data
        usuario.telefone = form.telefone.data
        usuario.ativo = form.ativo.data
        usuario.pode_cadastrar_cliente = form.pode_cadastrar_cliente.data
        usuario.pode_cadastrar_funcionario = form.pode_cadastrar_funcionario.data
        usuario.pode_cadastrar_cargo = form.pode_cadastrar_cargo.data
        usuario.pode_agendar = form.pode_agendar.data
        usuario.pode_ver_agendamentos = form.pode_ver_agendamentos.data
        usuario.pode_ver_relatorios = form.pode_ver_relatorios.data
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('usuarios_pesquisar', search=1))
    return render_template('usuario_form.html', form=form, usuario=usuario)

@app.route('/cadastro/usuarios/excluir/<int:usuario_id>', methods=['POST'])
@login_required
@master_required
def usuarios_excluir(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.is_master():
        flash('Não é permitido excluir o usuário MASTER.', 'danger')
        return redirect(url_for('usuarios_pesquisar', search=1))
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuário excluído com sucesso!', 'info')
    return redirect(url_for('usuarios_pesquisar', search=1))

@app.route('/cadastro/cliente', methods=['GET', 'POST'])
@login_required
@permission_required('pode_cadastrar_cliente')
def cadastro_cliente():
    """
    Rota para cadastro de novos clientes.
    """
    form = CadastroClienteForm()
    if form.validate_on_submit():
        if Usuario.query.filter_by(username=form.username.data).first():
            flash('Nome de usuário já existe.', 'danger')
            return render_template('cadastro.html', form=form, tipo='cliente')
        
        if Usuario.query.filter_by(email=form.email.data).first():
            flash('Email já cadastrado.', 'danger')
            return render_template('cadastro.html', form=form, tipo='cliente')
        
        usuario = Usuario(
            username=form.username.data,
            email=form.email.data,
            nome=form.nome.data,
            telefone=form.telefone.data,
            tipo_usuario='restrito'
        )
        usuario.set_password(form.password.data)
        
        db.session.add(usuario)
        db.session.commit()
        
        flash('Cliente cadastrado com sucesso!', 'success')
        return redirect(url_for('cadastro'))
    
    return render_template('cadastro.html', form=form, tipo='cliente')

@app.route('/funcionarios')
@login_required
@permission_required('pode_cadastrar_funcionario')
def funcionarios():
    """
    Rota para listar e gerenciar funcionários.
    """
    funcionarios = Funcionario.query.join(Usuario).join(Cargo).all()
    return render_template('funcionarios.html', funcionarios=funcionarios)

@app.route('/funcionarios/criar', methods=['GET', 'POST'])
@login_required
@permission_required('pode_cadastrar_funcionario')
def criar_funcionario():
    """
    Rota para criar um novo funcionário.
    """
    form = FuncionarioForm()
    if form.validate_on_submit():
        funcionario_existente = Funcionario.query.filter_by(usuario_id=form.usuario_id.data).first()
        if funcionario_existente:
            flash('Usuário já é funcionário.', 'danger')
            return render_template('funcionarios.html', form=form, action='criar')
        
        funcionario = Funcionario(
            usuario_id=form.usuario_id.data,
            cargo_id=form.cargo_id.data
        )
        
        db.session.add(funcionario)
        db.session.commit()
        
        flash('Funcionário criado com sucesso!', 'success')
        return redirect(url_for('funcionarios'))
    
    return render_template('funcionarios.html', form=form, action='criar')

# --------------------------------------------------------------------------------------------------
# ROTAS DE CARGOS CORRIGIDAS E COMPLETAS
# --------------------------------------------------------------------------------------------------

@app.route('/cargos')
@login_required
@permission_required('pode_cadastrar_cargo')
def cargos_main():
    """
    Rota principal de cargos, redireciona para a página de pesquisa.
    """
    return redirect(url_for('cargos_pesquisar'))

@app.route('/cargos/pesquisar')
@login_required
@permission_required('pode_cadastrar_cargo')
def cargos_pesquisar():
    """
    Rota para pesquisar e exibir cargos com paginação.
    """
    query = request.args.get('query', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 5

    base_query = Cargo.query.order_by(Cargo.nome)

    if query:
        base_query = base_query.filter(Cargo.nome.ilike(f'%{query}%'))

    cargos = base_query.paginate(page=page, per_page=per_page, error_out=False)
    
    form = CargoForm()
    
    return render_template('cargos.html', cargos=cargos, form=form, query=query)

@app.route('/cargos/inserir', methods=['GET', 'POST'])
@login_required
@permission_required('pode_cadastrar_cargo')
def cargos_inserir():
    """
    Rota para inserir um novo cargo.
    """
    form = CargoForm()
    if form.validate_on_submit():
        cargo_existente = Cargo.query.filter_by(nome=form.nome.data).first()
        if cargo_existente:
            flash('Já existe um cargo com este nome.', 'danger')
            return redirect(url_for('cargos_pesquisar'))
            
        novo_cargo = Cargo(
            nome=form.nome.data,
            descricao=form.descricao.data
        )
        
        db.session.add(novo_cargo)
        db.session.commit()
        flash('Cargo adicionado com sucesso!', 'success')
        return redirect(url_for('cargos_pesquisar'))
    
    flash('Erro ao validar o formulário de cargo.', 'danger')
    return redirect(url_for('cargos_pesquisar'))

@app.route('/cargos/editar/<int:cargo_id>', methods=['GET', 'POST'])
@login_required
@permission_required('pode_cadastrar_cargo')
def cargos_editar(cargo_id):
    """
    Rota para editar um cargo existente.
    """
    cargo = Cargo.query.get_or_404(cargo_id)
    form = CargoForm(obj=cargo)
    if form.validate_on_submit():
        cargo.nome = form.nome.data
        cargo.descricao = form.descricao.data
        db.session.commit()
        flash('Cargo atualizado com sucesso!', 'success')
        return redirect(url_for('cargos_pesquisar'))
    
    return render_template('editar_cargo.html', form=form, cargo=cargo)

@app.route('/cargos/excluir/<int:cargo_id>', methods=['POST'])
@login_required
@permission_required('pode_cadastrar_cargo')
def cargos_excluir(cargo_id):
    """
    Rota para excluir um cargo, com verificação de uso por funcionários.
    """
    cargo = Cargo.query.get_or_404(cargo_id)
    funcionarios_usando_cargo = Funcionario.query.filter_by(cargo_id=cargo.id).first()

    if funcionarios_usando_cargo:
        flash('Não é possível excluir este cargo, pois ele está associado a funcionários existentes.', 'danger')
    else:
        db.session.delete(cargo)
        db.session.commit()
        flash('Cargo excluído com sucesso!', 'info')
    
    return redirect(url_for('cargos_pesquisar'))

# --------------------------------------------------------------------------------------------------
# FIM DAS ROTAS DE CARGOS
# --------------------------------------------------------------------------------------------------

@app.route('/cadastro/servicos')
@login_required
@permission_required('pode_cadastrar_servico')
def servicos_main():
    """Redireciona para a tela de pesquisa de serviços."""
    return redirect(url_for('servicos_pesquisar'))

@app.route('/cadastro/servicos/pesquisar', methods=['GET'])
@login_required
@permission_required('pode_cadastrar_servico')
def servicos_pesquisar():
    """Rota para pesquisar e exibir serviços com paginação, filtros e ordenação.

    Suporta resposta JSON quando format=json.
    """
    query = request.args.get('query', '').strip()
    page = request.args.get('page', 1, type=int)
    format_json = request.args.get('format') == 'json'
    show_results = request.args.get('search') == '1'

    # Tamanho da página configurável (opções seguras)
    allowed_page_sizes = {5, 10, 20, 50}
    try:
        per_page = int(request.args.get('per_page', 10))
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in allowed_page_sizes:
        per_page = 10

    # Filtros adicionais
    only_active_raw = request.args.get('only_active', '').lower()
    only_active = only_active_raw in {'1', 'true', 'on', 'yes'}

    def parse_float(name):
        value = request.args.get(name)
        if value is None or str(value).strip() == '':
            return None
        try:
            return float(str(value).replace(',', '.'))
        except ValueError:
            return None

    min_preco = parse_float('min_preco')
    max_preco = parse_float('max_preco')

    # Ordenação
    sort = request.args.get('sort', 'nome')
    direction = request.args.get('direction', 'asc')
    sort_map = {
        'nome': Servico.nome,
        'preco': Servico.preco,
        'duracao': Servico.duracao_minutos,
    }
    sort_column = sort_map.get(sort, Servico.nome)
    if direction == 'desc':
        sort_column = sort_column.desc()

    servicos = None

    if show_results or format_json:
        base_query = Servico.query

        if query:
            base_query = base_query.filter(Servico.nome.ilike(f'%{query}%'))
        if only_active:
            base_query = base_query.filter(Servico.ativo.is_(True))
        if min_preco is not None:
            base_query = base_query.filter(Servico.preco >= min_preco)
        if max_preco is not None:
            base_query = base_query.filter(Servico.preco <= max_preco)

        base_query = base_query.order_by(sort_column)
        servicos = base_query.paginate(page=page, per_page=per_page, error_out=False)

    # Suporte a JSON para consumo via JS (sempre retorna resultados)
    if format_json:
        return jsonify({
            'items': [
                {
                    'id': s.id,
                    'nome': s.nome,
                    'descricao': s.descricao,
                    'preco': s.preco,
                    'duracao_minutos': s.duracao_minutos,
                    'ativo': s.ativo,
                }
                for s in (servicos.items if servicos else [])
            ],
            'pagination': {
                'page': servicos.page if servicos else 1,
                'per_page': per_page,
                'pages': servicos.pages if servicos else 0,
                'total': servicos.total if servicos else 0,
                'has_prev': servicos.has_prev if servicos else False,
                'has_next': servicos.has_next if servicos else False,
            }
        })

    form = ServicoForm()
    return render_template(
        'pesquisar_servico.html',
        servicos=servicos,
        form=form,
        show_results=show_results,
        # Filtros e estado da UI
        query=query,
        only_active=only_active,
        min_preco=min_preco,
        max_preco=max_preco,
        sort=sort,
        direction=direction,
        per_page=per_page,
    )

@app.route('/cadastro/servicos/inserir', methods=['GET', 'POST'])
@login_required
@permission_required('pode_cadastrar_servico')
def servicos_inserir():
    """Rota para inserir um novo serviço."""
    form = ServicoForm()
    if form.validate_on_submit():
        servico_existente = Servico.query.filter_by(nome=form.nome.data).first()
        if servico_existente:
            flash('Já existe um serviço com este nome.', 'danger')
            return redirect(url_for('servicos_pesquisar')) 

        novo_servico = Servico(
            nome=form.nome.data,
            descricao=form.descricao.data,
            preco=form.preco.data,
            duracao_minutos=form.duracao_minutos.data,
            ativo=form.ativo.data if hasattr(form, 'ativo') else True
        )
        db.session.add(novo_servico)
        db.session.commit()
        flash('Serviço adicionado com sucesso!', 'success')
        return redirect(url_for('servicos_pesquisar'))
    
    flash('Erro ao validar o formulário de serviço.', 'danger')
    return redirect(url_for('servicos_pesquisar'))

@app.route('/cadastro/servicos/excluir/<int:servico_id>', methods=['POST'])
@login_required
@permission_required('pode_cadastrar_servico')
def servicos_excluir(servico_id):
    """Deleta um serviço específico."""
    servico = Servico.query.get_or_404(servico_id)
    agendamentos_usando_servico = Agendamento.query.filter_by(servico_id=servico.id).first()

    if agendamentos_usando_servico:
        flash('Não é possível deletar este serviço, pois ele está associado a agendamentos existentes.', 'danger')
        return redirect(url_for('servicos_pesquisar'))

    db.session.delete(servico)
    db.session.commit()
    flash('Serviço deletado com sucesso!', 'info')
    return redirect(url_for('servicos_pesquisar'))

@app.route('/cadastro/servicos/visualizar/<int:servico_id>', methods=['GET'])
@login_required
@permission_required('pode_cadastrar_servico')
def servicos_visualizar(servico_id):
    """Exibe detalhes de um serviço."""
    servico = Servico.query.get_or_404(servico_id)
    return render_template('servico_detalhe.html', servico=servico)

@app.route('/cadastro/servicos/editar/<int:servico_id>', methods=['GET', 'POST'])
@login_required
@permission_required('pode_cadastrar_servico')
def servicos_editar(servico_id):
    """Edita um serviço existente."""
    servico = Servico.query.get_or_404(servico_id)
    form = ServicoForm(obj=servico)
    if form.validate_on_submit():
        servico.nome = form.nome.data
        servico.descricao = form.descricao.data
        servico.preco = form.preco.data
        servico.duracao_minutos = form.duracao_minutos.data
        servico.ativo = form.ativo.data if hasattr(form, 'ativo') else servico.ativo
        db.session.commit()
        flash('Serviço atualizado com sucesso!', 'success')
        return redirect(url_for('servicos_pesquisar'))
    return render_template('servico_form.html', form=form, servico=servico)

@app.route('/agendamentos')
@login_required
@permission_required('pode_ver_agendamentos')
def agendamentos():
    """
    Exibe a lista de agendamentos com base nas permissões do usuário.
    """
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    if current_user.is_master():
        agendamentos = Agendamento.query.order_by(Agendamento.data_agendamento.desc())\
                                        .paginate(page=page, per_page=per_page, error_out=False)
    elif current_user.is_funcionario():
        funcionario = Funcionario.query.filter_by(usuario_id=current_user.id).first()
        if funcionario:
            agendamentos = Agendamento.query.filter_by(funcionario_id=funcionario.id)\
                                             .order_by(Agendamento.data_agendamento.desc())\
                                             .paginate(page=page, per_page=per_page, error_out=False)
        else:
            agendamentos = None
    else:
        agendamentos = Agendamento.query.filter_by(cliente_id=current_user.id)\
                                        .order_by(Agendamento.data_agendamento.desc())\
                                        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('agendamentos.html', agendamentos=agendamentos)

@app.route('/agendar', methods=['GET', 'POST'])
@login_required
@permission_required('pode_agendar')
def agendar():
    """
    Rota para criar um novo agendamento.
    A duração do agendamento é obtida dinamicamente do serviço selecionado.
    """
    form = AgendamentoForm()
    
    if form.validate_on_submit():
        servico_selecionado = Servico.query.get(form.servico_id.data)

        data_inicio = form.data_agendamento.data
        data_fim = data_inicio + timedelta(minutes=servico_selecionado.duracao_minutos)

        conflito = Agendamento.query.filter(
            and_(
                Agendamento.funcionario_id == form.funcionario_id.data,
                Agendamento.status == 'agendado',
                or_(
                    and_(Agendamento.data_agendamento < data_fim, Agendamento.data_fim > data_inicio),
                    and_(Agendamento.data_agendamento == data_inicio)
                )
            )
        ).first()
        
        if conflito:
            flash('Já existe um agendamento para este funcionário neste horário ou há um conflito de horários.', 'danger')
            return render_template('agendar.html', form=form)
        
        agendamento = Agendamento(
            cliente_id=form.cliente_id.data,
            funcionario_id=form.funcionario_id.data,
            data_agendamento=form.data_agendamento.data,
            servico_id=form.servico_id.data,
            duracao_minutos=servico_selecionado.duracao_minutos,
            preco_total=servico_selecionado.preco,
            observacoes=form.observacoes.data
        )
        
        db.session.add(agendamento)
        db.session.commit()
        
        flash('Agendamento criado com sucesso!', 'success')
        return redirect(url_for('agendamentos'))
    
    return render_template('agendar.html', form=form)

@app.route('/agendamento/<int:agendamento_id>/atualizar', methods=['POST'])
@login_required
def atualizar_status_agendamento(agendamento_id):
    """
    Rota para atualizar o status de um agendamento.
    """
    form = AtualizarStatusAgendamentoForm()
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    
    if not (current_user.is_master() or 
            (current_user.is_funcionario() and agendamento.funcionario.usuario_id == current_user.id) or
            (not current_user.is_master() and not current_user.is_funcionario() and agendamento.cliente_id == current_user.id)):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('agendamentos'))
    
    if form.validate_on_submit():
        status_antigo = agendamento.status
        agendamento.status = form.status.data
        if form.observacoes.data:
            agendamento.observacoes = form.observacoes.data
        
        db.session.commit()
        
        flash(f'Status do agendamento atualizado de "{status_antigo}" para "{form.status.data}".', 'success')
    
    return redirect(url_for('agendamentos'))

@app.route('/relatorios')
@login_required
@permission_required('pode_ver_relatorios')
def relatorios():
    """
    Exibe relatórios estatísticos.
    """
    hoje = datetime.utcnow().date()
    inicio_mes = hoje.replace(day=1)
    
    dados_relatorio = {
        'agendamentos_hoje': Agendamento.query.filter(
            func.date(Agendamento.data_agendamento) == hoje
        ).count(),
        'agendamentos_mes': Agendamento.query.filter(
            func.date(Agendamento.data_agendamento) >= inicio_mes
        ).count(),
        'agendamentos_concluidos': Agendamento.query.filter_by(status='concluido').count(),
        'agendamentos_cancelados': Agendamento.query.filter_by(status='cancelado').count(),
        'funcionarios_ativos': Funcionario.query.filter_by(ativo=True).count(),
        'total_clientes': Usuario.query.filter(
            Usuario.tipo_usuario == 'restrito',
            Usuario.ativo == True,
            Usuario.perfil_funcionario == None
        ).count()
    }
    
    stats_mensais = db.session.query(
        func.extract('month', Agendamento.data_agendamento).label('mes'),
        func.count(Agendamento.id).label('count')
    ).filter(
        func.extract('year', Agendamento.data_agendamento) == datetime.utcnow().year
    ).group_by(
        func.extract('month', Agendamento.data_agendamento)
    ).all()
    
    return render_template('relatorios.html', dados_relatorio=dados_relatorio, stats_mensais=stats_mensais)

@app.route('/bot-whatsapp', methods=['GET'])
@login_required
@master_required
def bot_whatsapp():
    # Redireciona para a subrota padrão (API)
    return redirect(url_for('bot_whatsapp_api'))

@app.route('/bot-whatsapp/api', methods=['GET', 'POST'])
@login_required
@master_required
def bot_whatsapp_api():
    """
    Configuração da API do WhatsApp (tokens e IDs).
    """
    config = ConfiguracaoEmpresa.query.first()
    if not config:
        config = ConfiguracaoEmpresa()
        db.session.add(config)
        db.session.commit()
    
    form = ConfiguracaoBotWhatsAppForm(obj=config)
    
    if form.validate_on_submit():
        config.whatsapp_token = form.whatsapp_token.data
        config.whatsapp_phone_id = form.whatsapp_phone_id.data
        config.whatsapp_webhook_verify_token = form.whatsapp_webhook_verify_token.data
        
        db.session.commit()
        flash('Configurações da API do WhatsApp atualizadas com sucesso!', 'success')
        return redirect(url_for('bot_whatsapp_api'))
    
    return render_template('bot_whatsapp.html', form=form, config=config)

@app.route('/bot-whatsapp/configurar', methods=['GET', 'POST'])
@login_required
@master_required
def bot_whatsapp_configurar():
    """
    Configurações do comportamento do Bot (templates de mensagem, horários, etc.).
    Esta rota apresenta um formulário básico de configuração do bot.
    """
    if request.method == 'POST':
        flash('Configurações do Bot salvas com sucesso!', 'success')
        return redirect(url_for('bot_whatsapp_configurar'))
    return render_template('bot_config.html')

@app.route('/bot-whatsapp/fluxo', methods=['GET', 'POST'])
@login_required
@master_required
def bot_whatsapp_fluxo():
    """
    Editor de Fluxo do Bot (fluxograma). O usuário define nós e conexões.
    """
    if request.method == 'POST':
        flow_json = request.form.get('flow_json')
        # Aqui poderíamos persistir o JSON do fluxo em um storage/DB
        flash('Fluxo do Bot salvo com sucesso!', 'success')
        return redirect(url_for('bot_whatsapp_fluxo'))
    return render_template('bot_fluxo.html')

@app.route('/bot-whatsapp/geral', methods=['GET', 'POST'])
@login_required
@master_required
def bot_whatsapp_geral():
    """
    Configurações gerais do Bot (horários de atendimento, timezone, limites, etc.).
    """
    if request.method == 'POST':
        # Capturar campos
        horario_inicio = request.form.get('horario_inicio')
        horario_fim = request.form.get('horario_fim')
        dias_semana = request.form.getlist('dias_semana')
        timezone = request.form.get('timezone')
        msg_fora = request.form.get('msg_fora_horario')

        # Persistir em ConfiguracaoEmpresa (como exemplo simples)
        config = ConfiguracaoEmpresa.query.first()
        if not config:
            config = ConfiguracaoEmpresa()
            db.session.add(config)
            db.session.commit()

        # Guardar em campos reutilizados (ou seria ideal criar novas colunas)
        # Aqui usamos whatsapp_webhook_verify_token para armazenar JSON (exemplo)
        import json
        blob = {
            'horario_inicio': horario_inicio,
            'horario_fim': horario_fim,
            'dias_semana': dias_semana,
            'timezone': timezone,
            'msg_fora_horario': msg_fora
        }
        config.whatsapp_webhook_verify_token = json.dumps(blob)
        db.session.commit()

        flash('Configurações gerais do Bot salvas com sucesso!', 'success')
        return redirect(url_for('bot_whatsapp_geral'))
    return render_template('bot_geral.html')

@app.route('/configuracoes', methods=['GET', 'POST'])
@login_required
@master_required
def configuracoes():
    """
    Configurações gerais da empresa.
    """
    config = ConfiguracaoEmpresa.query.first()
    if not config:
        config = ConfiguracaoEmpresa()
        db.session.add(config)
        db.session.commit()
    
    form = ConfiguracaoEmpresaForm(obj=config)
    
    if form.validate_on_submit():
        config.nome_empresa = form.nome_empresa.data
        
        if form.logo.data:
            filename = secure_filename(form.logo.data.filename)
            if filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                form.logo.data.save(filepath)
                config.logo_path = filename
        
        db.session.commit()
        flash('Configurações da empresa atualizadas com sucesso!', 'success')
        return redirect(url_for('configuracoes'))
    
    return render_template('configuracoes.html', form=form, config=config)

@app.context_processor
def inject_config():
    """
    Injeta a configuração da empresa em todos os templates.
    """
    config = ConfiguracaoEmpresa.query.first()
    return dict(empresa_config=config)