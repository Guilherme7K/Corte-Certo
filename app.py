from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Usuario, Servico, Agendamento, HorarioFuncionamento
from datetime import datetime, timedelta
from functools import wraps
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from utils import obter_horarios_disponiveis, obter_agendamentos_por_periodo, obter_agendamentos_do_mes, calcular_receita_periodo
import os
import re

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Usar as configs do arquivo config.py
BARBEIRO_INFO = {
    'nome': 'João Silva',
    'barbearia': Config.NOME_EMPRESA,
    'endereco': Config.ENDERECO,
    'telefone': Config.TELEFONE,
    'email': Config.EMAIL_CONTATO
}

# Inicializar banco de dados automaticamente
def init_db():
    """Inicializa o banco de dados com tabelas e dados padrão"""
    with app.app_context():
        try:
            # Criar todas as tabelas
            db.create_all()
            print("✅ Tabelas criadas/verificadas!")
            
            # Verificar se já existe um admin
            admin = Usuario.query.filter_by(email='admin@cortecerto.com').first()
            if not admin:
                admin = Usuario(
                    nome='Administrador',
                    email='admin@cortecerto.com',
                    telefone='11987654321',
                    senha=generate_password_hash('admin123'),
                    tipo='admin'
                )
                db.session.add(admin)
                print("✅ Usuário admin criado!")
            
            # Verificar se já existem serviços
            if Servico.query.count() == 0:
                servicos_padrao = [
                    Servico(nome='Corte de Cabelo', descricao='Corte masculino tradicional ou moderno', preco=35.00, duracao=30, ativo=True),
                    Servico(nome='Barba', descricao='Aparar e modelar barba', preco=25.00, duracao=20, ativo=True),
                    Servico(nome='Corte + Barba', descricao='Combo completo de corte e barba', preco=50.00, duracao=45, ativo=True),
                    Servico(nome='Sobrancelha', descricao='Design de sobrancelha masculina', preco=15.00, duracao=15, ativo=True),
                    Servico(nome='Hidratação', descricao='Tratamento capilar com hidratação profunda', preco=40.00, duracao=30, ativo=True),
                    Servico(nome='Acabamento', descricao='Finalização com máquina e navalha', preco=20.00, duracao=15, ativo=True),
                ]
                db.session.add_all(servicos_padrao)
                print("✅ Serviços padrão criados!")
            
            # Verificar se já existem horários de funcionamento
            if HorarioFuncionamento.query.count() == 0:
                horarios = [
                    HorarioFuncionamento(dia_semana=1, horario_abertura='09:00', horario_fechamento='19:00', ativo=True),
                    HorarioFuncionamento(dia_semana=2, horario_abertura='09:00', horario_fechamento='19:00', ativo=True),
                    HorarioFuncionamento(dia_semana=3, horario_abertura='09:00', horario_fechamento='19:00', ativo=True),
                    HorarioFuncionamento(dia_semana=4, horario_abertura='09:00', horario_fechamento='19:00', ativo=True),
                    HorarioFuncionamento(dia_semana=5, horario_abertura='09:00', horario_fechamento='19:00', ativo=True),
                    HorarioFuncionamento(dia_semana=6, horario_abertura='09:00', horario_fechamento='17:00', ativo=True),
                    HorarioFuncionamento(dia_semana=0, horario_abertura='09:00', horario_fechamento='13:00', ativo=False),
                ]
                db.session.add_all(horarios)
                print("✅ Horários de funcionamento criados!")
            
            db.session.commit()
            print("✅ Banco de dados inicializado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar banco: {e}")
            db.session.rollback()

# Chamar init_db ao iniciar
init_db()



# Decoradores de Segurança
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa fazer login para acessar esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa fazer login para acessar esta página', 'warning')
            return redirect(url_for('login'))
        if session.get('usuario_tipo') != 'admin':
            flash('Acesso negado. Área restrita a administradores.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Função para sanitizar inputs
def sanitizar_input(texto):
    if not texto:
        return texto
    # Remove caracteres perigosos
    caracteres_perigosos = ['<', '>', '"', "'", '&', '\\', '/']
    for char in caracteres_perigosos:
        texto = texto.replace(char, '')
    return texto.strip()

# Função para validar email
def validar_email(email):
    import re
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None

# Função para validar senha forte
def validar_senha_forte(senha):
    if len(senha) < 8:
        return False, "A senha deve ter no mínimo 8 caracteres"
    if not any(char.isdigit() for char in senha):
        return False, "A senha deve conter pelo menos um número"
    if not any(char.isupper() for char in senha):
        return False, "A senha deve conter pelo menos uma letra maiúscula"
    if not any(char.islower() for char in senha):
        return False, "A senha deve conter pelo menos uma letra minúscula"
    return True, "Senha válida"

@app.route('/')
def index():
    return render_template('index.html', barbeiro=BARBEIRO_INFO)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = sanitizar_input(request.form.get('email', ''))
        senha = request.form.get('senha', '')
        
        if not email or not senha:
            flash('Email e senha são obrigatórios', 'danger')
            return redirect(url_for('login'))
        
        if not validar_email(email):
            flash('Email inválido', 'danger')
            return redirect(url_for('login'))
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.verificar_senha(senha):
            session.clear()
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            session['usuario_tipo'] = usuario.tipo
            session.permanent = True
            
            flash('Login realizado com sucesso!', 'success')
            
            if usuario.tipo == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('cliente_dashboard'))
        else:
            flash('Email ou senha incorretos', 'danger')
    
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = sanitizar_input(request.form.get('nome', ''))
        email = sanitizar_input(request.form.get('email', ''))
        senha = request.form.get('senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')
        telefone = sanitizar_input(request.form.get('telefone', ''))
        
        # Validações
        if not all([nome, email, senha, confirmar_senha]):
            flash('Todos os campos obrigatórios devem ser preenchidos', 'danger')
            return redirect(url_for('cadastro'))
        
        if len(nome) < 3:
            flash('Nome deve ter pelo menos 3 caracteres', 'danger')
            return redirect(url_for('cadastro'))
        
        if not validar_email(email):
            flash('Email inválido', 'danger')
            return redirect(url_for('cadastro'))
        
        if senha != confirmar_senha:
            flash('As senhas não coincidem', 'danger')
            return redirect(url_for('cadastro'))
        
        valida, mensagem = validar_senha_forte(senha)
        if not valida:
            flash(mensagem, 'danger')
            return redirect(url_for('cadastro'))
        
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado', 'danger')
            return redirect(url_for('cadastro'))
        
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            telefone=telefone,
            tipo='cliente'
        )
        novo_usuario.set_senha(senha)
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    
    return render_template('cadastro.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logout realizado com sucesso', 'success')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    hoje = datetime.now().date()
    agora = datetime.now()
    
    # Agendamentos de hoje
    agendamentos_hoje = Agendamento.query.filter(
        db.func.date(Agendamento.data_hora) == hoje
    ).order_by(Agendamento.data_hora).all()
    
    # Estatísticas gerais
    total_agendamentos = Agendamento.query.count()
    total_clientes = Usuario.query.filter_by(tipo='cliente').count()
    
    # Substituição de strftime por db.extract
    agendamentos_mes = Agendamento.query.filter(
        db.extract('year', Agendamento.data_hora) == agora.year,
        db.extract('month', Agendamento.data_hora) == agora.month
    ).count()
    
    # Agendamentos por status hoje
    agendados_hoje = Agendamento.query.filter(
        db.func.date(Agendamento.data_hora) == hoje,
        Agendamento.status == 'agendado'
    ).count()
    
    concluidos_hoje = Agendamento.query.filter(
        db.func.date(Agendamento.data_hora) == hoje,
        Agendamento.status == 'concluido'
    ).count()
    
    # Receita estimada hoje
    agendamentos_hoje_obj = Agendamento.query.filter(
        db.func.date(Agendamento.data_hora) == hoje
    ).join(Agendamento.servico).all()
    
    receita_hoje = sum(ag.servico.preco for ag in agendamentos_hoje_obj if ag.status != 'cancelado')
    
    # Serviços mais populares (top 5)
    servicos_populares = db.session.query(
        Servico.nome,
        db.func.count(Agendamento.id).label('total')
    ).join(Agendamento).group_by(Servico.id).order_by(db.text('total DESC')).limit(5).all()
    
    # Próximos agendamentos (próximas 3 horas)
    proximos_agendamentos = Agendamento.query.filter(
        Agendamento.data_hora >= agora,
        Agendamento.data_hora <= agora + timedelta(hours=3),
        Agendamento.status == 'agendado'
    ).order_by(Agendamento.data_hora).all()
    
    # Agendamentos da semana (para gráfico)
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    agendamentos_semana = []
    for i in range(7):
        dia = inicio_semana + timedelta(days=i)
        count = Agendamento.query.filter(
            db.func.date(Agendamento.data_hora) == dia
        ).count()
        agendamentos_semana.append({
            'dia': dia.strftime('%a'),
            'count': count
        })
    
    return render_template('admin/dashboard.html',
                            agendamentos=agendamentos_hoje,
                            total_agendamentos=total_agendamentos,
                            total_clientes=total_clientes,
                            agendamentos_mes=agendamentos_mes,
                            agendados_hoje=agendados_hoje,
                            concluidos_hoje=concluidos_hoje,
                            receita_hoje=receita_hoje,
                            servicos_populares=servicos_populares,
                            proximos_agendamentos=proximos_agendamentos,
                            agendamentos_semana=agendamentos_semana,
                            barbeiro=BARBEIRO_INFO)

@app.route('/admin/agendamento/<int:id>/concluir', methods=['POST'])
@admin_required
def concluir_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)
    
    if agendamento.status != 'agendado':
        flash('Apenas agendamentos com status "agendado" podem ser concluídos', 'warning')
        return redirect(url_for('admin_agendamentos'))
    
    agendamento.status = 'concluido'
    db.session.commit()
    
    flash('Agendamento marcado como concluído!', 'success')
    return redirect(url_for('admin_agendamentos'))

@app.route('/admin/servicos', methods=['GET', 'POST'])
@admin_required
def admin_servicos():
    if request.method == 'POST':
        nome = sanitizar_input(request.form.get('nome', ''))
        descricao = sanitizar_input(request.form.get('descricao', ''))
        preco_str = request.form.get('preco', '0')
        duracao_str = request.form.get('duracao', '0')
        
        # Validações
        try:
            preco = float(preco_str)
            duracao = int(duracao_str)
            
            if preco <= 0:
                flash('Preço deve ser maior que zero', 'danger')
                return redirect(url_for('admin_servicos'))
            
            if duracao <= 0 or duracao > 480:
                flash('Duração deve ser entre 1 e 480 minutos', 'danger')
                return redirect(url_for('admin_servicos'))
            
        except ValueError:
            flash('Preço e duração devem ser números válidos', 'danger')
            return redirect(url_for('admin_servicos'))
        
        if not nome or len(nome) < 3:
            flash('Nome do serviço deve ter pelo menos 3 caracteres', 'danger')
            return redirect(url_for('admin_servicos'))
        
        novo_servico = Servico(
            nome=nome,
            descricao=descricao,
            preco=preco,
            duracao=duracao
        )
        
        db.session.add(novo_servico)
        db.session.commit()
        
        flash('Serviço cadastrado com sucesso!', 'success')
        return redirect(url_for('admin_servicos'))
    
    servicos = Servico.query.all()
    return render_template('admin/servicos.html', servicos=servicos)

@app.route('/admin/servicos/editar/<int:servico_id>', methods=['POST'])
@admin_required
def editar_servico(servico_id):
    servico = Servico.query.get_or_404(servico_id)
    
    nome = sanitizar_input(request.form.get('nome', ''))
    descricao = sanitizar_input(request.form.get('descricao', ''))
    preco_str = request.form.get('preco', '0')
    duracao_str = request.form.get('duracao', '0')
    ativo_str = request.form.get('ativo', '1')
    
    # Validações
    try:
        preco = float(preco_str)
        duracao = int(duracao_str)
        ativo = bool(int(ativo_str))
        
        if preco <= 0:
            flash('Preço deve ser maior que zero', 'danger')
            return redirect(url_for('admin_servicos'))
        
        if duracao <= 0 or duracao > 480:
            flash('Duração deve ser entre 1 e 480 minutos', 'danger')
            return redirect(url_for('admin_servicos'))
        
    except ValueError:
        flash('Preço e duração devem ser números válidos', 'danger')
        return redirect(url_for('admin_servicos'))
    
    if not nome or len(nome) < 3:
        flash('Nome do serviço deve ter pelo menos 3 caracteres', 'danger')
        return redirect(url_for('admin_servicos'))
    
    # Atualizar o serviço
    servico.nome = nome
    servico.descricao = descricao
    servico.preco = preco
    servico.duracao = duracao
    servico.ativo = ativo
    
    db.session.commit()
    
    flash('Serviço atualizado com sucesso!', 'success')
    return redirect(url_for('admin_servicos'))

@app.route('/cliente/dashboard')
@login_required
def cliente_dashboard():
    if session.get('usuario_tipo') == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    agendamentos = Agendamento.query.filter_by(
        cliente_id=session['usuario_id']
    ).order_by(Agendamento.data_hora.desc()).all()
    
    return render_template('cliente/dashboard.html', 
                            agendamentos=agendamentos,
                            barbeiro=BARBEIRO_INFO)


@app.route('/cliente/agendar', methods=['GET', 'POST'])
@login_required
def cliente_agendar():
    if session.get('usuario_tipo') == 'admin':
        flash('Administradores não podem fazer agendamentos', 'warning')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        servico_id = request.form.get('servico_id')
        data = request.form.get('data')
        hora = request.form.get('hora')
        observacoes = sanitizar_input(request.form.get('observacoes', ''))
        
        # Validações
        if not all([servico_id, data, hora]):
            flash('Todos os campos são obrigatórios', 'danger')
            return redirect(url_for('cliente_agendar'))
        
        try:
            servico = Servico.query.get(int(servico_id))
            if not servico or not servico.ativo:
                flash('Serviço inválido ou inativo', 'danger')
                return redirect(url_for('cliente_agendar'))
            
            data_hora = datetime.strptime(f"{data} {hora}", '%Y-%m-%d %H:%M')
            
            # Verificar se a data não é no passado
            if data_hora < datetime.now():
                flash('Não é possível agendar para datas passadas', 'danger')
                return redirect(url_for('cliente_agendar'))
            
            # Verificar se é um dia útil (segunda a sábado)
            if data_hora.weekday() == 6:  # Domingo
                flash('Não abrimos aos domingos', 'danger')
                return redirect(url_for('cliente_agendar'))
            
            # Verificar horário comercial
            hora_agendamento = data_hora.time()
            if hora_agendamento < datetime.strptime('09:00', '%H:%M').time() or \
                hora_agendamento >= datetime.strptime('19:00', '%H:%M').time():
                flash('Horário fora do expediente (9h às 19h)', 'danger')
                return redirect(url_for('cliente_agendar'))
            
        except (ValueError, TypeError):
            flash('Data ou horário inválidos', 'danger')
            return redirect(url_for('cliente_agendar'))
        
        # Verificar se horário está disponível
        agendamento_existente = Agendamento.query.filter_by(
            data_hora=data_hora,
            status='agendado'
        ).first()
        
        if agendamento_existente:
            flash('Este horário já está ocupado. Escolha outro.', 'danger')
            return redirect(url_for('cliente_agendar'))
        
        # Limitar observações
        if observacoes and len(observacoes) > 500:
            flash('Observações muito longas (máximo 500 caracteres)', 'danger')
            return redirect(url_for('cliente_agendar'))
        
        novo_agendamento = Agendamento(
            cliente_id=session['usuario_id'],
            servico_id=servico_id,
            data_hora=data_hora,
            observacoes=observacoes
        )
        
        db.session.add(novo_agendamento)
        db.session.commit()
        
        flash('Agendamento realizado com sucesso!', 'success')
        return redirect(url_for('cliente_dashboard'))
    
    servicos = Servico.query.filter_by(ativo=True).all()
    return render_template('cliente/agendar.html', 
                            servicos=servicos,
                            barbeiro=BARBEIRO_INFO)

@app.route('/meus-agendamentos')
@login_required
def meus_agendamentos():
    cliente_id = session.get('usuario_id')
    
    # Buscar agendamentos do cliente com joins
    agendamentos = Agendamento.query.filter_by(cliente_id=cliente_id)\
        .join(Agendamento.servico)\
        .order_by(Agendamento.data_hora.desc()).all()
    
    return render_template('cliente/dashboard.html',
                            agendamentos=agendamentos,
                            barbeiro=BARBEIRO_INFO)

@app.route('/cliente/agendamento/<int:id>/cancelar', methods=['POST'])
@login_required
def cliente_cancelar_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)
    
    # Verificar se o agendamento pertence ao cliente logado
    if agendamento.cliente_id != session.get('usuario_id'):
        flash('Você não tem permissão para cancelar este agendamento', 'danger')
        return redirect(url_for('meus_agendamentos'))
    
    # Verificar se pode cancelar (pelo menos 2 horas de antecedência)
    agora = datetime.now()
    diferenca = agendamento.data_hora - agora
    
    if diferenca.total_seconds() < 7200:  # 2 horas = 7200 segundos
        flash('Não é possível cancelar com menos de 2 horas de antecedência', 'warning')
        return redirect(url_for('meus_agendamentos'))
    
    # Cancelar o agendamento
    agendamento.status = 'cancelado'
    db.session.commit()
    
    flash('Agendamento cancelado com sucesso!', 'success')
    return redirect(url_for('meus_agendamentos'))

@app.route('/api/horarios-disponiveis')
@login_required
def horarios_disponiveis():
    from flask import jsonify
    
    data = request.args.get('data')
    servico_id = request.args.get('servico_id')
    
    if not data or not servico_id:
        return jsonify({'error': 'Parâmetros inválidos'}), 400
    
    try:
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        servico = Servico.query.get(int(servico_id))
        
        if not servico:
            return jsonify({'error': 'Serviço não encontrado'}), 404
        
        # Verificar se é domingo
        if data_obj.weekday() == 6:
            return jsonify({'horarios': [], 'mensagem': 'Não abrimos aos domingos'})
        
        # Verificar se é data passada
        if data_obj < datetime.now().date():
            return jsonify({'horarios': [], 'mensagem': 'Data inválida'})
        
        # Gerar horários de 9h às 19h (intervalo de 30 minutos)
        horarios = []
        hora_inicio = 9
        hora_fim = 19
        
        for hora in range(hora_inicio, hora_fim):
            for minuto in [0, 30]:
                horario = f"{hora:02d}:{minuto:02d}"
                data_hora = datetime.strptime(f"{data} {horario}", '%Y-%m-%d %H:%M')
                
                # Verificar se não é no passado
                if data_hora < datetime.now():
                    continue
                
                # Verificar se já está agendado
                agendado = Agendamento.query.filter_by(
                    data_hora=data_hora,
                    status='agendado'
                ).first()
                
                horarios.append({
                    'horario': horario,
                    'disponivel': not bool(agendado)
                })
        
        return jsonify({'horarios': horarios})
        
    except (ValueError, TypeError) as e:
        return jsonify({'error': 'Erro ao processar dados'}), 400


@app.route('/admin/agendamentos')
@admin_required
def admin_agendamentos():
    # Pegar filtros
    data_filtro = request.args.get('data')
    status_filtro = request.args.get('status')
    
    # Query base
    query = Agendamento.query
    
    # Aplicar filtros
    if data_filtro:
        try:
            data_obj = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Agendamento.data_hora) == data_obj)
        except ValueError:
            pass
    
    if status_filtro and status_filtro != 'todos':
        query = query.filter(Agendamento.status == status_filtro)
    
    # Ordenar por data
    agendamentos = query.order_by(Agendamento.data_hora.desc()).all()
    
    return render_template('admin/agendamentos.html', 
                            agendamentos=agendamentos,
                            barbeiro=BARBEIRO_INFO)

@app.route('/admin/agendamento/<int:id>/atualizar-status', methods=['POST'])
@admin_required
def atualizar_status_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)
    novo_status = request.form.get('status')
    
    if novo_status in ['agendado', 'concluido', 'cancelado']:
        agendamento.status = novo_status
        db.session.commit()
        flash(f'Status atualizado para: {novo_status}', 'success')
    else:
        flash('Status inválido', 'danger')
    
    return redirect(url_for('admin_agendamentos'))

@app.route('/admin/agendamento/<int:id>/cancelar', methods=['POST'])
@admin_required
def cancelar_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)
    agendamento.status = 'cancelado'
    db.session.commit()
    flash('Agendamento cancelado com sucesso', 'success')
    
    if session.get('usuario_tipo') == 'admin':
        return redirect(url_for('admin_agendamentos'))
    else:
        return redirect(url_for('cliente_dashboard'))

# Tratamento de erros
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    db.session.rollback()
    return render_template('500.html'), 500



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)