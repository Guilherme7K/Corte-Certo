from datetime import datetime, timedelta
from models import db, Agendamento, HorarioFuncionamento
from sqlalchemy import and_, or_, extract

def obter_horarios_disponiveis(data, servico):
    """
    Retorna os horários disponíveis para um serviço em uma data específica
    Compatível com PostgreSQL e SQLite
    """
    # Calcular tempo mínimo de antecedência (agora + 30 minutos)
    agora = datetime.now()
    minimo_antecedencia = agora + timedelta(minutes=30)
    
    # Obter dia da semana (0=Domingo, 6=Sábado)
    dia_semana = data.weekday()
    if dia_semana == 6:  # Domingo
        dia_semana = 0
    else:
        dia_semana += 1
    
    # Buscar horário de funcionamento
    horario_func = HorarioFuncionamento.query.filter_by(
        dia_semana=dia_semana,
        ativo=True
    ).first()
    
    if not horario_func:
        return []
    
    # Converter horários de string para datetime
    abertura_str = horario_func.horario_abertura  # "09:00"
    fechamento_str = horario_func.horario_fechamento  # "19:00"
    
    hora_abertura, min_abertura = map(int, abertura_str.split(':'))
    hora_fechamento, min_fechamento = map(int, fechamento_str.split(':'))
    
    inicio = datetime.combine(data.date(), datetime.min.time().replace(hour=hora_abertura, minute=min_abertura))
    fim = datetime.combine(data.date(), datetime.min.time().replace(hour=hora_fechamento, minute=min_fechamento))
    
    # Gerar horários disponíveis a cada 30 minutos
    horarios_disponiveis = []
    horario_atual = inicio
    
    while horario_atual + timedelta(minutes=servico.duracao) <= fim:
        # Verificar se o horário está no futuro com no mínimo 30 minutos de antecedência
        if horario_atual < minimo_antecedencia:
            horario_atual += timedelta(minutes=30)
            continue
        
        # Verificar se já existe agendamento nesse horário
        agendamento_existente = Agendamento.query.filter(
            and_(
                Agendamento.data_hora >= horario_atual,
                Agendamento.data_hora < horario_atual + timedelta(minutes=servico.duracao),
                Agendamento.status.in_(['agendado', 'confirmado'])
            )
        ).first()
        
        if not agendamento_existente:
            horarios_disponiveis.append(horario_atual.strftime('%H:%M'))
        
        horario_atual += timedelta(minutes=30)
    
    return horarios_disponiveis

def obter_agendamentos_por_periodo(data_inicio, data_fim):
    """
    Retorna agendamentos em um período específico
    Compatível com PostgreSQL e SQLite
    """
    return Agendamento.query.filter(
        and_(
            Agendamento.data_hora >= data_inicio,
            Agendamento.data_hora <= data_fim
        )
    ).order_by(Agendamento.data_hora).all()

def obter_agendamentos_do_mes(ano, mes):
    """
    Retorna agendamentos de um mês específico
    Compatível com PostgreSQL e SQLite
    """
    return Agendamento.query.filter(
        extract('year', Agendamento.data_hora) == ano,
        extract('month', Agendamento.data_hora) == mes
    ).order_by(Agendamento.data_hora).all()

def calcular_receita_periodo(data_inicio, data_fim, status='concluido'):
    """
    Calcula a receita total de um período
    """
    agendamentos = Agendamento.query.filter(
        and_(
            Agendamento.data_hora >= data_inicio,
            Agendamento.data_hora <= data_fim,
            Agendamento.status == status
        )
    ).all()
    
    return sum([ag.servico.preco for ag in agendamentos if ag.servico])