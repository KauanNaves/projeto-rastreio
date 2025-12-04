from flask import Flask, render_template
from livereload import Server
from routes.usuarios import usuarios
from routes.main import main
from routes.pedidos import pedidos
import os
import database.database as db

app = Flask(__name__)

# Configuração para que o Flask saiba que deve atualizar os templates
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.secret_key = 'senai_qualidade_dev_secret_key'

app.register_blueprint(main)
app.register_blueprint(usuarios)
app.register_blueprint(pedidos)

if not os.path.exists('database.db'):
    with app.app_context():
        db.criar_tabelas()
        print("Banco de dados inicializado com sucesso!")

if __name__ == "__main__":
    # Cria o servidor Livereload conectando ao seu app Flask
    server = Server(app.wsgi_app)

    # Diz ao servidor para vigiar todos os arquivos HTML na pasta templates
    server.watch("templates/*.html")
    server.watch("static/*.css")
    server.watch("static/*.js")
    server.watch("static/*.png")
    server.watch("static/*.ico")
    server.watch("static/*.svg")
    server.watch("routes/*.py")
    # Se você tiver CSS ou JS, pode adicionar assim (opcional):
    # server.watch("static/*.css")
    # server.watch("static/*.js")

    # Inicia o servidor disponível na rede (0.0.0.0) na porta 5000
    server.serve(host="0.0.0.0", port=5000, debug=True)