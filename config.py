import os

class Config:
    # Principais Dados da Barbearia
    NOME_EMPRESA = "Corte Certo"
    EMAIL_CONTATO = "contato@cortecerto.com.br"
    TELEFONE = "(11) 98765-4321"
    ENDERECO = "Rua Principal, 123 - Centro"
    
    # URLs e Links Sociais
    LINK_WHATSAPP = 'https://wa.me/5511987654321'
    LINK_INSTAGRAM = 'https://www.instagram.com/cortecerto/'
    LINK_FACEBOOK = 'https://www.facebook.com/cortecerto/'
    
    # Configurações do Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-super-segura-aqui'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///barbearia.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Segurança
    SESSION_COOKIE_SECURE = True  # True em produção
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Email (opcional - para notificações)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')