r"""
Gera o painel "Tabela de Comissão" (painel.html) a partir de dados.json —
lista de produtos ordenável/filtrável, ordenada por padrão pela Comissão
Caixa (o que mais vale a pena empurrar na venda).
"""

import datetime
import json
import os

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DADOS = os.path.join(PASTA_BASE, "dados.json")
CAMINHO_SAIDA = os.path.join(PASTA_BASE, "painel.html")


def gerar_html(produtos):
    data_extracao = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    dados_json = json.dumps(produtos, ensure_ascii=False)

    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tabela de Comissão — Equipe GYN</title>
<style>
  :root {{
    --bg: #0B0D12;
    --surface: #12151C;
    --surface-2: #171B24;
    --border: #262B36;
    --ink: #F2F3F5;
    --ink-soft: #9AA1AE;
    --ink-faint: #6B7280;
    --accent: #4F8CFF;
    --good: #2FBF71;
    --warn: #E0A72E;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: ui-sans-serif, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  .wrap {{ max-width: 980px; margin: 0 auto; padding: 32px 20px 64px; }}
  header {{ margin-bottom: 20px; }}
  header h1 {{ margin: 0 0 6px; font-size: 26px; font-weight: 800; letter-spacing: -0.01em; }}
  header p {{ margin: 0; color: var(--ink-soft); font-size: 14px; }}

  .barra {{
    display: flex; gap: 10px; align-items: center; margin-bottom: 16px;
    flex-wrap: wrap;
  }}
  .barra input {{
    flex: 1; min-width: 220px;
    background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
    color: var(--ink); font-size: 14px; padding: 10px 14px;
  }}
  .barra input:focus {{ outline: none; border-color: var(--accent); }}
  .barra .contagem {{ color: var(--ink-faint); font-size: 13px; white-space: nowrap; }}

  .tabela-wrap {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
    overflow: auto;
  }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13.5px; min-width: 760px; }}
  thead th {{
    position: sticky; top: 0; background: var(--surface-2);
    text-align: right; padding: 10px 12px; font-weight: 700; font-size: 11.5px;
    text-transform: uppercase; letter-spacing: 0.04em; color: var(--ink-faint);
    border-bottom: 1px solid var(--border); cursor: pointer; white-space: nowrap;
  }}
  thead th:first-child, thead th:nth-child(2) {{ text-align: left; }}
  thead th:hover {{ color: var(--ink); }}
  thead th .seta {{ font-size: 10px; margin-left: 3px; color: var(--accent); }}
  tbody td {{
    padding: 9px 12px; border-bottom: 1px solid var(--border); text-align: right;
    white-space: nowrap;
  }}
  tbody td:first-child, tbody td:nth-child(2) {{ text-align: left; }}
  tbody td:nth-child(2) {{ white-space: normal; min-width: 220px; }}
  tbody tr:hover {{ background: var(--surface-2); }}
  tbody tr:last-child td {{ border-bottom: none; }}
  .cod {{ color: var(--ink-faint); font-variant-numeric: tabular-nums; }}
  .destaque {{ color: var(--good); font-weight: 700; }}

  footer {{ text-align: center; margin-top: 24px; font-size: 11.5px; color: var(--ink-faint); }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Tabela de Comissão</h1>
    <p>Ranking de produtos por comissão — toque no cabeçalho pra reordenar</p>
  </header>

  <div class="barra">
    <input type="text" id="busca" placeholder="Buscar por código ou produto...">
    <span class="contagem" id="contagem"></span>
  </div>

  <div class="tabela-wrap">
    <table>
      <thead>
        <tr>
          <th data-col="codigo">Código</th>
          <th data-col="produto">Produto</th>
          <th data-col="peso_caixa">Peso Caixa</th>
          <th data-col="comissao_pct">Comissão %</th>
          <th data-col="preco_quilo">Preço Quilo</th>
          <th data-col="comissao_quilo">Comissão Quilo</th>
          <th data-col="comissao_caixa">Comissão Caixa</th>
        </tr>
      </thead>
      <tbody id="corpo"></tbody>
    </table>
  </div>

  <footer>Dados extraídos de TABELA.xls · gerado automaticamente em {data_extracao}</footer>
</div>

<script>
const DADOS = {dados_json};

let ordem = {{ col: "comissao_caixa", dir: -1 }};

function fmtNum(v, casas) {{
  return Number(v).toLocaleString("pt-BR", {{ minimumFractionDigits: casas, maximumFractionDigits: casas }});
}}
function fmtMoeda(v) {{ return "R$ " + fmtNum(v, 2); }}
function fmtPct(v) {{ return fmtNum(v * 100, 2) + "%"; }}

function normalizar(s) {{
  return String(s).normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").toUpperCase();
}}

function renderizar() {{
  const termo = normalizar(document.getElementById("busca").value.trim());
  let linhas = DADOS.filter(p =>
    !termo || normalizar(p.produto).includes(termo) || String(p.codigo).includes(termo)
  );
  linhas.sort((a, b) => {{
    const va = a[ordem.col], vb = b[ordem.col];
    if (typeof va === "string") return va.localeCompare(vb) * ordem.dir;
    return (va - vb) * ordem.dir;
  }});

  document.getElementById("contagem").textContent = linhas.length + " produto(s)";

  document.getElementById("corpo").innerHTML = linhas.map(p => `
    <tr>
      <td class="cod">${{p.codigo}}</td>
      <td>${{p.produto}}</td>
      <td>${{fmtNum(p.peso_caixa, 2)}} kg</td>
      <td>${{fmtPct(p.comissao_pct)}}</td>
      <td>${{fmtMoeda(p.preco_quilo)}}</td>
      <td>${{fmtMoeda(p.comissao_quilo)}}</td>
      <td class="destaque">${{fmtMoeda(p.comissao_caixa)}}</td>
    </tr>
  `).join("");

  document.querySelectorAll("thead th").forEach(th => {{
    const base = th.textContent.replace(/\\s*[▲▼]\\s*$/, "");
    th.innerHTML = base + (th.dataset.col === ordem.col ? `<span class="seta">${{ordem.dir === 1 ? "▲" : "▼"}}</span>` : "");
  }});
}}

document.getElementById("busca").addEventListener("input", renderizar);

document.querySelectorAll("thead th").forEach(th => {{
  th.addEventListener("click", () => {{
    const col = th.dataset.col;
    if (ordem.col === col) {{
      ordem.dir *= -1;
    }} else {{
      ordem.col = col;
      ordem.dir = col === "produto" || col === "codigo" ? 1 : -1;
    }}
    renderizar();
  }});
}});

renderizar();
</script>
</body>
</html>
'''


def main():
    with open(CAMINHO_DADOS, "r", encoding="utf-8") as f:
        produtos = json.load(f)

    html = gerar_html(produtos)
    with open(CAMINHO_SAIDA, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Painel gerado em: {CAMINHO_SAIDA}")


if __name__ == "__main__":
    main()
