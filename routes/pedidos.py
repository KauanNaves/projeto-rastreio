from flask import Blueprint, render_template, request, redirect, url_for

pedidos = Blueprint('pedidos', __name__)

@pedidos.route('/novo_pedido', methods=['GET'])
def novo_pedido_template():
    return render_template('novo_pedido.html')

@pedidos.route('/novo_pedido', methods=['POST'])
def novo_pedido():
    return render_template('novo_pedido.html')

@pedidos.route('/detalhes_pedido')
def detalhes_pedido():
    return render_template('detalhes_pedido.html')

@pedidos.route('/avaliar_pedido')
def avaliar_pedido():
    return render_template('avaliar_pedido.html')