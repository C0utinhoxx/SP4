from typing import Any, Callable, Dict, List, Tuple


def busca_linear(sessoes: List[Any], campo: str, valor: Any) -> Dict[str, Any]:
    comparacoes = 0
    for indice, sessao in enumerate(sessoes):
        comparacoes += 1
        atual = getattr(sessao, campo)
        if isinstance(valor, str):
            encontrado = str(atual).lower() == str(valor).lower()
        else:
            encontrado = atual == valor
        if encontrado:
            return {
                "encontrado": True,
                "indice": indice,
                "sessao": sessao,
                "comparacoes": comparacoes,
                "elementos_percorridos": indice + 1,
                "algoritmo": "Busca Linear",
                "complexidade": "O(n)",
            }

    return {
        "encontrado": False,
        "indice": -1,
        "sessao": None,
        "comparacoes": comparacoes,
        "elementos_percorridos": len(sessoes),
        "algoritmo": "Busca Linear",
        "complexidade": "O(n)",
    }


def busca_binaria(sessoes: List[Any], campo: str, valor: Any) -> Dict[str, Any]:
    baixo, alto = 0, len(sessoes) - 1
    comparacoes = 0

    while baixo <= alto:
        comparacoes += 1
        meio = (baixo + alto) // 2
        atual = getattr(sessoes[meio], campo)

        if isinstance(valor, str):
            atual_c = str(atual).lower()
            valor_c = str(valor).lower()
        else:
            atual_c, valor_c = atual, valor

        if atual_c == valor_c:
            return {
                "encontrado": True,
                "indice": meio,
                "sessao": sessoes[meio],
                "comparacoes": comparacoes,
                "elementos_percorridos": comparacoes,
                "algoritmo": "Busca Binária",
                "complexidade": "O(log n)",
            }
        if atual_c < valor_c:
            baixo = meio + 1
        else:
            alto = meio - 1

    return {
        "encontrado": False,
        "indice": -1,
        "sessao": None,
        "comparacoes": comparacoes,
        "elementos_percorridos": comparacoes,
        "algoritmo": "Busca Binária",
        "complexidade": "O(log n)",
    }


def _novo_metricas(algoritmo: str, complexidade: str) -> Dict[str, Any]:
    return {
        "algoritmo": algoritmo,
        "complexidade": complexidade,
        "comparacoes": 0,
        "trocas": 0,
        "passadas": 0,
        "tamanho": 0,
    }


def bubble_sort(lista: List[Any], campo: str, reverse: bool = False) -> Tuple[List[Any], Dict]:
    itens = list(lista)
    metricas = _novo_metricas("Bubble Sort", "O(n²)")
    metricas["tamanho"] = len(itens)
    n = len(itens)

    for i in range(n):
        trocou = False
        metricas["passadas"] += 1
        for j in range(0, n - i - 1):
            metricas["comparacoes"] += 1
            a = itens[j].chave(campo)
            b = itens[j + 1].chave(campo)
            trocar = a > b if not reverse else a < b
            if trocar:
                itens[j], itens[j + 1] = itens[j + 1], itens[j]
                metricas["trocas"] += 1
                trocou = True
        if not trocou:
            break

    return itens, metricas


def insertion_sort(lista: List[Any], campo: str, reverse: bool = False) -> Tuple[List[Any], Dict]:
    itens = list(lista)
    metricas = _novo_metricas("Insertion Sort", "O(n²)")
    metricas["tamanho"] = len(itens)

    for i in range(1, len(itens)):
        atual = itens[i]
        j = i - 1
        metricas["passadas"] += 1
        while j >= 0:
            metricas["comparacoes"] += 1
            ordenar = atual.chave(campo) < itens[j].chave(campo)
            if reverse:
                ordenar = atual.chave(campo) > itens[j].chave(campo)
            if not ordenar:
                break
            itens[j + 1] = itens[j]
            metricas["trocas"] += 1
            j -= 1
        itens[j + 1] = atual

    return itens, metricas


def selection_sort(lista: List[Any], campo: str, reverse: bool = False) -> Tuple[List[Any], Dict]:
    itens = list(lista)
    metricas = _novo_metricas("Selection Sort", "O(n²)")
    metricas["tamanho"] = len(itens)
    n = len(itens)

    for i in range(n):
        extremo = i
        metricas["passadas"] += 1
        for j in range(i + 1, n):
            metricas["comparacoes"] += 1
            atual = itens[j].chave(campo)
            alvo = itens[extremo].chave(campo)
            menor = atual < alvo if not reverse else atual > alvo
            if menor:
                extremo = j
        if extremo != i:
            itens[i], itens[extremo] = itens[extremo], itens[i]
            metricas["trocas"] += 1

    return itens, metricas


def merge_sort(lista: List[Any], campo: str, reverse: bool = False) -> Tuple[List[Any], Dict]:
    metricas = _novo_metricas("Merge Sort", "O(n log n)")
    metricas["tamanho"] = len(lista)

    def ordenar(itens: List[Any]) -> List[Any]:
        if len(itens) <= 1:
            return itens
        meio = len(itens) // 2
        esquerda = ordenar(itens[:meio])
        direita = ordenar(itens[meio:])
        return intercalar(esquerda, direita)

    def intercalar(esq: List[Any], dir: List[Any]) -> List[Any]:
        resultado = []
        i = j = 0
        while i < len(esq) and j < len(dir):
            metricas["comparacoes"] += 1
            manter = esq[i].chave(campo) <= dir[j].chave(campo)
            if reverse:
                manter = esq[i].chave(campo) >= dir[j].chave(campo)
            if manter:
                resultado.append(esq[i])
                i += 1
            else:
                resultado.append(dir[j])
                j += 1
            metricas["trocas"] += 1
        resultado.extend(esq[i:])
        resultado.extend(dir[j:])
        metricas["passadas"] += 1
        return resultado

    ordenados = ordenar(list(lista))
    return ordenados, metricas


def quick_sort(lista: List[Any], campo: str, reverse: bool = False) -> Tuple[List[Any], Dict]:
    itens = list(lista)
    metricas = _novo_metricas("Quick Sort", "O(n log n)")
    metricas["tamanho"] = len(itens)

    def ordenar(inicio: int, fim: int) -> None:
        if inicio >= fim:
            return
        metricas["passadas"] += 1
        pivo = itens[fim].chave(campo)
        i = inicio - 1
        for j in range(inicio, fim):
            metricas["comparacoes"] += 1
            menor = itens[j].chave(campo) < pivo
            if reverse:
                menor = itens[j].chave(campo) > pivo
            if menor:
                i += 1
                itens[i], itens[j] = itens[j], itens[i]
                metricas["trocas"] += 1
        itens[i + 1], itens[fim] = itens[fim], itens[i + 1]
        metricas["trocas"] += 1
        ordenar(inicio, i)
        ordenar(i + 2, fim)

    if itens:
        ordenar(0, len(itens) - 1)
    return itens, metricas


ALGORITMOS_ORDEM = {
    "bubble": ("Bubble Sort", "O(n²)", bubble_sort),
    "insertion": ("Insertion Sort", "O(n²)", insertion_sort),
    "selection": ("Selection Sort", "O(n²)", selection_sort),
    "merge": ("Merge Sort", "O(n log n)", merge_sort),
    "quick": ("Quick Sort", "O(n log n)", quick_sort),
}

ALGORITMOS_BUSCA = {
    "linear": ("Busca Linear", "O(n)", busca_linear),
    "binaria": ("Busca Binária", "O(log n)", busca_binaria),
}
