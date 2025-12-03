from flask import Blueprint, render_template, request, redirect, url_for


usuarios = Blueprint('usuarios', __name__)

@usuarios.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pass
        return redirect(url_for('usuarios.login'))
    elif request.method == 'GET':
        return render_template('login.html')
    

@usuarios.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')