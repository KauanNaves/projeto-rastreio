from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import database.database as db
import random

pedidos = Blueprint('pedidos', __name__)

def gerar_token():
    """Gera um número de 6 dígitos simulando um token de rastreio"""
    return str(random.randint(100000, 999999))

# --- ROTAS ADMINISTRATIVAS (Exigem Login) ---

@pedidos.route('/novo_pedido', methods=['GET', 'POST'])
def novo_pedido():
    if 'user_id' not in session:
        return redirect(url_for('usuarios.login'))

    if request.method == 'POST':
        dados = {
            'token': gerar_token(),
            'cliente_nome': request.form.get('cliente'),
            'cliente_email': request.form.get('email'), 
            'descricao': request.form.get('descricao'),
            'prazo': request.form.get('prazo'),
            'prioridade': request.form.get('prioridade')
        }

        if not all([dados['cliente_nome'], dados['descricao']]):
             return "Erro: Nome e Descrição são obrigatórios", 400

        try:
            db.adicionar_pedido(
                dados['cliente_nome'],
                dados['cliente_email'],
                "PED-" + dados['token'][:3],
                dados['descricao'],
                "Pendente",
                dados['prioridade'],
                dados['prazo'],
                dados['token']
            )
            return redirect(url_for('main.index'))
        except Exception as e:
            return f"Erro ao salvar pedido: {e}", 500

    return render_template('novo_pedido.html')

@pedidos.route('/detalhes_pedido/<token>')
def detalhes_pedido(token):
    if 'user_id' not in session:
        return redirect(url_for('usuarios.login'))

    pedido = db.buscar_pedido(token)
    
    if not pedido:
        return "Pedido não encontrado", 404

    progresso = 10
    if pedido['status'] == 'Em andamento':
        progresso = 50
    elif pedido['status'] == 'Concluído':
        progresso = 100

    return render_template('detalhes_pedido.html', pedido=pedido, progresso=progresso)

@pedidos.route('/editar_pedido/<token>', methods=['GET', 'POST'])
def editar_pedido(token):
    if 'user_id' not in session:
        return redirect(url_for('usuarios.login'))

    pedido = db.buscar_pedido(token)
    
    if not pedido:
        return "Pedido não encontrado", 404

    if request.method == 'POST':
        cliente_nome = request.form.get('cliente')
        cliente_email = request.form.get('email')
        descricao = request.form.get('descricao')
        prazo = request.form.get('prazo')
        prioridade = request.form.get('prioridade')
        status = request.form.get('status')
        
        db.atualizar_pedido(token, cliente_nome, cliente_email, descricao, status, prioridade, prazo)
        return redirect(url_for('pedidos.detalhes_pedido', token=token))

    return render_template('editar_pedido.html', pedido=pedido)

@pedidos.route('/excluir_pedido/<token>', methods=['POST'])
def excluir_pedido(token):
    if 'user_id' not in session:
        return redirect(url_for('usuarios.login'))

    db.apagar_pedido(token)
    return redirect(url_for('main.index'))

@pedidos.route('/concluir_pedido/<token>', methods=['POST'])
def concluir_pedido(token):
    if 'user_id' not in session:
        return redirect(url_for('usuarios.login'))

    db.atualizar_status_pedido(token, 'Concluído')
    return redirect(url_for('pedidos.detalhes_pedido', token=token))


# --- ROTAS PÚBLICAS (CLIENTE - SEM LOGIN) ---

@pedidos.route('/rastreio/<token>')
def rastreio_publico(token):
    # Rota pública de visualização
    pedido = db.buscar_pedido(token)
    
    if not pedido:
        return "Pedido não encontrado", 404

    progresso = 10
    if pedido['status'] == 'Em andamento':
        progresso = 50
    elif pedido['status'] == 'Concluído':
        progresso = 100

    return render_template('rastreio_cliente.html', pedido=pedido, progresso=progresso)

@pedidos.route('/avaliar_pedido/<token>', methods=['GET', 'POST'])
def avaliar_pedido(token):
    # Rota pública de avaliação
    pedido = db.buscar_pedido(token)
    
    if not pedido:
        return "Pedido não encontrado", 404

    if request.method == 'POST':
        # Captura os dados do formulário
        nota = request.form.get('nota')
        comentario = request.form.get('comentario')
        
        # Salva no banco
        db.salvar_avaliacao_pedido(token, nota, comentario)
        
        # Redireciona de volta para o rastreio com mensagem
        return render_template('rastreio_cliente.html', pedido=pedido, progresso=100, mensagem_sucesso="Obrigado pela sua avaliação!")

    return render_template('avaliar_pedido.html', pedido=pedido)