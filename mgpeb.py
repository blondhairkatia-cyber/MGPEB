# =====================================================================
#  MGPEB - Modulo de Gerenciamento de Pouso e Estabilizacao de Base
#  Missao Aurora Siger - Prototipo em Python
#
#  Conteudos aplicados:
#   - Estruturas lineares: listas, fila (queue) e pilha (stack)
#   - Algoritmos de busca: busca linear e busca binaria
#   - Algoritmos de ordenacao: insertion sort e selection sort
#   - Regras booleanas (portas logicas) com IF / ELIF / ELSE
#   - Funcoes matematicas aplicadas (quadratica e linear)
#
#  Como executar:  python mgpeb.py
# =====================================================================


# ---------------------------------------------------------------------
# 1. CONSTANTES DA MISSAO
# ---------------------------------------------------------------------
COMBUSTIVEL_MINIMO = 20      # % minimo para considerar o combustivel "OK"
VENTO_MAXIMO = 60            # km/h maximo para considerar a atmosfera "OK"
GRAVIDADE_MARTE = 3.71       # m/s^2


# ---------------------------------------------------------------------
# 2. CADASTRO DOS MODULOS
#    Cada modulo e um dicionario com os atributos basicos.
#    prioridade: 1 (baixa) ate 5 (altissima)
#    chegada: minutos apos o inicio da janela de pouso (horario em orbita)
# ---------------------------------------------------------------------
def criar_modulo(codigo, tipo, prioridade, combustivel, massa, criticidade, chegada, sensores_ok):
    """Cria e devolve um dicionario representando um modulo de pouso."""
    return {
        "codigo": codigo,
        "tipo": tipo,
        "prioridade": prioridade,
        "combustivel": combustivel,   # em %
        "massa": massa,               # em kg
        "criticidade": criticidade,   # "alta", "media" ou "baixa"
        "chegada": chegada,           # minutos
        "sensores_ok": sensores_ok,   # True = sensores integros
    }


def cadastrar_modulos():
    """Devolve a lista inicial de modulos que estao chegando a orbita."""
    return [
        criar_modulo("HAB-01", "Habitacao",           5, 55, 12000, "alta",  30, True),
        criar_modulo("ENE-02", "Energia",             5, 40,  8500, "alta",  10, True),
        criar_modulo("LAB-03", "Laboratorio",         3, 70,  6000, "media", 50, True),
        criar_modulo("LOG-04", "Logistica",           2, 15,  9500, "baixa", 20, True),
        criar_modulo("MED-05", "Suporte Medico",      4, 35,  4000, "alta",  40, True),
        criar_modulo("COM-06", "Comunicacao",         3, 60,  3000, "media", 60, False),
        criar_modulo("AGR-07", "Agricultura",         2,  8,  7000, "media", 70, True),
    ]


# ---------------------------------------------------------------------
# 3. ESTRUTURAS LINEARES
#    - fila_pouso: FILA (FIFO) -> entra no fim (append), sai do inicio (pop(0))
#    - pousados, em_espera, em_alerta: LISTAS auxiliares
#    - historico: PILHA (LIFO) -> empilha com append, desempilha com pop()
# ---------------------------------------------------------------------
fila_pouso = []
pousados = []
em_espera = []
em_alerta = []
historico = []


def enfileirar(fila, modulo):
    """Insere o modulo no final da fila."""
    fila.append(modulo)


def desenfileirar(fila):
    """Remove e devolve o primeiro modulo da fila (FIFO)."""
    if len(fila) == 0:
        return None
    return fila.pop(0)


def empilhar(pilha, evento):
    """Coloca um evento no topo da pilha."""
    pilha.append(evento)


def desempilhar(pilha):
    """Remove e devolve o evento do topo da pilha (LIFO)."""
    if len(pilha) == 0:
        return None
    return pilha.pop()


# ---------------------------------------------------------------------
# 4. ALGORITMOS DE BUSCA
# ---------------------------------------------------------------------
def buscar_menor_combustivel(lista):
    """Busca linear: percorre a lista e guarda o modulo com menos combustivel."""
    if len(lista) == 0:
        return None
    menor = lista[0]
    for modulo in lista:
        if modulo["combustivel"] < menor["combustivel"]:
            menor = modulo
    return menor


def buscar_maior_prioridade(lista):
    """Busca linear: devolve o modulo de maior prioridade."""
    if len(lista) == 0:
        return None
    maior = lista[0]
    for modulo in lista:
        if modulo["prioridade"] > maior["prioridade"]:
            maior = modulo
    return maior


def buscar_por_tipo(lista, tipo):
    """Busca linear: devolve todos os modulos de um tipo de carga."""
    encontrados = []
    for modulo in lista:
        if modulo["tipo"].lower() == tipo.lower():
            encontrados.append(modulo)
    return encontrados


def busca_binaria_por_chegada(lista_ordenada, minuto):
    """Busca binaria: a lista PRECISA estar ordenada por 'chegada'.
    Devolve o modulo que chega no minuto informado ou None."""
    inicio = 0
    fim = len(lista_ordenada) - 1
    while inicio <= fim:
        meio = (inicio + fim) // 2
        valor = lista_ordenada[meio]["chegada"]
        if valor == minuto:
            return lista_ordenada[meio]
        elif valor < minuto:
            inicio = meio + 1
        else:
            fim = meio - 1
    return None


# ---------------------------------------------------------------------
# 5. ALGORITMOS DE ORDENACAO
# ---------------------------------------------------------------------
def vem_antes(a, b):
    """Criterio da fila de pouso:
    1o) maior prioridade primeiro;
    2o) em caso de empate, menor combustivel primeiro."""
    if a["prioridade"] != b["prioridade"]:
        return a["prioridade"] > b["prioridade"]
    return a["combustivel"] < b["combustivel"]


def insertion_sort_fila(lista):
    """Insertion sort: devolve uma NOVA lista ordenada pelo criterio da fila."""
    copia = lista[:]
    for i in range(1, len(copia)):
        atual = copia[i]
        j = i - 1
        while j >= 0 and vem_antes(atual, copia[j]):
            copia[j + 1] = copia[j]
            j = j - 1
        copia[j + 1] = atual
    return copia


def selection_sort_por_chegada(lista):
    """Selection sort: devolve uma NOVA lista ordenada pelo horario de chegada."""
    copia = lista[:]
    n = len(copia)
    for i in range(n - 1):
        menor = i
        for j in range(i + 1, n):
            if copia[j]["chegada"] < copia[menor]["chegada"]:
                menor = j
        copia[i], copia[menor] = copia[menor], copia[i]
    return copia


# ---------------------------------------------------------------------
# 6. REGRAS DE DECISAO (FUNCOES BOOLEANAS)
#    Variaveis:
#      C = combustivel suficiente     (combustivel >= 20%)
#      A = atmosfera favoravel        (vento <= 60 km/h E NAO tempestade)
#      D = area de pouso disponivel   (plataformas livres > 0)
#      S = sensores integros
#
#    AUTORIZAR = S AND D AND (A OR (NOT C))
#    ALERTA    = NOT S
#    ESPERA    = S AND NOT(D AND (A OR (NOT C)))
#
#    Leitura: com sensores bons e area livre, o modulo pousa se a
#    atmosfera estiver boa OU se estiver com pouco combustivel
#    (pouso de emergencia: esperar seria mais perigoso).
# ---------------------------------------------------------------------
def atmosfera_favoravel(clima):
    """A = (vento <= VENTO_MAXIMO) AND (NOT tempestade)"""
    return clima["vento"] <= VENTO_MAXIMO and not clima["tempestade"]


def decidir_pouso(modulo, clima, plataformas_livres):
    """Aplica a funcao booleana e devolve 'AUTORIZADO', 'ESPERA' ou 'ALERTA'."""
    C = modulo["combustivel"] >= COMBUSTIVEL_MINIMO
    A = atmosfera_favoravel(clima)
    D = plataformas_livres > 0
    S = modulo["sensores_ok"]

    if not S:
        return "ALERTA"                      # NOT S
    elif D and (A or not C):
        return "AUTORIZADO"                  # S AND D AND (A OR NOT C)
    else:
        return "ESPERA"                      # S AND NOT(D AND (A OR NOT C))


def simular_janela(numero, clima, plataformas):
    """Processa toda a fila de pouso em uma janela de operacao."""
    print(f"\n--- JANELA DE POUSO {numero} | vento {clima['vento']} km/h | "
          f"tempestade: {'sim' if clima['tempestade'] else 'nao'} | plataformas: {plataformas} ---")

    while len(fila_pouso) > 0:
        modulo = desenfileirar(fila_pouso)
        decisao = decidir_pouso(modulo, clima, plataformas)

        if decisao == "AUTORIZADO":
            plataformas = plataformas - 1
            pousados.append(modulo)
            if modulo["combustivel"] < COMBUSTIVEL_MINIMO:
                motivo = "pouso de EMERGENCIA (combustivel critico)"
            else:
                motivo = "condicoes normais"
        elif decisao == "ALERTA":
            em_alerta.append(modulo)
            motivo = "falha de sensores"
        else:
            em_espera.append(modulo)
            if plataformas == 0:
                motivo = "sem plataforma livre"
            else:
                motivo = "atmosfera desfavoravel"

        empilhar(historico, f"Janela {numero}: {modulo['codigo']} -> {decisao}")
        print(f"  {modulo['codigo']:7} {modulo['tipo']:15} -> {decisao:10} ({motivo})")


# ---------------------------------------------------------------------
# 7. MODELAGEM MATEMATICA
#    a) Descida apos o paraquedas (queda livre em Marte):
#         h(t) = h0 - v0*t - (g/2)*t^2       (funcao QUADRATICA)
#         v(t) = v0 + g*t                    (funcao LINEAR)
#    b) Altitude de acionamento dos retrofoguetes:
#         h_ign = v^2 / (2*(a_motor - g))
#    c) Energia solar ao longo do dia (aproximacao quadratica):
#         P(t) = Pmax * (1 - ((t - 12)/6)^2), para 6 <= t <= 18
# ---------------------------------------------------------------------
def altura(t, h0=2000, v0=60, g=GRAVIDADE_MARTE):
    """Altura (m) em funcao do tempo (s) apos o desligamento do paraquedas."""
    return h0 - v0 * t - (g / 2) * t ** 2


def velocidade(t, v0=60, g=GRAVIDADE_MARTE):
    """Velocidade de descida (m/s) em funcao do tempo (s)."""
    return v0 + g * t


def altitude_ignicao(v, a_motor=12.0, g=GRAVIDADE_MARTE):
    """Altitude minima (m) para que os retrofoguetes consigam zerar a velocidade v."""
    return v ** 2 / (2 * (a_motor - g))


def potencia_solar(hora, pmax=100):
    """Potencia solar (kW) gerada na base em funcao da hora do dia."""
    if hora < 6 or hora > 18:
        return 0
    return pmax * (1 - ((hora - 12) / 6) ** 2)


def momento_retrofoguete(margem=1.2):
    """Percorre o tempo de 1 em 1 segundo ate a altura ficar menor que a
    altitude de ignicao (com margem de seguranca de 20%)."""
    t = 0
    while altura(t) > altitude_ignicao(velocidade(t)) * margem:
        t = t + 1
    return t


# ---------------------------------------------------------------------
# 8. FUNCOES DE EXIBICAO
# ---------------------------------------------------------------------
def mostrar_lista(titulo, lista):
    print(f"\n{titulo} ({len(lista)} modulo(s))")
    for m in lista:
        print(f"  {m['codigo']:7} {m['tipo']:15} prio={m['prioridade']} "
              f"comb={m['combustivel']:3}% massa={m['massa']:6}kg "
              f"crit={m['criticidade']:5} chegada={m['chegada']:3}min "
              f"sensores={'OK' if m['sensores_ok'] else 'FALHA'}")


def titulo(texto):
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


# ---------------------------------------------------------------------
# 9. PROGRAMA PRINCIPAL
# ---------------------------------------------------------------------
def main():
    titulo("MGPEB - MISSAO AURORA SIGER")

    # Cadastro e entrada na fila (ordem de chegada da comunicacao)
    for modulo in cadastrar_modulos():
        enfileirar(fila_pouso, modulo)
    mostrar_lista("Fila inicial de pouso", fila_pouso)

    # Buscas
    titulo("BUSCAS")
    m = buscar_menor_combustivel(fila_pouso)
    print(f"Menor combustivel : {m['codigo']} ({m['combustivel']}%)")
    m = buscar_maior_prioridade(fila_pouso)
    print(f"Maior prioridade  : {m['codigo']} (prioridade {m['prioridade']})")
    medicos = buscar_por_tipo(fila_pouso, "Suporte Medico")
    print(f"Tipo 'Suporte Medico': {[x['codigo'] for x in medicos]}")
    por_chegada = selection_sort_por_chegada(fila_pouso)
    m = busca_binaria_por_chegada(por_chegada, 40)
    print(f"Busca binaria (chegada = 40 min): {m['codigo'] if m else 'nenhum'}")

    # Ordenacao
    titulo("ORDENACAO")
    mostrar_lista("Ordenada por chegada (selection sort)", por_chegada)
    fila_pouso[:] = insertion_sort_fila(fila_pouso)
    mostrar_lista("Fila reorganizada: prioridade desc. e combustivel asc. (insertion sort)", fila_pouso)

    # Simulacao das decisoes de pouso
    titulo("SIMULACAO DE AUTORIZACAO DE POUSO")
    simular_janela(1, {"vento": 35, "tempestade": False}, plataformas=3)

    # Quem ficou em espera volta para a fila na proxima janela
    while len(em_espera) > 0:
        enfileirar(fila_pouso, em_espera.pop(0))
    simular_janela(2, {"vento": 85, "tempestade": True}, plataformas=3)

    mostrar_lista("Modulos pousados", pousados)
    mostrar_lista("Modulos em espera", em_espera)
    mostrar_lista("Modulos em alerta", em_alerta)

    # Pilha: ultimos eventos (do mais recente para o mais antigo)
    titulo("HISTORICO (PILHA) - 3 ULTIMOS EVENTOS")
    for _ in range(3):
        print("  " + desempilhar(historico))

    # Modelagem matematica
    titulo("MODELAGEM: DESCIDA E RETROFOGUETES")
    print("  t(s)   altura(m)   velocidade(m/s)   h_ignicao(m)")
    for t in range(0, 21, 5):
        print(f"  {t:4} {altura(t):10.1f} {velocidade(t):14.1f} {altitude_ignicao(velocidade(t)):14.1f}")
    t_ign = momento_retrofoguete()
    print(f"\n  Acionar retrofoguetes em t = {t_ign} s "
          f"(altura {altura(t_ign):.0f} m, velocidade {velocidade(t_ign):.1f} m/s)")

    titulo("MODELAGEM: ENERGIA SOLAR NA BASE")
    for hora in range(6, 19, 2):
        print(f"  {hora:2}h -> {potencia_solar(hora):6.1f} kW")
    print("  Regra: pousos que exigem muita energia da base ficam entre 9h e 15h (P >= 75 kW).")


if __name__ == "__main__":
    main()
