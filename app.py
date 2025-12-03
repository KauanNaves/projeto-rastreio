from flask import Flask, render_template
from routes.usuarios import usuarios
from routes.main import main
from routes.pedidos import pedidos

app = Flask(__name__)


app.register_blueprint(main)
app.register_blueprint(usuarios)
app.register_blueprint(pedidos)

if __name__ == "__main__":
    app.run()