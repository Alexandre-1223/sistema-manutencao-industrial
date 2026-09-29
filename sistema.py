import sqlite3

# Cria (ou abre) o banco de dados
conexao = sqlite3.connect("manutencao.db")
conexao.execute("PRAGMA foreign_keys = ON")
cursor = conexao.cursor()

# Cria a tabela de equipamentos
cursor.execute("""
CREATE TABLE IF NOT EXISTS equipamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    setor TEXT NOT NULL,
    status TEXT NOT NULL
)
""")

# Cria a tabela de ordens de serviço
cursor.execute("""
CREATE TABLE IF NOT EXISTS ordens_servico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipamento_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    prioridade TEXT NOT NULL,
    descricao TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (equipamento_id) REFERENCES equipamentos(id)
)
""")

def cadastrar_os(equipamento_id, tipo, prioridade, descricao, status):

    # Verifica se o equipamento existe
    cursor.execute(
        "SELECT * FROM equipamentos WHERE id = ?",
        (equipamento_id,)
    )

    equipamento = cursor.fetchone()

    if equipamento is None:
        return

 # Salva a OS no banco
    cursor.execute("""
        INSERT INTO ordens_servico
        (equipamento_id, tipo, prioridade, descricao, status)
        VALUES (?, ?, ?, ?, ?)
    """, (equipamento_id, tipo, prioridade, descricao, status))

    conexao.commit()

def listar_ordens_servico():
    cursor.execute("SELECT ordens_servico.id, equipamentos.nome, ordens_servico.tipo, ordens_servico.prioridade, ordens_servico.descricao, ordens_servico.status FROM ordens_servico JOIN equipamentos ON equipamentos.id = ordens_servico.equipamento_id")
    
   
    return cursor.fetchall()

def atualizar_status_os(id_os, novo_status):
     
    cursor.execute(
        "UPDATE ordens_servico SET status = ? WHERE id = ?",
        (novo_status, id_os)
    )

    conexao.commit()
    
    return cursor.rowcount
    
def excluir_os(id_os):
    
    cursor.execute(
        "DELETE FROM ordens_servico WHERE id = ?",
        (id_os,)
    )

    conexao.commit()

    return cursor.rowcount


def buscar_ordens_status(status):
   
    cursor.execute(
        "SELECT equipamentos.nome, ordens_servico.tipo, ordens_servico.prioridade, ordens_servico.descricao, ordens_servico.status FROM ordens_servico JOIN equipamentos ON equipamentos.id = ordens_servico.equipamento_id WHERE ordens_servico.status = ?",
        (status,)
    )

    return cursor.fetchall()


def listar_equipamentos():
    cursor.execute("SELECT * FROM equipamentos")
    equipamentos = cursor.fetchall()

    return equipamentos

def cadastra_equipamento(nome, setor, status):

    cursor.execute(
        "INSERT INTO equipamentos (nome, setor, status) VALUES (?, ?, ?)",
        (nome, setor, status)
    )

    conexao.commit()


def buscar_equipamento(id_equipamento):
    
    cursor.execute(
        "SELECT * FROM equipamentos WHERE id = ?",
        (id_equipamento,)
    )

    return  cursor.fetchone()

def atualizar_equipamento(novo_status,id_equipamento):
    
    cursor.execute(
        "UPDATE equipamentos SET status = ? WHERE id = ?",
        (novo_status, id_equipamento)
    )

    conexao.commit()

    return cursor.rowcount
        
def excluir_equipamento(id_equipamento):
    
    cursor.execute(
        "DELETE FROM equipamentos WHERE id = ?",
        (id_equipamento,)
    )

    conexao.commit()

    return cursor.rowcount


def resumo_sistema():
    cursor.execute("SELECT COUNT(*) FROM equipamentos")
    equipamento = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM equipamentos WHERE status = ?", ("Ativo",))
    status_ativo = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM equipamentos WHERE status = ?", ("Inativo",))
    status_inativo = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM ordens_servico WHERE status = ?", ("Aberta",))
    status_aberta = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM ordens_servico WHERE status = ?", ("Em andamento",))
    status_andamento = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM ordens_servico WHERE status = ?", ("Concluída",))
    status_concluida = cursor.fetchone()

    print("\n=== RESUMO DO SISTEMA ===")
    print(f"Equipamentos cadastrados: {equipamento[0]}")
    print(f"Equipamentos ativos: {status_ativo[0]}")
    print(f"Equipamentos inativos: {status_inativo[0]}")
    print()
    print(f"Ordens de serviço abertas: {status_aberta[0]}")
    print(f"Ordens de serviço em andamento: {status_andamento[0]}")
    print(f"Ordens de serviço concluídas: {status_concluida[0]}")

    # Fecha a conexão
    conexao.close()