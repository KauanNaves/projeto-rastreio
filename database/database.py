import sqlite3
import json  # Necessário para salvar as etapas como lista

def criar_conexao():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row 
    return conn

def criar_tabelas():
    conn = criar_conexao()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            senha_hash TEXT NOT NULL
        )
    """)

    # NOVO: Tabela de Produtos
    # etapas_json vai guardar algo como: ["Corte", "Solda", "Pintura"]
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            estoque_atual INTEGER NOT NULL DEFAULT 0,
            etapas_json TEXT NOT NULL
        )
    """)

    # ALTERADO: Pedidos agora se ligam a um produto
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            quantidade INTEGER NOT NULL DEFAULT 1,
            cliente_nome TEXT NOT NULL,
            cliente_email TEXT,
            numero_pedido TEXT NOT NULL,
            descricao TEXT, -- Agora é opcional, pois o produto já tem nome
            
            status TEXT NOT NULL,       -- Vai guardar o nome da etapa atual (ex: "Solda")
            etapa_index INTEGER DEFAULT 0, -- Qual o índice da etapa atual (0, 1, 2...)
            
            prioridade TEXT,
            prazo_entrega TEXT,
            token_rastreio TEXT NOT NULL UNIQUE,
            avaliacao_nota INTEGER, 
            avaliacao_obs TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_qualidade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            etapa_nome TEXT NOT NULL,
            aprovado BOOLEAN NOT NULL,
            observacoes TEXT,
            FOREIGN KEY (pedido_id) REFERENCES pedidos (id)
        )
    """)

    conn.commit()
    conn.close()

# --- Funções de Usuário ---
def adicionar_usuario(email, senha_hash):
    conn = criar_conexao()
    conn.execute("INSERT INTO usuarios (email, senha_hash) VALUES (?, ?)", (email, senha_hash))
    conn.commit()
    conn.close()

def buscar_usuario(email):
    conn = criar_conexao()
    usuario = conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    conn.close()
    return usuario

# --- NOVAS Funções de Produtos ---
def adicionar_produto(nome, estoque, lista_etapas):
    # Converte a lista de etapas ["Corte", "Solda"] para texto '["Corte", "Solda"]'
    etapas_str = json.dumps(lista_etapas)
    conn = criar_conexao()
    conn.execute("INSERT INTO produtos (nome, estoque_atual, etapas_json) VALUES (?, ?, ?)", 
                 (nome, estoque, etapas_str))
    conn.commit()
    conn.close()

def listar_produtos():
    conn = criar_conexao()
    produtos = conn.execute("SELECT * FROM produtos").fetchall()
    conn.close()
    return produtos

def buscar_produto(id):
    conn = criar_conexao()
    produto = conn.execute("SELECT * FROM produtos WHERE id = ?", (id,)).fetchone()
    conn.close()
    return produto

def atualizar_estoque(produto_id, nova_qtd):
    conn = criar_conexao()
    conn.execute("UPDATE produtos SET estoque_atual = ? WHERE id = ?", (nova_qtd, produto_id))
    conn.commit()
    conn.close()

# --- Funções de Pedidos (Adaptadas) ---
def adicionar_pedido(dados):
    conn = criar_conexao()
    conn.execute("""
        INSERT INTO pedidos (
            produto_id, quantidade, cliente_nome, cliente_email, 
            numero_pedido, descricao, status, etapa_index,
            prioridade, prazo_entrega, token_rastreio
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dados['produto_id'], 
        dados['quantidade'], 
        dados['cliente_nome'], 
        dados['cliente_email'], 
        dados['numero_pedido'], 
        dados['descricao'],
        dados['status'], 
        0, 
        dados['prioridade'], 
        dados['prazo'],  # Confirme se aqui está 'prazo'
        dados['token']   # <--- AQUI ERA O ERRO: Mudamos de 'token_rastreio' para 'token'
    ))
    conn.commit()
    conn.close()


def listar_pedidos():
    conn = criar_conexao()
    # Fazemos um JOIN para pegar o nome do produto junto com o pedido
    query = """
        SELECT pedidos.*, produtos.nome as produto_nome, produtos.etapas_json 
        FROM pedidos 
        LEFT JOIN produtos ON pedidos.produto_id = produtos.id
        ORDER BY pedidos.id DESC
    """
    pedidos = conn.execute(query).fetchall()
    conn.close()
    return pedidos

def buscar_pedido(token):
    conn = criar_conexao()
    query = """
        SELECT pedidos.*, produtos.nome as produto_nome, produtos.etapas_json 
        FROM pedidos 
        LEFT JOIN produtos ON pedidos.produto_id = produtos.id
        WHERE token_rastreio = ?
    """
    pedido = conn.execute(query, (token,)).fetchone()
    conn.close()
    return pedido

def atualizar_progresso_pedido(token, novo_status, novo_index):
    conn = criar_conexao()
    conn.execute("UPDATE pedidos SET status = ?, etapa_index = ? WHERE token_rastreio = ?", 
                 (novo_status, novo_index, token))
    conn.commit()
    conn.close()

def salvar_avaliacao_pedido(token, nota, obs):
    conn = criar_conexao()
    conn.execute("UPDATE pedidos SET avaliacao_nota = ?, avaliacao_obs = ? WHERE token_rastreio = ?", (nota, obs, token))
    conn.commit()
    conn.close()

def apagar_pedido(token):
    # Nota: Em produção real, faríamos Soft Delete. Mantendo hard delete por enquanto.
    conn = criar_conexao()
    conn.execute("DELETE FROM pedidos WHERE token_rastreio = ?", (token,))
    conn.commit()
    conn.close()


def atualizar_produto(id, nome, estoque, lista_etapas):
    # Converte a lista novamente para JSON antes de salvar
    etapas_str = json.dumps(lista_etapas)
    conn = criar_conexao()
    conn.execute("""
        UPDATE produtos 
        SET nome = ?, estoque_atual = ?, etapas_json = ?
        WHERE id = ?
    """, (nome, estoque, etapas_str, id))
    conn.commit()
    conn.close()

def listar_feedbacks():
    conn = criar_conexao()
    # Busca pedidos com nota, trazendo também o nome do produto
    query = """
        SELECT pedidos.*, produtos.nome as produto_nome 
        FROM pedidos 
        LEFT JOIN produtos ON pedidos.produto_id = produtos.id
        WHERE avaliacao_nota IS NOT NULL 
        ORDER BY pedidos.id DESC
    """
    feedbacks = conn.execute(query).fetchall()
    conn.close()
    return feedbacks

def cancelar_pedido(token):
    conn = criar_conexao()
    
    # 1. Busca os dados do pedido para saber produto e quantidade
    pedido = conn.execute("SELECT produto_id, quantidade FROM pedidos WHERE token_rastreio = ?", (token,)).fetchone()
    
    if pedido:
        # 2. Devolve a quantidade ao estoque (Estorno)
        conn.execute("""
            UPDATE produtos 
            SET estoque_atual = estoque_atual + ? 
            WHERE id = ?
        """, (pedido['quantidade'], pedido['produto_id']))
        
        # 3. Marca o pedido como Cancelado (Não deleta)
        conn.execute("""
            UPDATE pedidos 
            SET status = 'Cancelado', avaliacao_obs = 'Pedido cancelado administrativamente.' 
            WHERE token_rastreio = ?
        """, (token,))
        
        conn.commit()
    
    conn.close()