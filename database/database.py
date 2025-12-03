import sqlite3

def criar_conexao():
    conn = sqlite3.connect('database.db')
    return conn


def criar_cursor(conn):
    cursor = conn.cursor()
    return cursor


def criar_tabelas():
    criar_tabela_usuarios()
    criar_tabela_pedidos()
    criar_tabela_qualidade()


def criar_tabela_usuarios():
    conn = criar_conexao()
    cursor = criar_cursor(conn)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            senha_hash TEXT NOT NULL
)""")

    fechar_cursor(cursor)
    fechar_conexao(conn, cursor)


def adicionar_usuario(email, senha_hash):
    conn = criar_conexao()
    cursor = criar_cursor(conn)

    cursor.execute("""
        INSERT INTO usuarios (email, senha_hash)
        VALUES (?, ?)
    """, (email, senha_hash))

    conn.commit()
    fechar_cursor(cursor)
    fechar_conexao(conn, cursor)


def buscar_usuario(email):
    conn = criar_conexao()
    cursor = criar_cursor(conn)

    cursor.execute("""
        SELECT * FROM usuarios WHERE email = ?
    """, (email,))

    usuario = cursor.fetchone()
    fechar_cursor(cursor)
    fechar_conexao(conn, cursor)

    return usuario


def criar_tabela_pedidos():
    conn = criar_conexao()
    cursor = criar_cursor(conn)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_nome TEXT NOT NULL,
            numero_pedido TEXT   NOT NULL,
            descricao TEXT NOT NULL,
            status TEXT NOT NULL,
            token_rastreio TEXT NOT NULL UNIQUE,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")

    fechar_cursor(cursor)
    fechar_conexao(conn, cursor)


def adicionar_pedido(cliente_nome, numero_pedido, descricao, status, token_rastreio):
    conn = criar_conexao()
    cursor = criar_cursor(conn)

    cursor.execute("""
        INSERT INTO pedidos (cliente_nome, numero_pedido, descricao, status, token_rastreio)
        VALUES (?, ?, ?, ?, ?)
    """, (cliente_nome, numero_pedido, descricao, status, token_rastreio))

    conn.commit()
    fechar_cursor(cursor)
    fechar_conexao(conn, cursor)


def buscar_pedido(numero_pedido):
    conn = criar_conexao()
    cursor = criar_cursor(conn)

    cursor.execute("""
        SELECT * FROM pedidos WHERE token_rastreio = ?
    """, (numero_pedido,))

    pedido = cursor.fetchone()
    fechar_cursor(cursor)
    fechar_conexao(conn, cursor)

    return pedido


def apagar_pedido(numero_pedido):
    conn = criar_conexao()
    cursor = criar_cursor(conn)

    cursor.execute("""
        DELETE FROM pedidos WHERE token_rastreio = ?
    """, (numero_pedido,))

    conn.commit()
    fechar_cursor(cursor)
    fechar_conexao(conn, cursor)


def criar_tabela_qualidade():
    conn = criar_conexao()
    cursor = criar_cursor(conn)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_qualidade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            etapa_nome   TEXT NOT NULL,
            aprovado BOOLEAN NOT NULL,
            observacoes TEXT,
            FOREIGN KEY (pedido_id) REFERENCES pedidos (id)
)""")

    fechar_cursor(cursor)
    fechar_conexao(conn, cursor)


def adicionar_qualidade(pedido_id, etapa_nome, aprovado, observacoes):
    conn = criar_conexao()
    cursor = criar_cursor(conn)

    cursor.execute("""
        INSERT INTO itens_qualidade (pedido_id, etapa_nome, aprovado, observacoes)
        VALUES (?, ?, ?, ?)
    """, (pedido_id, etapa_nome, aprovado, observacoes))

    conn.commit()
    fechar_cursor(cursor)
    fechar_conexao(conn, cursor)


def buscar_qualidade(pedido_id):
    conn = criar_conexao()
    cursor = criar_cursor(conn)

    cursor.execute("""
        SELECT * FROM itens_qualidade WHERE pedido_id = ?
    """, (pedido_id,))

    qualidade = cursor.fetchall()
    fechar_cursor(cursor)
    fechar_conexao(conn, cursor)

    return qualidade


def fechar_cursor(cursor):
    cursor.close()


def fechar_conexao(conn, cursor):
    fechar_cursor(cursor)
    conn.close()