from flask import Flask, render_template
from models import db, Usuario, Servico, HorarioFuncionamento
from datetime import datetime, date
from config import Config, BARBEIRO_INFO
from werkzeug.security import generate_password_hash
import os

from controllers.main_controller import main_bp
from controllers.auth_controller import auth_bp
from controllers.admin_controller import admin_bp
from controllers.cliente_controller import cliente_bp
from controllers.api_controller import api_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Context processor para tornar variáveis disponíveis em todos os templates
@app.context_processor
def inject_global_variables():
    return {
        'datetime': datetime,
        'date': date,
        'now': datetime.now,
        'barbeiro': BARBEIRO_INFO
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

# Registrar Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(cliente_bp)
app.register_blueprint(api_bp)

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