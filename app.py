from flask import Flask, jsonify, render_template, request

from backend.algorithms import ALGORITMOS_BUSCA, ALGORITMOS_ORDEM
from backend import models
from backend.models import tarifa_para_hora
from backend.repository import (
    CAMPOS_BUSCA,
    CAMPOS_ORDENACAO,
    EXPLICACAO_COMPLEXIDADE,
    criar_repository_com_dados,
)
from backend.stats import calcular_estatisticas, calcular_relatorio

app = Flask(__name__)
repositorio = criar_repository_com_dados()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/catalogo")
def catalogo():
    return jsonify(
        {
            "campos_busca": CAMPOS_BUSCA,
            "campos_ordenacao": CAMPOS_ORDENACAO,
            "algoritmos_busca": [
                {"id": chave, "nome": nome, "complexidade": cx,
                 "explicacao": EXPLICACAO_COMPLEXIDADE[nome]}
                for chave, (nome, cx, _) in ALGORITMOS_BUSCA.items()
            ],
            "algoritmos_ordem": [
                {"id": chave, "nome": nome, "complexidade": cx,
                 "explicacao": EXPLICACAO_COMPLEXIDADE[nome]}
                for chave, (nome, cx, _) in ALGORITMOS_ORDEM.items()
            ],
            "tarifa_base": models.TARIFA_BASE_KWH,
            "taxa_servico": models.TAXA_SERVICO_SESSAO,
            "faixas": {h: {"tarifa": tarifa_para_hora(h), "faixa": _faixa(h)} for h in (0, 3, 9, 19)},
        }
    )


def _faixa(hora: int) -> str:
    return models.faixa_horaria(hora)


@app.route("/api/sessoes", methods=["GET"])
def listar_sessoes():
    campo = request.args.get("campo", "placa")
    termo = request.args.get("termo", "")
    sessoes = repositorio.buscar_todos(campo, termo) if termo else repositorio.listar()
    return jsonify(
        {
            "sessoes": [s.para_dict() for s in sessoes],
            "total": repositorio.total(),
            "filtradas": len(sessoes),
        }
    )


@app.route("/api/sessoes", methods=["POST"])
def criar_sessao():
    dados = request.get_json(force=True, silent=True) or {}
    if not dados.get("data_inicio"):
        return jsonify({"erro": "Informe a data/hora de início."}), 400
    sessao = repositorio.adicionar(dados)
    return jsonify({"sessao": sessao.para_dict(), "total": repositorio.total()}), 201


@app.route("/api/sessoes/<int:sessao_id>", methods=["DELETE"])
def remover_sessao(sessao_id: int):
    ok = repositorio.remover(sessao_id)
    return (jsonify({"removido": ok, "total": repositorio.total()}),
            200 if ok else 404)


@app.route("/api/busca", methods=["POST"])
def busca():
    dados = request.get_json(force=True, silent=True) or {}
    campo = dados.get("campo", "id")
    valor = dados.get("valor", "")
    algoritmo = dados.get("algoritmo", "linear")

    if str(valor).strip() == "":
        return jsonify({"erro": "Informe o valor da busca."}), 400

    resultado = repositorio.buscar(campo, valor, algoritmo)
    sessao = resultado.pop("sessao", None)
    resultado["sessao"] = sessao.para_dict() if sessao else None
    resultado["explicacao"] = EXPLICACAO_COMPLEXIDADE[resultado["algoritmo"]]
    return jsonify(resultado)


@app.route("/api/ordenar", methods=["POST"])
def ordenar():
    dados = request.get_json(force=True, silent=True) or {}
    resultado = repositorio.ordenar(
        campo=dados.get("campo", "id"),
        algoritmo=dados.get("algoritmo", "bubble"),
        reverse=bool(dados.get("reverse", False)),
    )
    return jsonify(resultado)


@app.route("/api/tarifa", methods=["POST"])
def atualizar_tarifa():
    dados = request.get_json(force=True, silent=True) or {}
    try:
        base = float(dados.get("tarifa_base", models.TARIFA_BASE_KWH))
        taxa = float(dados.get("taxa_servico", models.TAXA_SERVICO_SESSAO))
    except (TypeError, ValueError):
        return jsonify({"erro": "Tarifa inválida."}), 400
    if base <= 0 or taxa < 0:
        return jsonify({"erro": "Tarifa deve ser > 0 e taxa >= 0."}), 400

    models.atualizar_tarifa(base, taxa)
    total = repositorio.recalcular_todas()
    return jsonify(
        {
            "tarifa_base": models.TARIFA_BASE_KWH,
            "taxa_servico": models.TAXA_SERVICO_SESSAO,
            "sessoes_recalculadas": total,
            "faixas": {
                "normal": models.tarifa_para_hora(12),
                "ponta": models.tarifa_para_hora(19),
                "valle": models.tarifa_para_hora(3),
            },
        }
    )


@app.route("/api/estatisticas")
def estatisticas():
    return jsonify(calcular_estatisticas(repositorio.listar()))


@app.route("/api/relatorio")
def relatorio():
    return jsonify(calcular_relatorio(repositorio.listar()))


@app.route("/api/complexidade")
def complexidade():
    n = repositorio.total()
    return jsonify(
        {
            "sessoes_atuais": n,
            "operacoes": [
                {"local": "repositorio.adicionar()", "acao": "inserir sessão no fim da lista",
                 "complexidade": "O(1)", "situacao": f"{n} sessões -> 1 operação"},
                {"local": "repository.listar()", "acao": " listar/serializar sessões",
                 "complexidade": "O(n)", "situacao": f"{n} sessões -> {n} leituras"},
                {"local": "algorithms.busca_linear()", "acao": "buscar sessão",
                 "complexidade": "O(n)", "situacao": f"pior caso: {n} comparações"},
                {"local": "algorithms.busca_binaria()", "acao": "buscar em lista ordenada",
                 "complexidade": "O(log n)",
                 "situacao": f"pior caso: ~{max(1, n.bit_length())} comparações"},
                {"local": "algorithms.bubble_sort() / insertion / selection",
                 "acao": "ordenar sessões", "complexidade": "O(n²)",
                 "situacao": f"~{n * (n - 1) // 2} comparações"},
                {"local": "algorithms.merge_sort() / quick_sort",
                 "acao": "ordenar sessões", "complexidade": "O(n log n)",
                 "situacao": f"~{n * max(1, n.bit_length())} comparações"},
                {"local": "stats.calcular_estatisticas()", "acao": "calcular médias e totais",
                 "complexidade": "O(n)", "situacao": f"{n} sessões percorridas 1x"},
            ],
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
