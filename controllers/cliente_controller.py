from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Servico, Agendamento, BloqueioAgenda
from config import BARBEIRO_INFO
from decorators import login_required
from utils import sanitizar_input
from datetime import datetime, timedelta, date

cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route('/cliente/dashboard')
@login_required
def cliente_dashboard():
    if session.get('usuario_tipo') == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    
    agendamentos = Agendamento.query.filter_by(
        cliente_id=session['usuario_id']
    ).order_by(Agendamento.data_hora.desc()).all()
    
    return render_template('cliente/dashboard.html', 
                            agendamentos=agendamentos,
                            barbeiro=BARBEIRO_INFO)

@cliente_bp.route('/cliente/agendar', methods=['GET', 'POST'])
@login_required
def cliente_agendar():
    if session.get('usuario_tipo') == 'admin':
        flash('Administradores não podem fazer agendamentos', 'warning')
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        servico_id = request.form.get('servico_id')
        data = request.form.get('data')
        hora = request.form.get('hora')
        observacoes = sanitizar_input(request.form.get('observacoes', ''))
        
        if not all([servico_id, data, hora]):
            flash('Todos os campos são obrigatórios', 'danger')
            return redirect(url_for('cliente.cliente_agendar'))
        
        try:
            servico = Servico.query.get(int(servico_id))
            if not servico or not servico.ativo:
                flash('Serviço inválido ou inativo', 'danger')
                return redirect(url_for('cliente.cliente_agendar'))
            
            data_hora = datetime.strptime(f"{data} {hora}", '%Y-%m-%d %H:%M')
            data_agendamento = data_hora.date()
            
            bloqueio_ativo = BloqueioAgenda.query.filter(
                BloqueioAgenda.ativo == True,
                BloqueioAgenda.data_inicio <= data_agendamento,
                BloqueioAgenda.data_fim >= data_agendamento
            ).first()
            
            if bloqueio_ativo:
                flash(f'Não é possível agendar nesta data. Motivo: {bloqueio_ativo.motivo}', 'danger')
                return redirect(url_for('cliente.cliente_agendar'))
            
            agora = datetime.now()
            minimo_antecedencia = agora + timedelta(minutes=30)
            
            if data_hora < minimo_antecedencia:
                flash('Não é possível agendar com menos de 30 minutos de antecedência', 'danger')
                return redirect(url_for('cliente.cliente_agendar'))
            
            if data_hora.weekday() == 6:
                flash('Não abrimos aos domingos', 'danger')
                return redirect(url_for('cliente.cliente_agendar'))
            
            hora_agendamento = data_hora.time()
            if hora_agendamento < datetime.strptime('09:00', '%H:%M').time() or \
                hora_agendamento >= datetime.strptime('19:00', '%H:%M').time():
                flash('Horário fora do expediente (9h às 19h)', 'danger')
                return redirect(url_for('cliente.cliente_agendar'))
            
        except (ValueError, TypeError):
            flash('Data ou horário inválidos', 'danger')
            return redirect(url_for('cliente.cliente_agendar'))
        
        agendamento_existente = Agendamento.query.filter_by(
            data_hora=data_hora,
            status='agendado'
        ).first()
        
        if agendamento_existente:
            flash('Este horário já está ocupado. Escolha outro.', 'danger')
            return redirect(url_for('cliente.cliente_agendar'))
        
        if observacoes and len(observacoes) > 500:
            flash('Observações muito longas (máximo 500 caracteres)', 'danger')
            return redirect(url_for('cliente.cliente_agendar'))
        
        novo_agendamento = Agendamento(
            cliente_id=session['usuario_id'],
            servico_id=servico_id,
            data_hora=data_hora,
            observacoes=observacoes
        )
        
        db.session.add(novo_agendamento)
        db.session.commit()
        
        flash('Agendamento realizado com sucesso!', 'success')
        return redirect(url_for('cliente.cliente_dashboard'))
    
    servicos = Servico.query.filter_by(ativo=True).all()
    return render_template('cliente/agendar.html', 
                            servicos=servicos,
                            today=date.today().isoformat(),
                            barbeiro=BARBEIRO_INFO)

@cliente_bp.route('/meus-agendamentos')
@login_required
def meus_agendamentos():
    cliente_id = session.get('usuario_id')
    
    agendamentos = Agendamento.query.filter_by(cliente_id=cliente_id)\
        .join(Agendamento.servico)\
        .order_by(Agendamento.data_hora.desc()).all()
    
    return render_template('cliente/dashboard.html',
                            agendamentos=agendamentos,
                            barbeiro=BARBEIRO_INFO)

@cliente_bp.route('/cliente/agendamento/<int:id>/cancelar', methods=['POST'])
@login_required
def cliente_cancelar_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)
    
    if agendamento.cliente_id != session.get('usuario_id'):
        flash('Você não tem permissão para cancelar este agendamento', 'danger')
        return redirect(url_for('cliente.meus_agendamentos'))
    
    agora = datetime.now()
    diferenca = agendamento.data_hora - agora
    
    if diferenca.total_seconds() < 7200:
        flash('Não é possível cancelar com menos de 2 horas de antecedência', 'warning')
        return redirect(url_for('cliente.meus_agendamentos'))
    
    agendamento.status = 'cancelado'
    db.session.commit()
    
    flash('Agendamento cancelado com sucesso', 'success')
    return redirect(url_for('cliente.cliente_dashboard'))

@cliente_bp.route('/cliente/agendamento/<int:id>/cancelar/confirmar', methods=['POST'])
@login_required
def confirmar_cancelamento_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)
    
    if agendamento.cliente_id != session.get('usuario_id'):
        flash('Você não tem permissão para cancelar este agendamento', 'danger')
        return redirect(url_for('cliente.meus_agendamentos'))
    
    agendamento.status = 'cancelado'
    db.session.commit()
    
    flash('Agendamento cancelado com sucesso!', 'success')
    return redirect(url_for('cliente.meus_agendamentos'))

@cliente_bp.route('/cliente/agendamento/<int:id>/excluir', methods=['POST'])
@login_required
def cliente_excluir_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)
    
    if agendamento.cliente_id != session.get('usuario_id'):
        flash('Você não tem permissão para excluir este agendamento', 'danger')
        return redirect(url_for('cliente.meus_agendamentos'))
    
    if agendamento.status not in ['concluido', 'cancelado']:
        flash('Só é possível remover agendamentos concluídos ou cancelados', 'warning')
        return redirect(url_for('cliente.meus_agendamentos'))
    
    db.session.delete(agendamento)
    db.session.commit()
    
    flash('Agendamento removido do histórico com sucesso!', 'success')
    return redirect(url_for('cliente.meus_agendamentos'))
