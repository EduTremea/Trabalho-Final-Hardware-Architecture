// Atualiza o painel a cada 2 segundos e envia os comandos para a API

const NOMES = { 0: "NORMAL", 1: "ATENÇÃO", 2: "TEMPESTADE" };
let configAtual = null;
let formEditado = false;

const $ = (id) => document.getElementById(id);

function hora(ts) {
  return new Date(ts * 1000).toLocaleTimeString("pt-BR");
}

function dataHora(ts) {
  return new Date(ts * 1000).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "medium" });
}

async function api(caminho, dados) {
  const opcoes = dados
    ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(dados) }
    : {};
  const resposta = await fetch(caminho, opcoes);
  const corpo = await resposta.json();
  if (!resposta.ok) throw new Error(corpo.erro || "erro na requisição");
  return corpo;
}

// ---------- gráficos ----------

function criarGrafico(id, series, eixos) {
  return new Chart($(id), {
    type: "line",
    data: { labels: [], datasets: series.map((s) => ({ ...s, data: [], pointRadius: 0, borderWidth: 2, tension: 0.25 })) },
    options: {
      animation: false,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      scales: eixos,
      plugins: { legend: { labels: { boxWidth: 12 } } },
    },
  });
}

const graficoChuva = criarGrafico(
  "graficoChuva",
  [{ label: "Chuva", borderColor: "#2f6fd6", yAxisID: "y", fill: true, backgroundColor: "rgba(47,111,214,0.12)" }],
  { x: { ticks: { maxTicksLimit: 8 } }, y: { min: 0, max: 1023 } }
);

const graficoClima = criarGrafico(
  "graficoClima",
  [
    { label: "Temperatura (°C)", borderColor: "#d6323a", yAxisID: "y" },
    { label: "Umidade (%)", borderColor: "#1f9d55", yAxisID: "y2" },
  ],
  {
    x: { ticks: { maxTicksLimit: 8 } },
    y: { position: "left", title: { display: true, text: "°C" } },
    y2: { position: "right", min: 0, max: 100, grid: { drawOnChartArea: false }, title: { display: true, text: "%" } },
  }
);

// ---------- atualização ----------

async function atualizarEstado() {
  try {
    const { leitura, online, config } = await api("/api/estado");
    configAtual = config;

    $("conexao").textContent = online ? "Arduino online" : "Arduino offline";
    $("conexao").className = "chip " + (online ? "online" : "offline");

    const faixa = $("faixa");
    if (!leitura) {
      faixa.className = "faixa nivel-off";
      $("nivel").textContent = "Sem dados";
      return;
    }

    faixa.className = "faixa " + (online ? "nivel-" + leitura.nivel : "nivel-off");
    $("nivel").textContent = NOMES[leitura.nivel];
    $("pontos").textContent = `${leitura.pontos} ponto(s) de risco · ${hora(leitura.ts)}`;
    $("aparelhos").textContent = leitura.rele ? "LIGADOS" : "DESLIGADOS";
    $("modo").textContent = config.modo === "auto" ? "modo automático" : "modo manual";

    $("temp").textContent = leitura.temp ?? "falha";
    $("umid").textContent = leitura.umid ?? "falha";
    $("chuva").textContent = leitura.chuva;

    document.querySelectorAll(".alternar").forEach((b) => b.classList.toggle("ativo", b.dataset.modo === config.modo));
    if (!formEditado) preencherLimites(config);
  } catch (erro) {
    $("conexao").textContent = "Servidor sem resposta";
    $("conexao").className = "chip offline";
  }
}

async function atualizarHistorico() {
  const minutos = $("periodo").value;
  const leituras = await api(`/api/historico?minutos=${minutos}`);

  // em períodos longos, pega uma leitura a cada N para não pesar o gráfico
  const passo = Math.max(1, Math.ceil(leituras.length / 600));
  const pontos = leituras.filter((_, i) => i % passo === 0);
  const rotulos = pontos.map((l) => hora(l.ts));

  graficoChuva.data.labels = rotulos;
  graficoChuva.data.datasets[0].data = pontos.map((l) => l.chuva);
  graficoChuva.update();

  graficoClima.data.labels = rotulos;
  graficoClima.data.datasets[0].data = pontos.map((l) => l.temp);
  graficoClima.data.datasets[1].data = pontos.map((l) => l.umid);
  graficoClima.update();
}

async function atualizarEventos() {
  const eventos = await api("/api/eventos");
  $("eventos").innerHTML = eventos
    .map((e) => `<tr class="ev-${e.tipo}"><td>${dataHora(e.ts)}</td><td>${e.descricao}</td></tr>`)
    .join("");
}

function preencherLimites(config) {
  const form = $("formLimites");
  for (const nome of ["limite_chuva", "subida_umidade", "janela_s", "religar_apos_s"]) {
    form.elements[nome].value = config[nome];
  }
  form.elements.exigir_queda_temp.checked = config.exigir_queda_temp;
}

async function atualizarTudo() {
  await atualizarEstado();
  try {
    await Promise.all([atualizarHistorico(), atualizarEventos()]);
  } catch (erro) {
    // servidor fora do ar; o chip de conexão já avisa
  }
}

// ---------- comandos ----------

document.querySelectorAll(".alternar").forEach((botao) =>
  botao.addEventListener("click", async () => {
    await api("/api/modo", { modo: botao.dataset.modo });
    atualizarTudo();
  })
);

$("ligar").addEventListener("click", async () => {
  await api("/api/rele", { ligado: true });
  atualizarTudo();
});

$("desligar").addEventListener("click", async () => {
  await api("/api/rele", { ligado: false });
  atualizarTudo();
});

$("formLimites").addEventListener("input", () => (formEditado = true));

$("formLimites").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const form = evento.target;
  const dados = { exigir_queda_temp: form.elements.exigir_queda_temp.checked };
  for (const nome of ["limite_chuva", "subida_umidade", "janela_s", "religar_apos_s"]) {
    dados[nome] = Number(form.elements[nome].value);
  }
  try {
    await api("/api/limites", dados);
    $("msgLimites").textContent = "Limites salvos.";
    formEditado = false;
  } catch (erro) {
    $("msgLimites").textContent = erro.message;
  }
  atualizarTudo();
});

$("periodo").addEventListener("change", atualizarHistorico);

atualizarTudo();
setInterval(atualizarTudo, 2000);
