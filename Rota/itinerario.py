KM_POR_TRECHO = 8
VELOCIDADE_KMH = {1: 50, 2: 40, 3: 30}
VELOCIDADE_PADRAO = 40


def calcular_itinerario(paradas, *, capacidade=None, vagas=None, prioridade=None, distancias=None):
    if capacidade is not None and capacidade <= 0:
        return _resultado(False, [], 0, 0, ["Veículo sem capacidade."])
    if capacidade is not None and vagas is not None and vagas > capacidade:
        return _resultado(False, [], 0, 0, ["As vagas passam da capacidade do veículo."])

    avisos = []
    brutas = []
    for parada in paradas or []:
        local = _texto(_campo(parada, "local"))
        if not local:
            avisos.append("Ponto sem local foi desconsiderado.")
            continue
        brutas.append({"local": local, "ordem": _campo(parada, "ordem")})

    if not brutas:
        avisos.append("Lista de paradas vazia.")
        return _resultado(True, [], 0, 0, avisos)

    brutas.sort(key=lambda item: (item["ordem"] is None, item["ordem"] or 0))
    vistos = set()
    unicos = []
    for item in brutas:
        chave = item["local"].casefold()
        if chave in vistos:
            avisos.append(f"Ponto duplicado desconsiderado: {item['local']}.")
            continue
        vistos.add(chave)
        unicos.append(item)

    if distancias:
        sequencia, distancia, inalcancaveis = _vizinho_mais_proximo(unicos, distancias)
        for local in inalcancaveis:
            avisos.append(f"Ponto inalcançável: {local}.")
    else:
        sequencia = unicos
        distancia = KM_POR_TRECHO * max(len(unicos) - 1, 0)

    saida = [
        {"ordem": indice, "local": item["local"], "ordem_informada": item["ordem"]}
        for indice, item in enumerate(sequencia, start=1)
    ]
    return _resultado(True, saida, _km(distancia), _tempo(distancia, prioridade), avisos)


def _vizinho_mais_proximo(paradas, distancias):
    matriz = {}
    for chave, valor in distancias.items():
        origem, destino = chave
        matriz[(origem.casefold(), destino.casefold())] = valor

    restantes = list(paradas)
    atual = restantes.pop(0)
    sequencia = [atual]
    distancia = 0
    while restantes:
        melhor = None
        melhor_km = None
        for candidato in restantes:
            km = _aresta(atual["local"], candidato["local"], matriz)
            if km is None:
                continue
            if melhor_km is None or km < melhor_km:
                melhor = candidato
                melhor_km = km
        if melhor is None:
            return sequencia, distancia, [item["local"] for item in restantes]
        distancia += melhor_km
        sequencia.append(melhor)
        restantes.remove(melhor)
        atual = melhor
    return sequencia, distancia, []


def _aresta(origem, destino, matriz):
    if origem.casefold() == destino.casefold():
        return 0
    ida = (origem.casefold(), destino.casefold())
    volta = (destino.casefold(), origem.casefold())
    if ida in matriz:
        return matriz[ida]
    return matriz.get(volta)


def _tempo(distancia, prioridade):
    velocidade = VELOCIDADE_KMH.get(prioridade, VELOCIDADE_PADRAO)
    if not velocidade:
        return 0
    return int(distancia / velocidade * 60 + 0.5)


def _km(valor):
    inteiro = int(valor)
    if valor == inteiro:
        return inteiro
    return round(valor, 1)


def _campo(parada, nome):
    if isinstance(parada, dict):
        return parada.get(nome)
    return getattr(parada, nome)


def _texto(valor):
    return (valor or "").strip()


def _resultado(ok, sequencia, distancia, tempo, avisos):
    return {
        "ok": ok,
        "sequencia": sequencia,
        "distancia_total_km": distancia,
        "tempo_estimado_min": tempo,
        "avisos": avisos,
    }
