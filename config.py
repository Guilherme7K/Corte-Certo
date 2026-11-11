import os
from dotenv import load_dotenv
from sqlalchemy.pool import NullPool

load_dotenv()

class Config:
    NOME_EMPRESA = "Corte Certo"
    EMAIL_CONTATO = "contato@cortecerto.com.br"
    TELEFONE = "(11) 98765-4321"
    ENDERECO = "Rua Principal, 123 - Centro"
    
    LINK_WHATSAPP = 'https://wa.me/5511987654321'
    LINK_INSTAGRAM = 'https://www.instagram.com/cortecerto/'
    LINK_FACEBOOK = 'https://www.facebook.com/cortecerto/'
    
    # Na Vercel a variável VERCEL é definida automaticamente
    EM_PRODUCAO = bool(os.environ.get('VERCEL')) or os.environ.get('FLASK_ENV') == 'production'

    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        if EM_PRODUCAO:
            raise RuntimeError('Defina a variável de ambiente SECRET_KEY')
        SECRET_KEY = 'chave-apenas-para-desenvolvimento'

    DATABASE_URL = os.environ.get('DATABASE_URL')

    # Usa explicitamente o driver psycopg2 (o SQLAlchemy 2.1 passou a usar psycopg 3 por padrão)
    if DATABASE_URL:
        for prefixo in ('postgres://', 'postgresql://'):
            if DATABASE_URL.startswith(prefixo):
                DATABASE_URL = 'postgresql+psycopg2://' + DATABASE_URL[len(prefixo):]

    if not DATABASE_URL and EM_PRODUCAO:
        raise RuntimeError('Defina a variável de ambiente DATABASE_URL')

    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///barbearia.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if DATABASE_URL:
        # Em ambiente serverless cada instância é efêmera: o pooler do Supabase
        # (porta 6543) gerencia as conexões, então o app não mantém um pool próprio
        SQLALCHEMY_ENGINE_OPTIONS = {
            'poolclass': NullPool,
            'connect_args': {
                'connect_timeout': 10,
                'application_name': 'corte_certo',
            },
        }

    SESSION_COOKIE_SECURE = EM_PRODUCAO
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Email (opcional - para notificações)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

BARBEIRO_INFO = {
    'nome': 'João Silva',
    'barbearia': Config.NOME_EMPRESA,
    'endereco': Config.ENDERECO,
    'telefone': Config.TELEFONE,
    'email': Config.EMAIL_CONTATO
}