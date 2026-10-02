# Sistema de Gerenciamento de Recargas — Sprint 4

Interface Web + backend Python para cadastro, busca, ordenação, estatística,
tarifação e relatório de sessões de recarga de veículos elétricos.

## Como executar

```bash
cd /Users/brunocoutinho/Documents/SP4
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python app.py
```

Abra <http://127.0.0.1:5000> no navegador.

## Estrutura

| Arquivo | Papel |
|---|---|
| `app.py` | Rotas Flask: Interface ⇄ Backend (JSON) |
| `backend/models.py` | `dataclass SessaoRecarga` + tarifação por faixa horária |
| `backend/repository.py` | Armazenamento das sessões em **lista** Python + busca/ordenação |
| `backend/algorithms.py` | Busca Linear/Binária e Bubble, Insertion, Selection, Merge e Quick Sort **manuais**, com contagem de operações |
| `backend/stats.py` | Estatísticas `O(n)` e relatório final |
| `templates/index.html` | Interface Web |
| `static/app.js`, `static/style.css` | Comunicação com a API e visual |

## Mapa para os critérios da Sprint 4

- **Demonstração e integração** — abas 1 a 6, tudo via `fetch()` → rota Flask → lista em Python → JSON → tela.
- **Estrutura de dados** — `SessaoRecarga` (dataclass) em `backend/models.py:48`; várias sessões em `repositorio.sessoes` (lista) em `backend/repository.py:33`.
- **Busca** — `busca_linear` (O(n)) e `busca_binaria` (O(log n)) em `backend/algorithms.py:17` e `:53`, com contador de comparações.
- **Ordenação** — cinco algoritmos próprios em `backend/algorithms.py:113` em diante (nenhum usa `list.sort()`).
- **Complexidade** — aba 6 calcula as operações com o valor real de `n`; cada algoritmo devolve `comparacoes`, `trocas` e `passadas`.
- **Tarifação/relatório** — ponta (18h–21h) +40%, válle (00h–06h) −20%, base `R$ 0,92/kWh` + taxa de sessão; tarifa alterável pela aba 5.

## API

| Rota | Método | Descrição |
|---|---|---|
| `/api/sessoes` | GET / POST | listar (com filtro) / cadastrar |
| `/api/sessoes/<id>` | DELETE | remover sessão |
| `/api/busca` | POST | busca linear ou binária |
| `/api/ordenar` | POST | ordenação com algoritmo próprio |
| `/api/estatisticas` | GET | médias, medianas, totais |
| `/api/relatorio` | GET | tarifação e resumo final |
| `/api/tarifa` | POST | altera tarifa e recalcula tudo `O(n)` |
| `/api/complexidade` | GET | operações reais por Big-O |
| `/api/catalogo` | GET | algoritmos, campos e explicações |
