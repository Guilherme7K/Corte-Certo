from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Usuario
from utils import sanitizar_input, validar_email, validar_senha_forte
from decorators import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = sanitizar_input(request.form.get('email', ''))
        senha = request.form.get('senha', '')
        
        if not email or not senha:
            flash('Email e senha são obrigatórios', 'danger')
            return redirect(url_for('auth.login'))
        
        if not validar_email(email):
            flash('Email inválido', 'danger')
            return redirect(url_for('auth.login'))
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.verificar_senha(senha):
            session.clear()
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            session['usuario_tipo'] = usuario.tipo
            session.permanent = True
            
            flash('Login realizado com sucesso!', 'success')
            
            if usuario.tipo == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('cliente.cliente_dashboard'))
        else:
            flash('Email ou senha incorretos', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = sanitizar_input(request.form.get('nome', ''))
        email = sanitizar_input(request.form.get('email', ''))
        senha = request.form.get('senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')
        telefone = sanitizar_input(request.form.get('telefone', ''))
        
        # Validações
        if not all([nome, email, senha, confirmar_senha]):
            flash('Todos os campos obrigatórios devem ser preenchidos', 'danger')
            return redirect(url_for('auth.cadastro'))
        
        if len(nome) < 3:
            flash('Nome deve ter pelo menos 3 caracteres', 'danger')
            return redirect(url_for('auth.cadastro'))
        
        if not validar_email(email):
            flash('Email inválido', 'danger')
            return redirect(url_for('auth.cadastro'))
        
        if senha != confirmar_senha:
            flash('As senhas não coincidem', 'danger')
            return redirect(url_for('auth.cadastro'))
        
        valida, mensagem = validar_senha_forte(senha)
        if not valida:
            flash(mensagem, 'danger')
            return redirect(url_for('auth.cadastro'))
        
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado', 'danger')
            return redirect(url_for('auth.cadastro'))
        
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            telefone=telefone,
            tipo='cliente'
        )
        novo_usuario.set_senha(senha)
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('cadastro.html')

@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logout realizado com sucesso', 'success')
    return redirect(url_for('main.index'))
