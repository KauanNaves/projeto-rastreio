import sqlite3

def criar_conexao():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row 
    return conn

def criar_cursor(conn):
    cursor = conn.cursor()
    return cursor

def criar_tabelas():
    conn = criar_conexao()
    cursor = criar_cursor(conn)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            senha_hash TEXT NOT NULL
        )
    """)

    # ADICIONAMOS: avaliacao_nota e avaliacao_obs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_nome TEXT NOT NULL,
            cliente_email TEXT,
            numero_pedido TEXT NOT NULL,
            descricao TEXT NOT NULL,
            status TEXT NOT NULL,
            prioridade TEXT,
            prazo_entrega TEXT,
            token_rastreio TEXT NOT NULL UNIQUE,
            avaliacao_nota INTEGER, 
            avaliacao_obs TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    cursor.close()
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

# --- Funções de Pedidos ---
def adicionar_pedido(cliente_nome, cliente_email, numero_pedido, descricao, status, prioridade, prazo_entrega, token_rastreio):
    conn = criar_conexao()
    conn.execute("""
        INSERT INTO pedidos (cliente_nome, cliente_email, numero_pedido, descricao, status, prioridade, prazo_entrega, token_rastreio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (cliente_nome, cliente_email, numero_pedido, descricao, status, prioridade, prazo_entrega, token_rastreio))
    conn.commit()
    conn.close()

def listar_pedidos():
    conn = criar_conexao()
    pedidos = conn.execute("SELECT * FROM pedidos ORDER BY id DESC").fetchall()
    conn.close()
    return pedidos

def buscar_pedido(token):
    conn = criar_conexao()
    pedido = conn.execute("SELECT * FROM pedidos WHERE token_rastreio = ?", (token,)).fetchone()
    conn.close()
    return pedido

def atualizar_pedido(token, cliente_nome, cliente_email, descricao, status, prioridade, prazo_entrega):
    conn = criar_conexao()
    conn.execute("""
        UPDATE pedidos 
        SET cliente_nome = ?, cliente_email = ?, descricao = ?, status = ?, prioridade = ?, prazo_entrega = ?
        WHERE token_rastreio = ?
    """, (cliente_nome, cliente_email, descricao, status, prioridade, prazo_entrega, token))
    conn.commit()
    conn.close()

def atualizar_status_pedido(token, novo_status):
    conn = criar_conexao()
    conn.execute("UPDATE pedidos SET status = ? WHERE token_rastreio = ?", (novo_status, token))
    conn.commit()
    conn.close()

def apagar_pedido(token):
    conn = criar_conexao()
    conn.execute("DELETE FROM pedidos WHERE token_rastreio = ?", (token,))
    conn.commit()
    conn.close()

# --- NOVA FUNÇÃO: SALVAR AVALIAÇÃO ---
def salvar_avaliacao_pedido(token, nota, obs):
    conn = criar_conexao()
    conn.execute("""
        UPDATE pedidos 
        SET avaliacao_nota = ?, avaliacao_obs = ?
        WHERE token_rastreio = ?
    """, (nota, obs, token))
    conn.commit()
    conn.close()

# Funções de Qualidade (Itens) mantidas, mas simplificadas aqui pois não alteramos a lógica
def fechar_cursor(cursor):
    cursor.close()