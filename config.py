import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NOME_EMPRESA = "Corte Certo"
    EMAIL_CONTATO = "contato@cortecerto.com.br"
    TELEFONE = "(11) 98765-4321"
    ENDERECO = "Rua Principal, 123 - Centro"
    
    LINK_WHATSAPP = 'https://wa.me/5511987654321'
    LINK_INSTAGRAM = 'https://www.instagram.com/cortecerto/'
    LINK_FACEBOOK = 'https://www.facebook.com/cortecerto/'
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-super-segura-aqui'
    
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///barbearia.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações otimizadas para Supabase
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
        'pool_size': 2,  # Reduzido para Render free
        'max_overflow': 1,
        'pool_timeout': 30,
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'corte_certo_render',
        }
    }
    
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Email (opcional - para notificações)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')