r"""
Extrai a lista de produtos de TABELA.xls (Desktop) e salva um dados.json
pronto pro gerador de HTML consumir.

Planilha "Planilha1", cabeçalho na linha 3 (índice 2), dados a partir da
linha 4 (índice 3): B=código, C=produto, D=peso caixa, E=comissão %,
F=preço quilo, G=comissão quilo, H=comissão caixa. Já vem ordenada por
Comissão Caixa decrescente na própria planilha — mantém essa ordem.
"""

import json
import os

import xlrd

CAMINHO_TABELA = r"C:\Users\edmar\Desktop\TABELA.xls"

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
CAMINHO_SAIDA = os.path.join(PASTA_BASE, "dados.json")


def _num(v):
    return v if isinstance(v, (int, float)) else 0


def extrair():
    wb = xlrd.open_workbook(CAMINHO_TABELA)
    ws = wb.sheet_by_index(0)

    produtos = []
    for r in range(3, ws.nrows):
        codigo = ws.cell_value(r, 1)
        if codigo == "":
            continue
        produtos.append({
            "codigo": int(codigo),
            "produto": str(ws.cell_value(r, 2)).strip(),
            "peso_caixa": _num(ws.cell_value(r, 3)),
            "comissao_pct": _num(ws.cell_value(r, 4)),
            "preco_quilo": _num(ws.cell_value(r, 5)),
            "comissao_quilo": _num(ws.cell_value(r, 6)),
            "comissao_caixa": _num(ws.cell_value(r, 7)),
        })
    return produtos


def main():
    produtos = extrair()
    with open(CAMINHO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(produtos, f, ensure_ascii=False, indent=2)
    print(f"{len(produtos)} produtos extraídos. Salvo em: {CAMINHO_SAIDA}")


if __name__ == "__main__":
    main()
