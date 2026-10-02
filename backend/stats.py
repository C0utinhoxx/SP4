from collections import defaultdict
from statistics import mean, median
from typing import Any, Dict, List

from . import models
from .models import SessaoRecarga


def _validas(sessoes: List[SessaoRecarga]) -> List[SessaoRecarga]:
    return [s for s in sessoes if s.status != "cancelada"]


def _arredondar(grupo: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    return {
        nome: {"sessoes": v["sessoes"], "kwh": round(v["kwh"], 2), "custo": round(v["custo"], 2)}
        for nome, v in grupo.items()
    }


def calcular_estatisticas(sessoes: List[SessaoRecarga]) -> Dict[str, Any]:
    dados = _validas(sessoes)
    if not dados:
        return {"mensagem": "Nenhuma sessão registrada ainda.", "total": 0}

    kwh = [s.kwh for s in dados]
    custos = [s.custo_total for s in dados]
    duracoes = [s.duracao_min for s in dados]

    maior = max(dados, key=lambda s: s.kwh)
    menor = min(dados, key=lambda s: s.kwh)

    por_faixa = defaultdict(lambda: {"sessoes": 0, "kwh": 0.0, "custo": 0.0})
    por_estacao = defaultdict(lambda: {"sessoes": 0, "kwh": 0.0, "custo": 0.0})
    for s in dados:
        por_faixa[s.faixa_tarifaria]["sessoes"] += 1
        por_faixa[s.faixa_tarifaria]["kwh"] += s.kwh
        por_faixa[s.faixa_tarifaria]["custo"] += s.custo_total
        por_estacao[s.estacao]["sessoes"] += 1
        por_estacao[s.estacao]["kwh"] += s.kwh
        por_estacao[s.estacao]["custo"] += s.custo_total

    return {
        "total": len(sessoes),
        "sessoes_validas": len(dados),
        "kwh_total": round(sum(kwh), 2),
        "custo_total": round(sum(custos), 2),
        "media_kwh": round(mean(kwh), 2),
        "mediana_kwh": round(median(kwh), 2),
        "media_custo": round(mean(custos), 2),
        "media_duracao": round(mean(duracoes), 1),
        "maior_sessao": {"placa": maior.placa, "veiculo": maior.veiculo, "kwh": maior.kwh},
        "menor_sessao": {"placa": menor.placa, "veiculo": menor.veiculo, "kwh": menor.kwh},
        "tarifa_base": models.TARIFA_BASE_KWH,
        "taxa_servico": models.TAXA_SERVICO_SESSAO,
        "por_faixa": _arredondar(por_faixa),
        "por_estacao": _arredondar(por_estacao),
        "complexidade": "O(n) — cada sessão é visitada uma única vez para acumular os totais.",
    }


def calcular_relatorio(sessoes: List[SessaoRecarga]) -> Dict[str, Any]:
    dados = _validas(sessoes)
    stats = calcular_estatisticas(sessoes)
    if not dados:
        return {"mensagem": "Sem dados para gerar o relatório.", "total": 0}

    datas = sorted(s.data_objeto() for s in dados)
    veiculos = defaultdict(lambda: {"sessoes": 0, "kwh": 0.0, "custo": 0.0})
    for s in dados:
        veiculos[f"{s.veiculo} ({s.placa})"]["sessoes"] += 1
        veiculos[f"{s.veiculo} ({s.placa})"]["kwh"] += s.kwh
        veiculos[f"{s.veiculo} ({s.placa})"]["custo"] += s.custo_total

    ranking = sorted(veiculos.items(), key=lambda par: par[1]["kwh"], reverse=True)[:5]

    return {
        "periodo_inicio": datas[0].strftime("%d/%m/%Y %H:%M"),
        "periodo_fim": datas[-1].strftime("%d/%m/%Y %H:%M"),
        "total_sessoes": stats["total"],
        "kwh_total": stats["kwh_total"],
        "custo_total": stats["custo_total"],
        "economia_valle": round(
            sum(s.kwh * (models.TARIFA_BASE_KWH - s.tarifa_kwh) for s in dados if s.faixa_tarifaria == "valle"), 2
        ),
        "custo_ponta": round(sum(s.custo_total for s in dados if s.faixa_tarifaria == "ponta"), 2),
        "consumo_medio": stats["media_kwh"],
        "duracao_media": stats["media_duracao"],
        "top_veiculos": [{"veiculo": nome, **valores} for nome, valores in ranking],
        "por_estacao": stats["por_estacao"],
        "por_faixa": stats["por_faixa"],
        "observacao": (
            "Tarifação aplicada por faixa horária: ponta (18h-21h) +40%, "
            "válle (00h-06h) -20% e horário normal com a tarifa base de "
            f"R$ {models.TARIFA_BASE_KWH:.2f}/kWh, mais taxa de serviço de "
            f"R$ {models.TAXA_SERVICO_SESSAO:.2f} por sessão."
        ),
    }
