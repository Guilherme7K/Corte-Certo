from flask import Blueprint, jsonify, request
from models import Servico, BloqueioAgenda
from utils import obter_horarios_disponiveis
from decorators import login_required
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/horarios-disponiveis', methods=['GET'])
@login_required
def horarios_disponiveis():
    data_str = request.args.get('data')
    servico_id = request.args.get('servico_id')
    
    if not data_str or not servico_id:
        return jsonify({'error': 'Parâmetros data e servico_id são obrigatórios'}), 400
    
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d')
        servico = Servico.query.get(int(servico_id))
        
        if not servico:
            return jsonify({'error': 'Serviço não encontrado'}), 404
        
        data_agendamento = data.date()
        bloqueio_ativo = BloqueioAgenda.query.filter(
            BloqueioAgenda.ativo == True,
            BloqueioAgenda.data_inicio <= data_agendamento,
            BloqueioAgenda.data_fim >= data_agendamento
        ).first()
        
        if bloqueio_ativo:
            return jsonify({'horarios': [], 'bloqueado': True, 'motivo': bloqueio_ativo.motivo})
        
        horarios = obter_horarios_disponiveis(data, servico)
        
        return jsonify({'horarios': horarios, 'bloqueado': False})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro ao processar requisição: {str(e)}'}), 500
