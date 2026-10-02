from dataclasses import dataclass, field, asdict
from datetime import datetime

TARIFA_BASE_KWH = 0.92
TAXA_SERVICO_SESSAO = 0.75
FATOR_PONTA = 1.40
FATOR_VALLE = 0.80


def faixa_horaria(hora: int) -> str:
    if 18 <= hora < 21:
        return "ponta"
    if 0 <= hora < 6:
        return "valle"
    return "normal"


def tarifa_para_hora(hora: int) -> float:
    faixa = faixa_horaria(hora)
    if faixa == "ponta":
        return round(TARIFA_BASE_KWH * FATOR_PONTA, 2)
    if faixa == "valle":
        return round(TARIFA_BASE_KWH * FATOR_VALLE, 2)
    return round(TARIFA_BASE_KWH, 2)


def atualizar_tarifa(base: float, taxa: float) -> None:
    global TARIFA_BASE_KWH, TAXA_SERVICO_SESSAO
    TARIFA_BASE_KWH = round(float(base), 2)
    TAXA_SERVICO_SESSAO = round(float(taxa), 2)


@dataclass
class SessaoRecarga:
    id: int
    veiculo: str
    placa: str
    estacao: str
    data_inicio: str
    duracao_min: float
    kwh: float
    status: str = "concluida"
    faixa_tarifaria: str = field(default="normal")
    tarifa_kwh: float = TARIFA_BASE_KWH
    taxa_servico: float = TAXA_SERVICO_SESSAO
    custo_total: float = 0.0
    potencia_media: float = 0.0

    def __post_init__(self):
        self.recalcular()

    def recalcular(self) -> None:
        hora = self.hora_inicio()
        self.faixa_tarifaria = faixa_horaria(hora)
        self.tarifa_kwh = tarifa_para_hora(hora)
        self.taxa_servico = TAXA_SERVICO_SESSAO
        self.custo_total = round(self.kwh * self.tarifa_kwh + self.taxa_servico, 2)
        horas = max(self.duracao_min, 1) / 60
        self.potencia_media = round(self.kwh / horas, 2)

    def hora_inicio(self) -> int:
        return datetime.fromisoformat(self.data_inicio).hour

    def data_objeto(self) -> datetime:
        return datetime.fromisoformat(self.data_inicio)

    def chave(self, campo: str):
        if campo == "data_inicio":
            return self.data_objeto()
        return getattr(self, campo)

    def para_dict(self) -> dict:
        dados = asdict(self)
        dados["data_inicio_fmt"] = self.data_objeto().strftime("%d/%m/%Y %H:%M")
        return dados
