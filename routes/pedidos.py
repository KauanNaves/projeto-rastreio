from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import database.database as db
import random
import json

pedidos = Blueprint('pedidos', __name__)

def gerar_token():
    return str(random.randint(100000, 999999))

@pedidos.route('/novo_pedido', methods=['GET', 'POST'])
def novo_pedido():
    if 'user_id' not in session:
        return redirect(url_for('usuarios.login'))

    if request.method == 'POST':
        produto_id = request.form.get('produto_id')
        quantidade = int(request.form.get('quantidade'))
        
        # 1. Busca o produto para validar estoque
        produto = db.buscar_produto(produto_id)
        
        if not produto:
            flash("Produto inválido.")
            return redirect(url_for('pedidos.novo_pedido'))

        # 2. Lógica de Estoque
        if produto['estoque_atual'] < quantidade:
            flash(f"Estoque insuficiente! Disponível: {produto['estoque_atual']}")
            return redirect(url_for('pedidos.novo_pedido'))

        # 3. Define a primeira etapa
        etapas = json.loads(produto['etapas_json'])
        primeira_etapa = etapas[0] if etapas else "Pendente"

        dados = {
            'token': gerar_token(),
            'produto_id': produto_id,
            'quantidade': quantidade,
            'cliente_nome': request.form.get('cliente'),
            'cliente_email': request.form.get('email'), 
            'descricao': request.form.get('descricao') or f"Pedido de {quantidade}x {produto['nome']}",
            'prazo': request.form.get('prazo'),
            'prioridade': request.form.get('prioridade'),
            'status': primeira_etapa, # Começa na primeira etapa definida
            'numero_pedido': "PED-" + str(random.randint(1000,9999))
        }

        try:
            # Salva o pedido
            db.adicionar_pedido(dados)
            
            # Baixa no Estoque
            novo_estoque = produto['estoque_atual'] - quantidade
            db.atualizar_estoque(produto_id, novo_estoque)

            flash("Pedido aprovado e estoque atualizado!")
            return redirect(url_for('main.index'))
        except Exception as e:
            return f"Erro ao salvar pedido: {e}", 500

    # GET: Precisa enviar a lista de produtos para o <select>
    produtos_disponiveis = db.listar_produtos()
    return render_template('novo_pedido.html', produtos=produtos_disponiveis)

@pedidos.route('/detalhes_pedido/<token>')
def detalhes_pedido(token):
    if 'user_id' not in session:
        return redirect(url_for('usuarios.login'))

    pedido = db.buscar_pedido(token)
    if not pedido: return "Não encontrado", 404

    # --- CORREÇÃO DE SEGURANÇA ---
    # Verifica se existem etapas antes de tentar converter o JSON
    etapas = []
    if pedido['etapas_json']:
        try:
            etapas = json.loads(pedido['etapas_json'])
        except:
            etapas = ["Erro ao carregar etapas"]
    else:
        # Se o produto foi excluído, definimos uma lista padrão para não quebrar a tela
        etapas = ["Produto Excluído / Histórico Indisponível"]

    # Lógica de Progresso Dinâmico
    total_etapas = len(etapas)
    etapa_atual_index = pedido['etapa_index']
    
    progresso = 0
    if total_etapas > 0:
        progresso = int(((etapa_atual_index + 1) / total_etapas) * 100)
        
    # Garante 100% visual se estiver concluído
    if pedido['status'] == 'Concluído': 
        progresso = 100

    return render_template('detalhes_pedido.html', pedido=pedido, progresso=progresso, etapas=etapas)


@pedidos.route('/avancar_etapa/<token>', methods=['POST'])
def avancar_etapa(token):
    if 'user_id' not in session: return redirect(url_for('usuarios.login'))
    
    pedido = db.buscar_pedido(token)
    etapas = json.loads(pedido['etapas_json'])
    index_atual = pedido['etapa_index']
    
    novo_index = index_atual + 1
    
    if novo_index < len(etapas):
        novo_status = etapas[novo_index]
        db.atualizar_progresso_pedido(token, novo_status, novo_index)
    else:
        # Chegou no fim
        db.atualizar_progresso_pedido(token, "Concluído", novo_index)
        
    return redirect(url_for('pedidos.detalhes_pedido', token=token))

@pedidos.route('/feedbacks')
def lista_feedbacks():
    if 'user_id' not in session:
        return redirect(url_for('usuarios.login'))
    
    feedbacks = db.listar_feedbacks()
    
    # Cálculo de Indicadores de Qualidade (KPIs)
    total = len(feedbacks)
    media = 0
    if total > 0:
        soma_notas = sum([f['avaliacao_nota'] for f in feedbacks])
        media = round(soma_notas / total, 1)
    
    return render_template('feedbacks.html', feedbacks=feedbacks, total=total, media=media)


@pedidos.route('/cancelar_pedido/<token>', methods=['POST'])
def cancelar_pedido_rota(token):
    if 'user_id' not in session:
        return redirect(url_for('usuarios.login'))

    # Chama a nova lógica de estorno e cancelamento
    db.cancelar_pedido(token)
    
    flash("Pedido cancelado e itens estornados ao estoque.")
    return redirect(url_for('pedidos.detalhes_pedido', token=token))


@pedidos.route('/editar_pedido/<token>', methods=['GET', 'POST'])
def editar_pedido(token):
    if 'user_id' not in session:
        return redirect(url_for('usuarios.login'))

    pedido = db.buscar_pedido(token)
    if not pedido:
        flash('Pedido não encontrado.')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        cliente = request.form.get('cliente')
        email = request.form.get('email')
        descricao = request.form.get('descricao')
        prazo = request.form.get('prazo')
        prioridade = request.form.get('prioridade')
        
        # Mantemos o status atual para não quebrar a lógica das etapas
        # Se quiser permitir mudar status manualmente, pegue do form: request.form.get('status')
        status = request.form.get('status') 

        try:
            db.atualizar_pedido(token, cliente, email, descricao, status, prioridade, prazo)
            flash('Pedido atualizado com sucesso!')
            return redirect(url_for('pedidos.detalhes_pedido', token=token))
        except Exception as e:
            flash(f"Erro ao atualizar: {e}")

    return render_template('editar_pedido.html', pedido=pedido)


# Rotas públicas (rastreio e avaliar) mantêm-se similares, 
# apenas precisam calcular o progresso igual fiz em detalhes_pedido
@pedidos.route('/rastreio/<token>')
def rastreio_publico(token):
    pedido = db.buscar_pedido(token)
    if not pedido: return "Não encontrado", 404
    
    # --- MESMA CORREÇÃO AQUI ---
    etapas = []
    if pedido['etapas_json']:
        try:
            etapas = json.loads(pedido['etapas_json'])
        except:
             etapas = []
    else:
        etapas = ["Produto não encontrado"]

    progresso = 0
    if len(etapas) > 0:
        progresso = int(((pedido['etapa_index'] + 1) / len(etapas)) * 100)
    
    if pedido['status'] == 'Concluído': 
        progresso = 100

    return render_template('rastreio_cliente.html', pedido=pedido, progresso=progresso, etapas=etapas)

@pedidos.route('/avaliar_pedido/<token>', methods=['GET', 'POST'])
def avaliar_pedido(token):
    pedido = db.buscar_pedido(token)
    if not pedido: return "Não encontrado", 404

    if request.method == 'POST':
        db.salvar_avaliacao_pedido(token, request.form.get('nota'), request.form.get('comentario'))
        return render_template('rastreio_cliente.html', pedido=pedido, progresso=100, mensagem_sucesso="Obrigado!")

    return render_template('avaliar_pedido.html', pedido=pedido)

