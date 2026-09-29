import sqlite3
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox

import sistema

# ==========================
# CONFIGURAÇÕES VISUAIS
# ==========================
FONTE = "Arial"

COR_PRIMARIA = "#1565C0"
COR_PRIMARIA_ESCURA = "#0D47A1"
COR_FUNDO = "#F4F6F8"
COR_CARD = "#FFFFFF"
COR_BORDA = "#CFD8DC"
COR_TEXTO = "#263238"
COR_TEXTO_SEC = "#607D8B"
COR_SUCESSO = "#2E7D32"
COR_ERRO = "#C62828"
COR_AVISO = "#EF6C00"
COR_NEUTRA = "#546E7A"

STATUS_EQUIP = ["Ativo", "Inativo"]
STATUS_OS = ["Aberta", "Em andamento", "Concluída"]
TIPOS = ["Preventiva", "Corretiva"]
PRIORIDADES = ["Baixa", "Média", "Alta"]

# ==========================
# JANELA
# ==========================
janela = tk.Tk()
janela.title("Sistema de Manutenção Industrial")
janela.geometry("420x800")
janela.minsize(360, 600)
janela.configure(bg=COR_FUNDO)
janela.option_add("*TCombobox*Listbox.font", (FONTE, 12))

# ==========================
# ESTILOS
# ==========================
estilo = ttk.Style()
estilo.theme_use("clam")

estilo.configure("Fundo.TFrame", background=COR_FUNDO)
estilo.configure("Campo.TLabel", background=COR_FUNDO, foreground=COR_TEXTO,
                 font=(FONTE, 11, "bold"))
estilo.configure("Detalhe.TLabel", background=COR_FUNDO, foreground=COR_TEXTO_SEC,
                 font=(FONTE, 10))

# Abas principais
estilo.configure("TNotebook", background=COR_FUNDO, borderwidth=0)
estilo.configure("TNotebook.Tab", padding=[14, 10], font=(FONTE, 11, "bold"),
                 background="#DDE3EA", foreground=COR_TEXTO, borderwidth=0)
estilo.map("TNotebook.Tab",
           background=[("selected", COR_PRIMARIA)],
           foreground=[("selected", "white")])

# Sub-abas
estilo.configure("Sub.TNotebook", background=COR_FUNDO, borderwidth=0)
estilo.configure("Sub.TNotebook.Tab", padding=[12, 8], font=(FONTE, 10, "bold"),
                 background="#E3E8ED", foreground=COR_TEXTO_SEC, borderwidth=0)
estilo.map("Sub.TNotebook.Tab",
           background=[("selected", "white")],
           foreground=[("selected", COR_PRIMARIA)])

# Botões
estilo.configure("TButton", font=(FONTE, 11, "bold"), padding=10,
                 background="#ECEFF1", foreground=COR_TEXTO, borderwidth=1)
estilo.map("TButton", background=[("active", "#CFD8DC")])

estilo.configure("Primary.TButton", background=COR_PRIMARIA, foreground="white",
                 borderwidth=0)
estilo.map("Primary.TButton",
           background=[("active", COR_PRIMARIA_ESCURA), ("pressed", COR_PRIMARIA_ESCURA)])

estilo.configure("Danger.TButton", background=COR_ERRO, foreground="white",
                 borderwidth=0)
estilo.map("Danger.TButton",
           background=[("active", "#8E0000"), ("pressed", "#8E0000")])

# Campos
estilo.configure("TEntry", padding=8, fieldbackground="white")
estilo.configure("TCombobox", padding=8, fieldbackground="white")
estilo.map("TCombobox", fieldbackground=[("readonly", "white")])

# Tabelas
# A altura da linha acompanha o tamanho real da fonte (no celular ela fica maior)
fonte_tabela = tkfont.Font(family=FONTE, size=9)
altura_linha = fonte_tabela.metrics("linespace") + 28
estilo.configure("Treeview", rowheight=altura_linha, font=fonte_tabela, background="white",
                 fieldbackground="white", foreground=COR_TEXTO, bordercolor=COR_BORDA)
estilo.configure("Treeview.Heading", font=(FONTE, 9, "bold"), background=COR_PRIMARIA,
                 foreground="white", padding=8, relief="flat")
estilo.map("Treeview.Heading", background=[("active", COR_PRIMARIA_ESCURA)])
estilo.map("Treeview",
           background=[("selected", "#BBDEFB")],
           foreground=[("selected", COR_TEXTO)])

estilo.configure("Vertical.TScrollbar", arrowsize=24)


# ==========================
# FUNÇÕES AUXILIARES
# ==========================
_aviso_id = None


def limpar_aviso():
    barra_status.config(text="Pronto", bg=COR_NEUTRA)


def aviso(texto, tipo="info"):
    """Mostra uma mensagem colorida na barra inferior."""
    global _aviso_id
    cores = {"ok": COR_SUCESSO, "erro": COR_ERRO, "aviso": COR_AVISO, "info": COR_PRIMARIA}
    barra_status.config(text=texto, bg=cores.get(tipo, COR_PRIMARIA))
    if _aviso_id is not None:
        janela.after_cancel(_aviso_id)
    _aviso_id = janela.after(6000, limpar_aviso)


def ajustar_quebra(widget, margem=24):
    """Faz o texto do Label quebrar linha conforme a largura da tela."""
    widget.bind("<Configure>",
                lambda e: e.widget.config(wraplength=max(e.width - margem, 100)))


def rotulo(pai, texto):
    ttk.Label(pai, text=texto, style="Campo.TLabel").pack(anchor="w", pady=(10, 3))


def criar_tabela(pai, colunas, altura=8):
    """Cria um Treeview com barra de rolagem.
    colunas = (id, titulo, largura EM CARACTERES, alinhamento)."""
    px_char = fonte_tabela.measure("0")
    caixa = ttk.Frame(pai, style="Fundo.TFrame")
    tabela = ttk.Treeview(caixa, columns=[c[0] for c in colunas], show="headings",
                          height=altura, selectmode="browse")
    for posicao, (cid, titulo, largura, ancora) in enumerate(colunas):
        tabela.heading(cid, text=titulo)
        # só a 2ª coluna (nome) estica; as outras mantêm a largura
        tabela.column(cid, width=largura * px_char + 20, minwidth=largura * px_char, anchor=ancora, stretch=(posicao == 1))
    barra = ttk.Scrollbar(caixa, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=barra.set)
    tabela.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    return caixa, tabela


def preencher_tabela(tabela, linhas):
    """linhas = lista de (iid, valores, tag). Mantém a seleção atual."""
    selecionado = tabela.selection()
    tabela.delete(*tabela.get_children())
    for iid, valores, tag in linhas:
        tabela.insert("", "end", iid=str(iid), values=valores, tags=(tag,) if tag else ())
    if selecionado and tabela.exists(selecionado[0]):
        tabela.selection_set(selecionado[0])


def id_selecionado(tabela, mensagem):
    selecao = tabela.selection()
    if not selecao:
        aviso(mensagem, "aviso")
        return None
    return int(selecao[0])


# ==========================
# RESUMO
# ==========================
def atualizar_resumo():
    equipamentos = sistema.listar_equipamentos()
    ordens = sistema.listar_ordens_servico()

    cards["total"].config(text=str(len(equipamentos)))
    cards["ativos"].config(text=str(sum(1 for e in equipamentos if e[3] == "Ativo")))
    cards["inativos"].config(text=str(sum(1 for e in equipamentos if e[3] == "Inativo")))
    cards["abertas"].config(text=str(sum(1 for o in ordens if o[5] == "Aberta")))
    cards["andamento"].config(text=str(sum(1 for o in ordens if o[5] == "Em andamento")))
    cards["concluidas"].config(text=str(sum(1 for o in ordens if o[5] == "Concluída")))


# ==========================
# EQUIPAMENTOS
# ==========================
def carregar_equipamentos(*_):
    termo = busca_var.get().strip().lower()
    linhas = []
    for eq in sistema.listar_equipamentos():
        if termo and termo not in eq[1].lower() and termo not in eq[2].lower():
            continue
        linhas.append((eq[0], (eq[0], eq[1], eq[2], eq[3]),
                       "inativo" if eq[3] == "Inativo" else ""))
    preencher_tabela(tabela_equip, linhas)


def atualizar_combo_equipamentos():
    valores = [f"{eq[0]} - {eq[1]}" for eq in sistema.listar_equipamentos()]
    combo_os_equip["values"] = valores
    if combo_os_equip.get() not in valores:
        combo_os_equip.set("")


def salvar_equipamento():
    nome = entrada_nome.get().strip()
    setor = entrada_setor.get().strip()
    status = combo_status_equip.get()

    if not nome or not setor:
        aviso("Preencha o nome e o setor do equipamento.", "erro")
        return

    sistema.cadastra_equipamento(nome, setor, status)

    entrada_nome.delete(0, tk.END)
    entrada_setor.delete(0, tk.END)
    combo_status_equip.set("Ativo")

    atualizar_tudo()
    sub_equip.select(aba_equip_lista)
    aviso(f"Equipamento '{nome}' cadastrado com sucesso!", "ok")


def alternar_status_equipamento():
    id_eq = id_selecionado(tabela_equip, "Toque em um equipamento da lista primeiro.")
    if id_eq is None:
        return

    atual = tabela_equip.set(str(id_eq), "status")
    novo = "Inativo" if atual == "Ativo" else "Ativo"

    if sistema.atualizar_equipamento(novo, id_eq) == 0:
        aviso("Equipamento não encontrado.", "erro")
    else:
        aviso(f"Equipamento {id_eq} agora está {novo}.", "ok")
    atualizar_tudo()


def excluir_equipamento():
    id_eq = id_selecionado(tabela_equip, "Toque em um equipamento da lista primeiro.")
    if id_eq is None:
        return

    nome = tabela_equip.set(str(id_eq), "nome")
    if not messagebox.askyesno("Confirmar exclusão",
                               f"Deseja realmente excluir '{nome}'?"):
        return

    try:
        excluido = sistema.excluir_equipamento(id_eq)
    except sqlite3.IntegrityError:
        sistema.conexao.rollback()
        aviso("Não é possível excluir: existem ordens de serviço vinculadas. "
              "Exclua as OS primeiro ou marque o equipamento como Inativo.", "erro")
        return

    if excluido == 0:
        aviso("Equipamento não encontrado.", "erro")
    else:
        aviso(f"Equipamento '{nome}' excluído.", "ok")
    atualizar_tudo()


# ==========================
# ORDENS DE SERVIÇO
# ==========================
descricoes_os = {}


def carregar_ordens(*_):
    filtro = filtro_os.get()
    linhas = []
    descricoes_os.clear()

    for ordem in sistema.listar_ordens_servico():
        # ordem = (id, nome_equipamento, tipo, prioridade, descricao, status)
        descricoes_os[ordem[0]] = (ordem[2], ordem[4])
        if filtro != "Todos" and ordem[5] != filtro:
            continue

        if ordem[5] == "Concluída":
            tag = "concluida"
        elif ordem[3] == "Alta":
            tag = "alta"
        else:
            tag = ""
        linhas.append((ordem[0], (ordem[0], ordem[1], ordem[3], ordem[5]), tag))

    preencher_tabela(tabela_os, linhas)
    mostrar_detalhe_os()


def mostrar_detalhe_os(*_):
    selecao = tabela_os.selection()
    if not selecao:
        detalhe_os.config(text="Toque em uma OS para ver a descrição.")
        return
    id_os = int(selecao[0])
    tipo, descricao = descricoes_os.get(id_os, ("", ""))
    detalhe_os.config(text=f"OS {id_os} ({tipo}): {descricao}")


def salvar_os():
    selecionado = combo_os_equip.get()
    if not selecionado:
        aviso("Selecione o equipamento da ordem de serviço.", "erro")
        return

    try:
        equipamento_id = int(selecionado.split(" - ")[0])
    except ValueError:
        aviso("Equipamento inválido.", "erro")
        return

    descricao = entrada_descricao.get("1.0", tk.END).strip()
    if not descricao:
        aviso("Escreva a descrição do serviço.", "erro")
        return

    if sistema.buscar_equipamento(equipamento_id) is None:
        aviso("Esse equipamento não existe mais.", "erro")
        atualizar_tudo()
        return

    sistema.cadastrar_os(equipamento_id, combo_tipo.get(), combo_prioridade.get(),
                         descricao, combo_status_os.get())

    entrada_descricao.delete("1.0", tk.END)
    combo_tipo.set("Preventiva")
    combo_prioridade.set("Baixa")
    combo_status_os.set("Aberta")

    atualizar_tudo()
    sub_os.select(aba_os_lista)
    aviso("Ordem de serviço cadastrada com sucesso!", "ok")


def atualizar_status_os():
    id_os = id_selecionado(tabela_os, "Toque em uma OS da lista primeiro.")
    if id_os is None:
        return

    novo = combo_novo_status.get()
    if sistema.atualizar_status_os(id_os, novo) == 0:
        aviso("OS não encontrada.", "erro")
    else:
        aviso(f"OS {id_os} atualizada para '{novo}'.", "ok")
    atualizar_tudo()


def excluir_os():
    id_os = id_selecionado(tabela_os, "Toque em uma OS da lista primeiro.")
    if id_os is None:
        return

    if not messagebox.askyesno("Confirmar exclusão", f"Deseja realmente excluir a OS {id_os}?"):
        return

    if sistema.excluir_os(id_os) == 0:
        aviso("OS não encontrada.", "erro")
    else:
        aviso(f"OS {id_os} excluída.", "ok")
    atualizar_tudo()


def atualizar_tudo(*_):
    carregar_equipamentos()
    carregar_ordens()
    atualizar_combo_equipamentos()
    atualizar_resumo()


# ==========================
# CABEÇALHO E BARRA DE STATUS
# ==========================
cabecalho = tk.Frame(janela, bg=COR_PRIMARIA)
cabecalho.pack(fill="x")

titulo = tk.Label(cabecalho, text="Sistema de Manutenção Industrial",
                  font=(FONTE, 15, "bold"), bg=COR_PRIMARIA, fg="white",
                  justify="left", anchor="w", padx=14)
titulo.pack(fill="x", pady=(12, 0))
ajustar_quebra(titulo, 28)

subtitulo = tk.Label(cabecalho, text="Controle de equipamentos e ordens de serviço",
                     font=(FONTE, 10), bg=COR_PRIMARIA, fg="#BBDEFB",
                     justify="left", anchor="w", padx=14)
subtitulo.pack(fill="x", pady=(0, 12))
ajustar_quebra(subtitulo, 28)

barra_status = tk.Label(janela, text="Pronto", font=(FONTE, 10, "bold"), bg=COR_NEUTRA,
                        fg="white", anchor="w", justify="left", padx=12, pady=10)
barra_status.pack(side="bottom", fill="x")
ajustar_quebra(barra_status, 24)

abas = ttk.Notebook(janela)
abas.pack(fill="both", expand=True, padx=6, pady=6)

aba_resumo = ttk.Frame(abas, style="Fundo.TFrame", padding=10)
aba_equip = ttk.Frame(abas, style="Fundo.TFrame", padding=6)
aba_os = ttk.Frame(abas, style="Fundo.TFrame", padding=6)

abas.add(aba_resumo, text="Resumo")
abas.add(aba_equip, text="Equipamentos")
abas.add(aba_os, text="Ordens")

# ==========================
# ABA RESUMO
# ==========================
cards = {}


def criar_card(linha, coluna, chave, titulo_card, cor):
    card = tk.Frame(aba_resumo, bg=COR_CARD, highlightbackground=COR_BORDA,
                    highlightthickness=1)
    card.grid(row=linha, column=coluna, sticky="nsew", padx=6, pady=6)
    valor = tk.Label(card, text="0", font=(FONTE, 30, "bold"), bg=COR_CARD, fg=cor)
    valor.pack(pady=(16, 0))
    tk.Label(card, text=titulo_card, font=(FONTE, 10), bg=COR_CARD,
             fg=COR_TEXTO_SEC).pack(pady=(0, 16))
    cards[chave] = valor


tk.Label(aba_resumo, text="Visão geral", font=(FONTE, 13, "bold"), bg=COR_FUNDO,
         fg=COR_TEXTO, anchor="w").grid(row=0, column=0, columnspan=2, sticky="w", padx=6)

criar_card(1, 0, "total", "Equipamentos", COR_PRIMARIA)
criar_card(1, 1, "ativos", "Ativos", COR_SUCESSO)
criar_card(2, 0, "inativos", "Inativos", COR_NEUTRA)
criar_card(2, 1, "abertas", "OS abertas", COR_AVISO)
criar_card(3, 0, "andamento", "OS em andamento", COR_PRIMARIA)
criar_card(3, 1, "concluidas", "OS concluídas", COR_SUCESSO)

aba_resumo.columnconfigure(0, weight=1, uniform="cards")
aba_resumo.columnconfigure(1, weight=1, uniform="cards")

# ==========================
# ABA EQUIPAMENTOS
# ==========================
sub_equip = ttk.Notebook(aba_equip, style="Sub.TNotebook")
sub_equip.pack(fill="both", expand=True)

aba_equip_lista = ttk.Frame(sub_equip, style="Fundo.TFrame", padding=8)
aba_equip_novo = ttk.Frame(sub_equip, style="Fundo.TFrame", padding=12)
sub_equip.add(aba_equip_lista, text="Lista")
sub_equip.add(aba_equip_novo, text="Novo equipamento")

# --- Lista ---
busca_var = tk.StringVar()
busca_var.trace_add("write", carregar_equipamentos)

ttk.Label(aba_equip_lista, text="Buscar por nome ou setor", style="Campo.TLabel").pack(
    anchor="w", pady=(0, 3))
ttk.Entry(aba_equip_lista, textvariable=busca_var, font=(FONTE, 11)).pack(fill="x", pady=(0, 8))

caixa_equip, tabela_equip = criar_tabela(
    aba_equip_lista,
    [("id", "ID", 3, "center"), ("nome", "Nome", 12, "w"),
     ("setor", "Setor", 12, "w"), ("status", "Status", 8, "center")],
    altura=9)
caixa_equip.pack(fill="both", expand=True)
tabela_equip.tag_configure("inativo", foreground="#90A4AE")

botoes_equip = ttk.Frame(aba_equip_lista, style="Fundo.TFrame")
botoes_equip.pack(fill="x", pady=(10, 0))
botoes_equip.columnconfigure(0, weight=1, uniform="b")
botoes_equip.columnconfigure(1, weight=1, uniform="b")
ttk.Button(botoes_equip, text="Ativar / Inativar", style="Primary.TButton",
           command=alternar_status_equipamento).grid(row=0, column=0, sticky="ew", padx=(0, 4))
ttk.Button(botoes_equip, text="Excluir", style="Danger.TButton",
           command=excluir_equipamento).grid(row=0, column=1, sticky="ew", padx=(4, 0))

# --- Novo ---
rotulo(aba_equip_novo, "Nome do equipamento")
entrada_nome = ttk.Entry(aba_equip_novo, font=(FONTE, 12))
entrada_nome.pack(fill="x")

rotulo(aba_equip_novo, "Setor")
entrada_setor = ttk.Entry(aba_equip_novo, font=(FONTE, 12))
entrada_setor.pack(fill="x")

rotulo(aba_equip_novo, "Status")
combo_status_equip = ttk.Combobox(aba_equip_novo, values=STATUS_EQUIP, state="readonly",
                                  font=(FONTE, 12))
combo_status_equip.set("Ativo")
combo_status_equip.pack(fill="x")

ttk.Button(aba_equip_novo, text="Cadastrar equipamento", style="Primary.TButton",
           command=salvar_equipamento).pack(fill="x", pady=(22, 0))

# ==========================
# ABA ORDENS DE SERVIÇO
# ==========================
sub_os = ttk.Notebook(aba_os, style="Sub.TNotebook")
sub_os.pack(fill="both", expand=True)

aba_os_lista = ttk.Frame(sub_os, style="Fundo.TFrame", padding=8)
aba_os_nova = ttk.Frame(sub_os, style="Fundo.TFrame", padding=12)
sub_os.add(aba_os_lista, text="Lista")
sub_os.add(aba_os_nova, text="Nova OS")

# --- Lista ---
ttk.Label(aba_os_lista, text="Filtrar por status", style="Campo.TLabel").pack(
    anchor="w", pady=(0, 3))
filtro_os = ttk.Combobox(aba_os_lista, values=["Todos"] + STATUS_OS, state="readonly",
                         font=(FONTE, 11))
filtro_os.set("Todos")
filtro_os.pack(fill="x", pady=(0, 8))
filtro_os.bind("<<ComboboxSelected>>", carregar_ordens)

caixa_os, tabela_os = criar_tabela(
    aba_os_lista,
    [("id", "OS", 3, "center"), ("equipamento", "Equipamento", 12, "w"),
     ("prioridade", "Prior.", 7, "center"), ("status", "Status", 13, "center")],
    altura=7)
caixa_os.pack(fill="both", expand=True)
tabela_os.tag_configure("alta", foreground=COR_ERRO)
tabela_os.tag_configure("concluida", foreground=COR_SUCESSO)
tabela_os.bind("<<TreeviewSelect>>", mostrar_detalhe_os)

detalhe_os = ttk.Label(aba_os_lista, text="Toque em uma OS para ver a descrição.",
                       style="Detalhe.TLabel", justify="left")
detalhe_os.pack(fill="x", pady=(8, 4))
ajustar_quebra(detalhe_os, 20)

acoes_os = ttk.Frame(aba_os_lista, style="Fundo.TFrame")
acoes_os.pack(fill="x")
acoes_os.columnconfigure(0, weight=1, uniform="a")
acoes_os.columnconfigure(1, weight=1, uniform="a")

combo_novo_status = ttk.Combobox(acoes_os, values=STATUS_OS, state="readonly",
                                 font=(FONTE, 11))
combo_novo_status.set("Em andamento")
combo_novo_status.grid(row=0, column=0, sticky="ew", padx=(0, 4))
ttk.Button(acoes_os, text="Atualizar status", style="Primary.TButton",
           command=atualizar_status_os).grid(row=0, column=1, sticky="ew", padx=(4, 0))
ttk.Button(acoes_os, text="Excluir OS selecionada", style="Danger.TButton",
           command=excluir_os).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

# --- Nova OS ---
rotulo(aba_os_nova, "Equipamento")
combo_os_equip = ttk.Combobox(aba_os_nova, state="readonly", font=(FONTE, 12))
combo_os_equip.pack(fill="x")

rotulo(aba_os_nova, "Tipo")
combo_tipo = ttk.Combobox(aba_os_nova, values=TIPOS, state="readonly", font=(FONTE, 12))
combo_tipo.set("Preventiva")
combo_tipo.pack(fill="x")

rotulo(aba_os_nova, "Prioridade")
combo_prioridade = ttk.Combobox(aba_os_nova, values=PRIORIDADES, state="readonly",
                                font=(FONTE, 12))
combo_prioridade.set("Baixa")
combo_prioridade.pack(fill="x")

rotulo(aba_os_nova, "Descrição do serviço")
entrada_descricao = tk.Text(aba_os_nova, height=5, font=(FONTE, 11), wrap="word",
                            bg="white", fg=COR_TEXTO, relief="flat", padx=8, pady=8,
                            highlightthickness=1, highlightbackground=COR_BORDA,
                            highlightcolor=COR_PRIMARIA)
entrada_descricao.pack(fill="x")

rotulo(aba_os_nova, "Status")
combo_status_os = ttk.Combobox(aba_os_nova, values=STATUS_OS, state="readonly",
                               font=(FONTE, 12))
combo_status_os.set("Aberta")
combo_status_os.pack(fill="x")

ttk.Button(aba_os_nova, text="Cadastrar ordem de serviço", style="Primary.TButton",
           command=salvar_os).pack(fill="x", pady=(22, 0))

# ==========================
# INICIALIZAÇÃO
# ==========================
abas.bind("<<NotebookTabChanged>>", atualizar_tudo)
atualizar_tudo()

janela.mainloop()
