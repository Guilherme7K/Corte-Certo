import secrets
from datetime import datetime, timedelta

from models import db, Usuario, Servico, Agendamento

EMAIL_CLIENTE_DEMO = 'demo@cortecerto.com'
EMAIL_ADMIN_DEMO = 'admin@cortecerto.com'


def _proximo_dia_util(base, dias):
    """Data daqui a `dias` dias, pulando o domingo (barbearia fechada)."""
    data = base + timedelta(days=dias)
    if data.weekday() == 6:
        data += timedelta(days=1)
    return data


def obter_cliente_demo():
    """Retorna o cliente de demonstração, criando-o com um histórico de exemplo."""
    cliente = Usuario.query.filter_by(email=EMAIL_CLIENTE_DEMO).first()
    if not cliente:
        cliente = Usuario(
            nome='Cliente Demonstração',
            email=EMAIL_CLIENTE_DEMO,
            telefone='11912345678',
            tipo='cliente',
        )
        # Senha aleatória: a conta só é acessada pelo botão de demonstração
        cliente.set_senha(secrets.token_urlsafe(32))
        db.session.add(cliente)
        db.session.flush()

    if not Agendamento.query.filter_by(cliente_id=cliente.id).first():
        servicos = Servico.query.filter_by(ativo=True).order_by(Servico.id).all()
        if servicos:
            hoje = datetime.now().replace(minute=0, second=0, microsecond=0)
            exemplos = [
                (_proximo_dia_util(hoje, 2).replace(hour=10), 'agendado', 'Agendamento de exemplo'),
                (_proximo_dia_util(hoje, -7).replace(hour=15), 'concluido', None),
                (_proximo_dia_util(hoje, -21).replace(hour=11), 'concluido', None),
            ]
            for i, (data_hora, status, observacoes) in enumerate(exemplos):
                db.session.add(Agendamento(
                    cliente_id=cliente.id,
                    servico_id=servicos[i % len(servicos)].id,
                    data_hora=data_hora,
                    status=status,
                    observacoes=observacoes,
                ))

    db.session.commit()
    return cliente


def obter_admin_demo():
    """Garante que o cliente demo exista (para o painel ter dados) e retorna o admin."""
    obter_cliente_demo()
    return Usuario.query.filter_by(email=EMAIL_ADMIN_DEMO, tipo='admin').first()
