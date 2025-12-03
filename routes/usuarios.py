from flask import Blueprint, render_template


usuarios = Blueprint('usuarios', __name__)

@usuarios.route('/login')
def login():
    return render_template('login.html')


@usuarios.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')