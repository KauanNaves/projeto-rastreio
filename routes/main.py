from flask import Blueprint, render_template, session, redirect, url_for
import database.database as db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # --- BLINDAGEM DE ROTA ---
    # Verifica se o usuário tem uma sessão ativa (se fez login)
    if 'user_id' not in session:
        return redirect(url_for('usuarios.login'))

    # Se passou pela segurança, executa a lógica normal:
    pedidos = db.listar_pedidos()
    return render_template('index.html', pedidos=pedidos)
@main.route('/sobre')
def sobre():  
    return render_template('sobre.html')    