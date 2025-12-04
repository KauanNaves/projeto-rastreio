from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import database.database as db
import json

produtos_bp = Blueprint('produtos', __name__)

@produtos_bp.route('/produtos')
def lista():
    if 'user_id' not in session:
        return redirect(url_for('usuarios.login'))
    
    lista = db.listar_produtos()
    # Vamos processar o JSON das etapas para exibir bonitinho
    produtos_formatados = []
    for p in lista:
        p_dict = dict(p)
        try:
            p_dict['etapas'] = json.loads(p['etapas_json'])
        except:
            p_dict['etapas'] = []
        produtos_formatados.append(p_dict)

    return render_template('produtos.html', produtos=produtos_formatados)


@produtos_bp.route('/novo_produto', methods=['GET', 'POST'])
def novo_produto():
    if 'user_id' not in session:
        return redirect(url_for('usuarios.login'))

    if request.method == 'POST':
        nome = request.form.get('nome')
        estoque = request.form.get('estoque')
        
        # Captura as etapas. Vamos supor que o usuário digite separado por vírgula
        # Ex: "Corte, Pintura, Acabamento"
        etapas_raw = request.form.get('etapas') 
        
        if not nome or not estoque or not etapas_raw:
            flash("Todos os campos são obrigatórios")
            return redirect(url_for('produtos.novo_produto'))

        # Tratamento das etapas
        lista_etapas = [e.strip() for e in etapas_raw.split(',') if e.strip()]
        
        if not lista_etapas:
            flash("Adicione pelo menos uma etapa de produção.")
            return redirect(url_for('produtos.novo_produto'))

        try:
            db.adicionar_produto(nome, int(estoque), lista_etapas)
            flash("Produto cadastrado com sucesso!")
            return redirect(url_for('produtos.lista'))
        except Exception as e:
            flash(f"Erro ao salvar: {e}")
    
    return render_template('novo_produto.html')


@produtos_bp.route('/editar_produto/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    if 'user_id' not in session:
        return redirect(url_for('usuarios.login'))

    produto = db.buscar_produto(id)
    if not produto:
        flash("Produto não encontrado.")
        return redirect(url_for('produtos.lista'))

    if request.method == 'POST':
        nome = request.form.get('nome')
        estoque = request.form.get('estoque')
        etapas_raw = request.form.get('etapas')

        if not nome or not estoque or not etapas_raw:
            flash("Todos os campos são obrigatórios.")
            return redirect(url_for('produtos.editar_produto', id=id))

        # Processa as etapas de String para Lista
        lista_etapas = [e.strip() for e in etapas_raw.split(',') if e.strip()]

        try:
            db.atualizar_produto(id, nome, int(estoque), lista_etapas)
            flash("Produto atualizado com sucesso!")
            return redirect(url_for('produtos.lista'))
        except Exception as e:
            flash(f"Erro ao atualizar: {e}")

    # --- Lógica do GET (Preparar formulário) ---
    # Precisamos converter o JSON do banco de volta para Texto (separado por vírgula)
    # para que o usuário possa editar na textarea.
    try:
        etapas_lista = json.loads(produto['etapas_json'])
        etapas_texto = ", ".join(etapas_lista)
    except:
        etapas_texto = ""

    return render_template('editar_produto.html', produto=produto, etapas_texto=etapas_texto)


@produtos_bp.route('/excluir_produto/<int:id>', methods=['POST'])
def excluir_produto_rota(id):
    if 'user_id' not in session:
        return redirect(url_for('usuarios.login'))

    sucesso, mensagem = db.excluir_produto(id)
    
    if sucesso:
        flash(mensagem) # Mensagem padrão (info/sucesso)
    else:
        # Precisamos de uma categoria diferente para erro? 
        # O base.html atual mostra tudo como 'alert-info', mas funciona.
        flash(f"ERRO: {mensagem}") 
        
    return redirect(url_for('produtos.lista'))

