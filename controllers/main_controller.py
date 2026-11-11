from flask import Blueprint, render_template, jsonify
from sqlalchemy import text
from models import db
from config import BARBEIRO_INFO

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html', barbeiro=BARBEIRO_INFO)

@main_bp.route('/saude')
def saude():
    """Verifica a conexão com o banco. Chamada diariamente pelo cron da Vercel,
    o que também impede o Supabase gratuito de pausar o projeto por inatividade."""
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify(status='ok', banco='ok')
    except Exception:
        db.session.rollback()
        return jsonify(status='erro', banco='indisponivel'), 503
