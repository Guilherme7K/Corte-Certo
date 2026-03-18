from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Usuario, Servico, Agendamento, HorarioFuncionamento, BloqueioAgenda
from config import BARBEIRO_INFO
from decorators import admin_required
from utils import sanitizar_input
from datetime import datetime, timedelta, date

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    hoje = datetime.now().date()
    agora = datetime.now()
    
    agendamentos_hoje = Agendamento.query.filter(
        db.func.date(Agendamento.data_hora) == hoje
    ).order_by(Agendamento.data_hora).all()
    
    total_agendamentos = Agendamento.query.count()
    total_clientes = Usuario.query.filter_by(tipo='cliente').count()
    
    agendamentos_mes = Agendamento.query.filter(
        db.extract('year', Agendamento.data_hora) == agora.year,
        db.extract('month', Agendamento.data_hora) == agora.month
    ).count()
    
    agendados_hoje = Agendamento.query.filter(
        db.func.date(Agendamento.data_hora) == hoje,
        Agendamento.status == 'agendado'
    ).count()
    
    concluidos_hoje = Agendamento.query.filter(
        db.func.date(Agendamento.data_hora) == hoje,
        Agendamento.status == 'concluido'
    ).count()
    
    agendamentos_hoje_obj = Agendamento.query.filter(
        db.func.date(Agendamento.data_hora) == hoje
    ).join(Agendamento.servico).all()
    
    receita_hoje = sum(ag.servico.preco for ag in agendamentos_hoje_obj if ag.status != 'cancelado')
    
    servicos_populares = db.session.query(
        Servico.nome,
        db.func.count(Agendamento.id).label('total')
    ).join(Agendamento).group_by(Servico.id).order_by(db.text('total DESC')).limit(5).all()
    
    proximos_agendamentos = Agendamento.query.filter(
        Agendamento.data_hora >= agora,
        Agendamento.data_hora <= agora + timedelta(hours=3),
        Agendamento.status == 'agendado'
    ).order_by(Agendamento.data_hora).all()
    
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

@admin_bp.route('/agendamento/<int:id>/concluir', methods=['POST'])
@admin_required
def concluir_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)
    
    if agendamento.status != 'agendado':
        flash('Apenas agendamentos com status "agendado" podem ser concluídos', 'warning')
        return redirect(url_for('admin.admin_agendamentos'))
    
    agendamento.status = 'concluido'
    db.session.commit()
    
    flash('Agendamento marcado como concluído!', 'success')
    return redirect(url_for('admin.admin_agendamentos'))

@admin_bp.route('/servicos', methods=['GET', 'POST'])
@admin_required
def admin_servicos():
    if request.method == 'POST':
        nome = sanitizar_input(request.form.get('nome', ''))
        descricao = sanitizar_input(request.form.get('descricao', ''))
        preco_str = request.form.get('preco', '0')
        duracao_str = request.form.get('duracao', '0')
        
        try:
            preco = float(preco_str)
            duracao = int(duracao_str)
            
            if preco <= 0:
                flash('Preço deve ser maior que zero', 'danger')
                return redirect(url_for('admin.admin_servicos'))
            
            if duracao <= 0 or duracao > 480:
                flash('Duração deve ser entre 1 e 480 minutos', 'danger')
                return redirect(url_for('admin.admin_servicos'))
            
        except ValueError:
            flash('Preço e duração devem ser números válidos', 'danger')
            return redirect(url_for('admin.admin_servicos'))
        
        if not nome or len(nome) < 3:
            flash('Nome do serviço deve ter pelo menos 3 caracteres', 'danger')
            return redirect(url_for('admin.admin_servicos'))
        
        novo_servico = Servico(
            nome=nome,
            descricao=descricao,
            preco=preco,
            duracao=duracao
        )
        
        db.session.add(novo_servico)
        db.session.commit()
        
        flash('Serviço cadastrado com sucesso!', 'success')
        return redirect(url_for('admin.admin_servicos'))
    
    servicos = Servico.query.all()
    return render_template('admin/servicos.html', servicos=servicos)

@admin_bp.route('/servicos/editar/<int:servico_id>', methods=['POST'])
@admin_required
def editar_servico(servico_id):
    servico = Servico.query.get_or_404(servico_id)
    
    nome = sanitizar_input(request.form.get('nome', ''))
    descricao = sanitizar_input(request.form.get('descricao', ''))
    preco_str = request.form.get('preco', '0')
    duracao_str = request.form.get('duracao', '0')
    ativo_str = request.form.get('ativo', '1')
    
    try:
        preco = float(preco_str)
        duracao = int(duracao_str)
        ativo = bool(int(ativo_str))
        
        if preco <= 0:
            flash('Preço deve ser maior que zero', 'danger')
            return redirect(url_for('admin.admin_servicos'))
        
        if duracao <= 0 or duracao > 480:
            flash('Duração deve ser entre 1 e 480 minutos', 'danger')
            return redirect(url_for('admin.admin_servicos'))
            
    except ValueError:
        flash('Preço e duração devem ser números válidos', 'danger')
        return redirect(url_for('admin.admin_servicos'))
    
    if not nome or len(nome) < 3:
        flash('Nome do serviço deve ter pelo menos 3 caracteres', 'danger')
        return redirect(url_for('admin.admin_servicos'))
    
    servico.nome = nome
    servico.descricao = descricao
    servico.preco = preco
    servico.duracao = duracao
    servico.ativo = ativo
    
    db.session.commit()
    
    flash('Serviço atualizado com sucesso!', 'success')
    return redirect(url_for('admin.admin_servicos'))

@admin_bp.route('/agendamentos')
@admin_required
def admin_agendamentos():
    data_filtro = request.args.get('data')
    status_filtro = request.args.get('status')
    
    query = Agendamento.query
    
    if data_filtro:
        try:
            data_obj = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Agendamento.data_hora) == data_obj)
        except ValueError:
            pass
    
    if status_filtro and status_filtro != 'todos':
        query = query.filter(Agendamento.status == status_filtro)
    
    agendamentos = query.order_by(Agendamento.data_hora.desc()).all()
    
    return render_template('admin/agendamentos.html', 
                            agendamentos=agendamentos,
                            barbeiro=BARBEIRO_INFO)

@admin_bp.route('/agendamento/<int:id>/atualizar-status', methods=['POST'])
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
    
    return redirect(url_for('admin.admin_agendamentos'))

@admin_bp.route('/agendamento/<int:id>/cancelar', methods=['POST'])
@admin_required
def cancelar_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)
    agendamento.status = 'cancelado'
    db.session.commit()
    flash('Agendamento cancelado com sucesso', 'success')
    
    if session.get('usuario_tipo') == 'admin':
        return redirect(url_for('admin.admin_agendamentos'))
    else:
        return redirect(url_for('cliente.cliente_dashboard'))

@admin_bp.route('/bloqueios')
@admin_required
def admin_bloqueios():
    try:
        bloqueios = BloqueioAgenda.query.order_by(BloqueioAgenda.data_inicio.desc()).all()
        return render_template('admin/bloqueios.html', bloqueios=bloqueios, barbeiro=BARBEIRO_INFO)
    except Exception as e:
        flash('Erro ao carregar bloqueios.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/bloqueios/novo', methods=['GET', 'POST'])
@admin_required
def novo_bloqueio():
    if request.method == 'POST':
        data_inicio_str = request.form.get('data_inicio')
        data_fim_str = request.form.get('data_fim')
        motivo = request.form.get('motivo', '').strip()
        
        if not data_inicio_str or not data_fim_str:
            flash('Data de início e fim são obrigatórias', 'danger')
            return redirect(url_for('admin.novo_bloqueio'))
        
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            
            if data_fim < data_inicio:
                flash('Data final deve ser maior ou igual à data inicial', 'danger')
                return redirect(url_for('admin.novo_bloqueio'))
            
            if data_inicio < date.today():
                flash('Não é possível bloquear datas passadas', 'danger')
                return redirect(url_for('admin.novo_bloqueio'))
            
            diferenca_dias = (data_fim - data_inicio).days
            if diferenca_dias > 90:
                flash('Período máximo de bloqueio é 90 dias', 'danger')
                return redirect(url_for('admin.novo_bloqueio'))
            
            conflito = BloqueioAgenda.query.filter(
                BloqueioAgenda.ativo == True,
                db.or_(
                    db.and_(
                        BloqueioAgenda.data_inicio <= data_inicio,
                        BloqueioAgenda.data_fim >= data_inicio
                    ),
                    db.and_(
                        BloqueioAgenda.data_inicio <= data_fim,
                        BloqueioAgenda.data_fim >= data_fim
                    ),
                    db.and_(
                        BloqueioAgenda.data_inicio >= data_inicio,
                        BloqueioAgenda.data_fim <= data_fim
                    )
                )
            ).first()
            
            if conflito:
                flash(f'Já existe um bloqueio ativo entre {conflito.data_inicio.strftime("%d/%m/%Y")} e {conflito.data_fim.strftime("%d/%m/%Y")}', 'warning')
                return redirect(url_for('admin.novo_bloqueio'))
            
        except ValueError:
            flash('Formato de data inválido', 'danger')
            return redirect(url_for('admin.novo_bloqueio'))
        
        novo_bloqueio_obj = BloqueioAgenda(
            data_inicio=data_inicio,
            data_fim=data_fim,
            motivo=motivo if motivo else 'Sem motivo especificado',
            criado_por=session['usuario_id']
        )
        
        db.session.add(novo_bloqueio_obj)
        db.session.commit()
        
        agendamentos_afetados = Agendamento.query.filter(
            db.func.date(Agendamento.data_hora) >= data_inicio,
            db.func.date(Agendamento.data_hora) <= data_fim,
            Agendamento.status == 'agendado'
        ).all()
        
        for agendamento in agendamentos_afetados:
            agendamento.status = 'cancelado'
            agendamento.observacoes = f"Cancelado automaticamente - {motivo}"
        
        db.session.commit()
        
        if agendamentos_afetados:
            flash(f'Bloqueio criado! {len(agendamentos_afetados)} agendamento(s) cancelados.', 'success')
        else:
            flash('Bloqueio criado com sucesso!', 'success')
        
        return redirect(url_for('admin.admin_bloqueios'))
    
    return render_template('admin/novo_bloqueio.html', barbeiro=BARBEIRO_INFO)

@admin_bp.route('/bloqueios/<int:id>/desativar', methods=['POST'])
@admin_required
def desativar_bloqueio(id):
    bloqueio = BloqueioAgenda.query.get_or_404(id)
    bloqueio.ativo = False
    db.session.commit()
    flash('Bloqueio desativado com sucesso!', 'success')
    return redirect(url_for('admin.admin_bloqueios'))

@admin_bp.route('/bloqueios/<int:id>/deletar', methods=['POST'])
@admin_required
def deletar_bloqueio(id):
    bloqueio = BloqueioAgenda.query.get_or_404(id)
    db.session.delete(bloqueio)
    db.session.commit()
    flash('Bloqueio deletado com sucesso!', 'success')
    return redirect(url_for('admin.admin_bloqueios'))
