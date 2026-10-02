from typing import Any, Dict, List, Optional

from .algorithms import (
    ALGORITMOS_BUSCA,
    ALGORITMOS_ORDEM,
    busca_binaria,
    busca_linear,
    merge_sort,
)
from .models import SessaoRecarga

CAMPOS_ORDENACAO = [
    "id", "data_inicio", "kwh", "custo_total", "duracao_min",
    "potencia_media", "placa", "veiculo", "estacao",
]
CAMPOS_BUSCA = ["id", "placa", "veiculo", "estacao", "kwh", "custo_total"]


class SessaoRepository:

    def __init__(self) -> None:
        self.sessoes: List[SessaoRecarga] = []
        self._proximo_id = 1

    def adicionar(self, dados: Dict[str, Any]) -> SessaoRecarga:
        sessao = SessaoRecarga(
            id=self._proximo_id,
            veiculo=str(dados.get("veiculo", "")).strip() or "Não informado",
            placa=str(dados.get("placa", "")).strip().upper() or "SEM-PLACA",
            estacao=str(dados.get("estacao", "")).strip() or "EST-01",
            data_inicio=str(dados.get("data_inicio", "")).replace(" ", "T"),
            duracao_min=float(dados.get("duracao_min", 30)),
            kwh=float(dados.get("kwh", 10)),
            status=str(dados.get("status", "concluida")),
        )
        self.sessoes.append(sessao)
        self._proximo_id += 1
        return sessao

    def listar(self) -> List[SessaoRecarga]:
        return list(self.sessoes)

    def remover(self, sessao_id: int) -> bool:
        for indice, sessao in enumerate(self.sessoes):
            if sessao.id == sessao_id:
                self.sessoes.pop(indice)
                return True
        return False

    def total(self) -> int:
        return len(self.sessoes)

    def recalcular_todas(self) -> int:
        for sessao in self.sessoes:
            sessao.recalcular()
        return len(self.sessoes)

    def buscar(self, campo: str, valor: Any, algoritmo: str = "linear") -> Dict[str, Any]:
        if algoritmo == "binaria":
            ordenada, metricas_ordem = merge_sort(self.sessoes, campo)
            resultado = busca_binaria(ordenada, campo, self._coerce(campo, valor))
            resultado["ordenacao_previa"] = metricas_ordem
        else:
            resultado = busca_linear(self.sessoes, campo, self._coerce(campo, valor))
            resultado["ordenacao_previa"] = None

        resultado["campo"] = campo
        resultado["valor_pesquisado"] = valor
        resultado["total_sessoes"] = self.total()
        return resultado

    def buscar_todos(self, campo: str, termo: str) -> List[SessaoRecarga]:
        termo = str(termo).lower().strip()
        achados: List[SessaoRecarga] = []
        for sessao in self.sessoes:
            valor = str(getattr(sessao, campo, "")).lower()
            if termo in valor:
                achados.append(sessao)
        return achados

    def ordenar(self, campo: str, algoritmo: str = "merge", reverse: bool = False) -> Dict[str, Any]:
        if campo not in CAMPOS_ORDENACAO:
            campo = "id"
        nome, complexidade, funcao = ALGORITMOS_ORDEM.get(algoritmo, ALGORITMOS_ORDEM["merge"])
        ordenadas, metricas = funcao(self.sessoes, campo, reverse)
        metricas["campo"] = campo
        metricas["direcao"] = "decrescente" if reverse else "crescente"
        metricas["lista_ordenada"] = [s.para_dict() for s in ordenadas]
        metricas["complexidade_explicacao"] = EXPLICACAO_COMPLEXIDADE[nome]
        return metricas

    @staticmethod
    def _coerce(campo: str, valor: Any) -> Any:
        if campo == "id":
            try:
                return int(valor)
            except (TypeError, ValueError):
                return valor
        if campo in ("kwh", "custo_total", "duracao_min"):
            try:
                return float(valor)
            except (TypeError, ValueError):
                return valor
        return valor


EXPLICACAO_COMPLEXIDADE = {
    "Bubble Sort": (
        "Compara cada elemento com o vizinho em n-1 posições, repetindo o "
        "processo n vezes: aproximadamente n*(n-1)/2 comparações -> O(n²)."
    ),
    "Insertion Sort": (
        "Para cada um dos n elementos desloca os anteriores até a posição "
        "correta: no pior caso também n*(n-1)/2 comparações -> O(n²)."
    ),
    "Selection Sort": (
        "Percorre os n-i restantes para achar o extremo, gerando "
        "n*(n-1)/2 comparações -> O(n²), mesmo com a lista já ordenada."
    ),
    "Merge Sort": (
        "Divide a lista em duas metades até sobrarem n elementos de tamanho 1 "
        "(log n níveis) e intercala percorrendo n elementos por nível -> "
        "n * log n -> O(n log n)."
    ),
    "Quick Sort": (
        "A cada divisão o pivô parte a lista ao meio (log n níveis) e percorre "
        "os elementos do nível: n * log n -> O(n log n) no caso médio."
    ),
    "Busca Linear": (
        "Percorre a lista do início até encontrar o item. No pior caso "
        "percorre todas as n sessões -> O(n)."
    ),
    "Busca Binária": (
        "Divide o intervalo de busca pela metade a cada comparação. Para n "
        "sessões são necessárias no máximo log2(n) comparações -> O(log n)."
    ),
}


def criar_repository_com_dados() -> SessaoRepository:
    repo = SessaoRepository()
    exemplos = [
        {"veiculo": "Nissan Leaf", "placa": "ABC1D23", "estacao": "EST-01", "data_inicio": "2026-09-27T19:10", "duracao_min": 45, "kwh": 22.5},
        {"veiculo": "BYD Dolphin", "placa": "DEF4G56", "estacao": "EST-02", "data_inicio": "2026-09-27T08:30", "duracao_min": 30, "kwh": 15.0},
        {"veiculo": "Volvo EX30", "placa": "GHI7J89", "estacao": "EST-01", "data_inicio": "2026-09-28T02:15", "duracao_min": 60, "kwh": 38.2},
        {"veiculo": "Tesla Model 3", "placa": "JKL0M12", "estacao": "EST-03", "data_inicio": "2026-09-28T18:45", "duracao_min": 25, "kwh": 26.8},
        {"veiculo": "Fiat 500e", "placa": "NOP3Q45", "estacao": "EST-02", "data_inicio": "2026-09-28T14:00", "duracao_min": 50, "kwh": 12.4},
        {"veiculo": "Chevrolet Bolt", "placa": "QRS6T78", "estacao": "EST-04", "data_inicio": "2026-09-29T20:05", "duracao_min": 40, "kwh": 30.1},
        {"veiculo": "Renault K-ZE", "placa": "UVW9X01", "estacao": "EST-01", "data_inicio": "2026-09-29T05:40", "duracao_min": 90, "kwh": 41.7},
        {"veiculo": "VW ID.4", "placa": "YZA2B34", "estacao": "EST-03", "data_inicio": "2026-09-29T12:20", "duracao_min": 35, "kwh": 19.6},
    ]
    for dados in exemplos:
        repo.adicionar(dados)
    return repo
