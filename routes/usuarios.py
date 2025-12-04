from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import database.database as db

usuarios = Blueprint('usuarios', __name__)

@usuarios.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = db.buscar_usuario(email)
        
        if usuario and check_password_hash(usuario['senha_hash'], senha):
            session['user_id'] = usuario['id']
            session['user_email'] = usuario['email']
            return redirect(url_for('main.index'))
        else:
            flash('Email ou senha incorretos.')
            return redirect(url_for('usuarios.login'))
            
    return render_template('login.html')

@usuarios.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('usuarios.login'))

@usuarios.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')

        # 1. Validações Básicas
        if senha != confirmar_senha:
            flash('As senhas não conferem.')
            return redirect(url_for('usuarios.cadastro'))
        
        if len(senha) < 6:
            flash('A senha deve ter no mínimo 6 caracteres.')
            return redirect(url_for('usuarios.cadastro'))

        # 2. Verifica se usuário já existe
        usuario_existente = db.buscar_usuario(email)
        if usuario_existente:
            flash('Este email já está cadastrado.')
            return redirect(url_for('usuarios.cadastro'))

        # 3. Cria o novo usuário
        try:
            senha_hash = generate_password_hash(senha)
            db.adicionar_usuario(email, senha_hash)
            
            flash('Conta criada com sucesso! Faça login.')
            return redirect(url_for('usuarios.login'))
        except Exception as e:
            flash(f'Erro ao criar conta: {e}')
            return redirect(url_for('usuarios.cadastro'))

    return render_template('cadastro.html')