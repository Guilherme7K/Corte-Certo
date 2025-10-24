from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), default='cliente')  # 'cliente' ou 'admin'
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='cliente', lazy=True)
    
    def set_senha(self, senha):
        """Define a senha do usuário com hash"""
        self.senha = generate_password_hash(senha)
    
    def verificar_senha(self, senha):
        """Verifica se a senha fornecida está correta"""
        return check_password_hash(self.senha, senha)
    
    def __repr__(self):
        return f'<Usuario {self.nome} - {self.email}>'

class Servico(db.Model):
    __tablename__ = 'servico'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    duracao = db.Column(db.Integer, nullable=False)  # em minutos
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='servico', lazy=True)
    
    def __repr__(self):
        return f'<Servico {self.nome} - R$ {self.preco}>'

class Agendamento(db.Model):
    __tablename__ = 'agendamento'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='agendado')  # 'agendado', 'concluido', 'cancelado'
    observacoes = db.Column(db.Text)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Agendamento {self.id} - Cliente: {self.cliente_id} - Data: {self.data_hora}>'

class HorarioFuncionamento(db.Model):
    __tablename__ = 'horario_funcionamento'
    
    id = db.Column(db.Integer, primary_key=True)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0=Domingo, 1=Segunda, ..., 6=Sábado
    horario_abertura = db.Column(db.String(5), nullable=False)  # Formato: "HH:MM"
    horario_fechamento = db.Column(db.String(5), nullable=False)  # Formato: "HH:MM"
    ativo = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        dias = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
        return f'<HorarioFuncionamento {dias[self.dia_semana]}: {self.horario_abertura} - {self.horario_fechamento}>'