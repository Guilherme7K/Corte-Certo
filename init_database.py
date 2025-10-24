from app import app, db
from models import Usuario, Servico, HorarioFuncionamento
from werkzeug.security import generate_password_hash

def init_database():
    """Inicializa o banco de dados com tabelas e dados padrão"""
    with app.app_context():
        print("🔄 Criando tabelas no banco de dados...")
        
        # Criar todas as tabelas
        db.create_all()
        print("✅ Tabelas criadas!")
        
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
        else:
            print("ℹ️  Usuário admin já existe")
        
        # Verificar se já existem serviços
        if Servico.query.count() == 0:
            servicos_padrao = [
                Servico(
                    nome='Corte de Cabelo',
                    descricao='Corte masculino tradicional ou moderno',
                    preco=35.00,
                    duracao=30,
                    ativo=True
                ),
                Servico(
                    nome='Barba',
                    descricao='Aparar e modelar barba',
                    preco=25.00,
                    duracao=20,
                    ativo=True
                ),
                Servico(
                    nome='Corte + Barba',
                    descricao='Combo completo de corte e barba',
                    preco=50.00,
                    duracao=45,
                    ativo=True
                ),
                Servico(
                    nome='Sobrancelha',
                    descricao='Design de sobrancelha masculina',
                    preco=15.00,
                    duracao=15,
                    ativo=True
                ),
                Servico(
                    nome='Hidratação',
                    descricao='Tratamento capilar com hidratação profunda',
                    preco=40.00,
                    duracao=30,
                    ativo=True
                ),
                Servico(
                    nome='Acabamento',
                    descricao='Finalização com máquina e navalha',
                    preco=20.00,
                    duracao=15,
                    ativo=True
                ),
            ]
            db.session.add_all(servicos_padrao)
            print("✅ Serviços padrão criados!")
        else:
            print(f"ℹ️  Já existem {Servico.query.count()} serviços cadastrados")
        
        # Verificar se já existem horários de funcionamento
        if HorarioFuncionamento.query.count() == 0:
            horarios = [
                HorarioFuncionamento(dia_semana=1, horario_abertura='09:00', horario_fechamento='19:00', ativo=True),  # Segunda
                HorarioFuncionamento(dia_semana=2, horario_abertura='09:00', horario_fechamento='19:00', ativo=True),  # Terça
                HorarioFuncionamento(dia_semana=3, horario_abertura='09:00', horario_fechamento='19:00', ativo=True),  # Quarta
                HorarioFuncionamento(dia_semana=4, horario_abertura='09:00', horario_fechamento='19:00', ativo=True),  # Quinta
                HorarioFuncionamento(dia_semana=5, horario_abertura='09:00', horario_fechamento='19:00', ativo=True),  # Sexta
                HorarioFuncionamento(dia_semana=6, horario_abertura='09:00', horario_fechamento='17:00', ativo=True),  # Sábado
                HorarioFuncionamento(dia_semana=0, horario_abertura='09:00', horario_fechamento='13:00', ativo=False), # Domingo (fechado)
            ]
            db.session.add_all(horarios)
            print("✅ Horários de funcionamento criados!")
        else:
            print(f"ℹ️  Já existem {HorarioFuncionamento.query.count()} horários cadastrados")
        
        # Salvar tudo
        db.session.commit()
        print("✅ Banco de dados inicializado com sucesso!")
        print("\n📊 Resumo:")
        print(f"   - Usuários: {Usuario.query.count()}")
        print(f"   - Serviços: {Servico.query.count()}")
        print(f"   - Horários: {HorarioFuncionamento.query.count()}")
        print("\n🔐 Credenciais Admin:")
        print("   Email: admin@cortecerto.com")
        print("   Senha: admin123")

if __name__ == '__main__':
    init_database()