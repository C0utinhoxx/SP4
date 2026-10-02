const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const api = {
  get: (url) => fetch(url).then((r) => r.json()),
  send: (url, method, body) =>
    fetch(url, { method, headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body) }).then((r) => r.json()),
};

const moeda = (v) => `R$ ${Number(v).toFixed(2)}`;
const brl = (v) => Number(v).toLocaleString("pt-BR", { minimumFractionDigits: 2 });

$$(".aba").forEach((btn) =>
  btn.addEventListener("click", () => {
    $$(".aba").forEach((b) => b.classList.remove("ativa"));
    $$(".painel").forEach((p) => p.classList.remove("ativo"));
    btn.classList.add("ativa");
    $("#" + btn.dataset.aba).classList.add("ativo");
    if (btn.dataset.aba === "stats") carregarStats();
    if (btn.dataset.aba === "relatorio") carregarRelatorio();
    if (btn.dataset.aba === "complexidade") carregarComplexidade();
  })
);

let catalogo = null;
async function carregarCatalogo() {
  catalogo = await api.get("/api/catalogo");
  const preencher = (el, itens) => {
    el.innerHTML = itens.map((i) => `<option value="${i.id}">${i.nome} — ${i.complexidade}</option>`).join("");
  };
  $("#campoBusca").innerHTML = catalogo.campos_busca.map((c) => `<option>${c}</option>`).join("");
  $("#campoOrdem").innerHTML = catalogo.campos_ordenacao.map((c) => `<option>${c}</option>`).join("");
  preencher($("#algoritmoBusca"), catalogo.algoritmos_busca);
  preencher($("#algoritmoOrdem"), catalogo.algoritmos_ordem);
  $("#statusBackend").textContent = `Backend Python (Flask) conectado — tarifa base ${moeda(catalogo.tarifa_base)}/kWh`;
}
carregarCatalogo();

async function carregarSessoes(campo = "", termo = "") {
  const url = termo
    ? `/api/sessoes?campo=${encodeURIComponent(campo)}&termo=${encodeURIComponent(termo)}`
    : "/api/sessoes";
  const dados = await api.get(url);
  const tbody = $("#tabelaSessoes tbody");
  tbody.innerHTML = dados.sessoes
    .map(
      (s) => `<tr>
        <td>${s.id}</td>
        <td>${s.veiculo}<br><small style="color:#9aa7b4">${s.placa}</small></td>
        <td>${s.estacao}</td>
        <td>${s.data_inicio_fmt}</td>
        <td>${s.duracao_min}</td>
        <td>${s.kwh}</td>
        <td>${s.faixa_tarifaria}</td>
        <td>${moeda(s.tarifa_kwh)}</td>
        <td><b>${moeda(s.custo_total)}</b></td>
        <td><button class="fantasma" onclick="removerSessao(${s.id})">x</button></td>
      </tr>`
    )
    .join("");
  $("#contador").textContent =
    `${dados.filtradas} sessão(ões) exibida(s) de ${dados.total} armazenadas na lista do Python`;
}
window.removerSessao = async (id) => {
  await api.send(`/api/sessoes/${id}`, "DELETE", {});
  carregarSessoes($("#campoFiltro").value, $("#termoFiltro").value.trim());
};

$("#formSessao").addEventListener("submit", async (e) => {
  e.preventDefault();
  const dados = Object.fromEntries(new FormData(e.target).entries());
  dados.duracao_min = parseFloat(dados.duracao_min);
  dados.kwh = parseFloat(dados.kwh);
  const resp = await api.send("/api/sessoes", "POST", dados);
  if (resp.erro) return alert(resp.erro);
  const s = resp.sessao;
  alert(`Sessão #${s.id} gravada!\n${s.veiculo} — ${s.kwh} kWh\nFaixa ${s.faixa_tarifaria}: ${moeda(s.tarifa_kwh)}/kWh\nCusto total: ${moeda(s.custo_total)}`);
  e.target.reset();
  carregarSessoes();
});

$("#btnFiltrar").addEventListener("click", () =>
  carregarSessoes($("#campoFiltro").value, $("#termoFiltro").value.trim())
);
$("#btnLimpar").addEventListener("click", () => {
  $("#termoFiltro").value = "";
  carregarSessoes();
});

$("#btnBuscar").addEventListener("click", async () => {
  const campo = $("#campoBusca").value;
  const valor = $("#valorBusca").value.trim();
  if (!valor) return alert("Informe o valor da busca.");
  const r = await api.send("/api/busca", "POST", {
    campo, valor, algoritmo: $("#algoritmoBusca").value,
  });
  if (r.erro) return alert(r.erro);

  $("#metricasBusca").hidden = false;
  $("#bBuscaAlgoritmo").textContent = r.algoritmo;
  $("#bBuscaComplex").textContent = r.complexidade;
  $("#bBuscaCompara").textContent = r.comparacoes;
  $("#bBuscaPercorridos").textContent = r.elementos_percorridos;
  $("#bBuscaTotal").textContent = r.total_sessoes;
  $("#explicacaoBusca").innerHTML =
    `<b style="color:#39d353">${r.algoritmo}:</b> ${r.explicacao}<br>` +
    `Chave de busca: campo <b>${r.campo}</b> = <b>${r.valor_pesquisado}</b>. ` +
    `A busca terminou após <b>${r.comparacoes}</b> comparação(ões), ` +
    (r.encontrado
      ? `localizando o registro no índice ${r.indice}.`
      : `percorrendo toda a lista — item não encontrado (pior caso).`) +
    (r.ordenacao_previa
      ? `<br>Pré-requisito da busca binária: lista ordenada antes (Merge Sort = ${r.ordenacao_previa.comparacoes} comparações).`
      : "");

  $("#resultadoBusca").innerHTML = r.encontrado
    ? `<div class="resultado-card">
         <h4>Sessão encontrada no índice ${r.indice}</h4>
         <p class="texto"><b>ID:</b> ${r.sessao.id} &nbsp; <b>Veículo:</b> ${r.sessao.veiculo}
         &nbsp; <b>Placa:</b> ${r.sessao.placa}<br>
         <b>Início:</b> ${r.sessao.data_inicio_fmt} &nbsp; <b>Energia:</b> ${r.sessao.kwh} kWh
         &nbsp; <b>Custo:</b> ${moeda(r.sessao.custo_total)}<br>
         <b>Faixa tarifária:</b> ${r.sessao.faixa_tarifaria} &nbsp;
         <b>R$/kWh:</b> ${moeda(r.sessao.tarifa_kwh)} &nbsp;
         <b>Potência média:</b> ${r.sessao.potencia_media} kW</p>
       </div>`
    : `<div class="vazio">Nenhuma sessão com ${r.campo} = "${r.valor_pesquisado}".</div>`;
});

$("#btnOrdenar").addEventListener("click", async () => {
  const r = await api.send("/api/ordenar", "POST", {
    campo: $("#campoOrdem").value,
    algoritmo: $("#algoritmoOrdem").value,
    reverse: $("#direcaoOrdem").value === "desc",
  });
  $("#metricasOrdem").hidden = false;
  $("#bOrdAlgoritmo").textContent = r.algoritmo;
  $("#bOrdComplex").textContent = r.complexidade;
  $("#bOrdCompara").textContent = r.comparacoes;
  $("#bOrdTrocas").textContent = r.trocas;
  $("#bOrdPassadas").textContent = r.passadas;
  $("#bOrdTam").textContent = r.tamanho;
  $("#explicacaoOrdem").innerHTML =
    `<b style="color:#39d353">${r.algoritmo} — ${r.complexidade}:</b> ${r.complexidade_explicacao}<br>` +
    `Campo de ordenação: <b>${r.campo}</b> (${r.direcao}). ` +
    `Comparações reais executadas: <b>${r.comparacoes}</b> para <b>${r.tamanho}</b> sessões.`;
  $("#tabelaOrdem tbody").innerHTML = r.lista_ordenada
    .map(
      (s, i) => `<tr><td>${i + 1}</td><td>${s.id}</td><td>${s.veiculo} (${s.placa})</td>
        <td>${s.data_inicio_fmt}</td><td>${s.duracao_min}</td><td>${s.kwh}</td>
        <td>${moeda(s.custo_total)}</td></tr>`
    )
    .join("");
});

async function carregarStats() {
  const r = await api.get("/api/estatisticas");
  if (r.mensagem) return;
  $("#kpiStats").innerHTML = `
    <div><b>${r.total}</b><span>sessões armazenadas</span></div>
    <div><b>${brl(r.kwh_total)} kWh</b><span>energia total</span></div>
    <div><b>${moeda(r.custo_total)}</b><span>custo total</span></div>
    <div><b>${r.media_kwh} kWh</b><span>consumo médio</span></div>
    <div><b>${r.mediana_kwh} kWh</b><span>mediana (O(n log n))</span></div>
    <div><b>${moeda(r.media_custo)}</b><span>custo médio</span></div>
    <div><b>${r.media_duracao} min</b><span>duração média</span></div>
    <div><b>${r.maior_sessao.kwh} kWh</b><span>maior sessão (${r.maior_sessao.placa})</span></div>`;

  const barras = (alvo, obj, campo) => {
    const total = Object.values(obj).reduce((a, b) => a + Number(b[campo]), 0) || 1;
    alvo.innerHTML = Object.entries(obj)
      .map(
        ([nome, v]) => `<div class="barra">
          <div class="nome"><span>${nome} — ${v.sessoes} sessão(ões)</span>
          <span>${brl(v[campo])}</span></div>
          <div class="trilho"><div class="fill" style="width:${(v[campo] / total) * 100}%"></div></div>
        </div>`
      )
      .join("");
  };
  barras($("#faixaStats"), r.por_faixa, "custo");
  barras($("#estacaoStats"), r.por_estacao, "kwh");
  $("#textoStats").innerHTML = `<b style="color:#39d353">Complexidade:</b> ${r.complexidade}`;
}
$("#btnStats").addEventListener("click", carregarStats);

async function carregarRelatorio() {
  const r = await api.get("/api/relatorio");
  if (r.mensagem) return;
  $("#kpiRelatorio").innerHTML = `
    <div><b>${r.total_sessoes}</b><span>sessões no período</span></div>
    <div><b>${brl(r.kwh_total)} kWh</b><span>energia total</span></div>
    <div><b>${moeda(r.custo_total)}</b><span>faturamento total</span></div>
    <div><b>${moeda(r.custo_ponta)}</b><span>gerado em horário de ponta</span></div>
    <div><b>${moeda(r.economia_valle)}</b><span>economia em horário válle</span></div>
    <div><b>${r.duracao_media} min</b><span>duração média</span></div>`;

  $("#topVeiculos").innerHTML = `<table><thead><tr>
      <th>Veículo</th><th>Sessões</th><th>kWh</th><th>Custo</th></tr></thead><tbody>` +
    r.top_veiculos
      .map((v) => `<tr><td>${v.veiculo}</td><td>${v.sessoes}</td><td>${brl(v.kwh)}</td>
        <td>${moeda(v.custo)}</td></tr>`)
      .join("") + `</tbody></table>`;

  $("#obsRelatorio").innerHTML =
    `<b>Período:</b> ${r.periodo_inicio} até ${r.periodo_fim}<br><br>${r.observacao}`;

  const total = Object.values(r.por_faixa).reduce((a, b) => a + b.custo, 0) || 1;
  $("#faixaRelatorio").innerHTML = Object.entries(r.por_faixa)
    .map(
      ([nome, v]) => `<div class="barra">
        <div class="nome"><span>Faixa ${nome} — ${v.sessoes} sessão(ões)</span>
        <span>${moeda(v.custo)}</span></div>
        <div class="trilho"><div class="fill" style="width:${(v.custo / total) * 100}%"></div></div>
      </div>`
    )
    .join("");
}
$("#btnRelatorio").addEventListener("click", async () => {
  const resp = await api.send("/api/tarifa", "POST", {
    tarifa_base: parseFloat($("#precoKwh").value),
    taxa_servico: parseFloat($("#taxaSessao").value),
  });
  if (resp.erro) return alert(resp.erro);
  alert(
    `Tarifa atualizada no backend Python!\n` +
      `Base: R$ ${resp.tarifa_base.toFixed(2)}/kWh | Taxa: R$ ${resp.taxa_servico.toFixed(2)}\n` +
      `Faixas: normal R$ ${resp.faixas.normal.toFixed(2)} | ` +
      `ponta R$ ${resp.faixas.ponta.toFixed(2)} | válle R$ ${resp.faixas.valle.toFixed(2)}\n` +
      `${resp.sessoes_recalculadas} sessões recalculadas em O(n).`
  );
  await carregarRelatorio();
  carregarSessoes();
});

async function carregarComplexidade() {
  const r = await api.get("/api/complexidade");
  $("#tabelaComplex tbody").innerHTML = r.operacoes
    .map(
      (o) => `<tr><td><code>${o.local}</code></td><td>${o.acao}</td>
        <td><b style="color:#f0a35e">${o.complexidade}</b></td><td>${o.situacao}</td></tr>`
    )
    .join("");
}

carregarSessoes();
