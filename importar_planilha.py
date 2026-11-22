"""Importa abas de uma planilha Excel para o APPY Dashboard.
Uso: python importar_planilha.py caminho/APPY.xlsx [--limpar]
Por segurança, o padrão acrescenta registros; --limpar apaga os registros atuais antes de importar.
"""
import re
import sys
import unicodedata
from pathlib import Path
import openpyxl
from app import app, db, Produto


def normalizar(valor):
    texto = str(valor or "").strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^A-Z0-9]+", " ", texto).strip()


def inteiro(valor):
    if valor is None or str(valor).strip() == "":
        return 0
    try:
        n = float(str(valor).replace(",", "."))
        return max(0, int(n))
    except (TypeError, ValueError):
        return 0


def encontrar_coluna(cabecalhos, alternativas):
    for i, h in enumerate(cabecalhos):
        for alt in alternativas:
            if alt in h:
                return i
    return None


def valor_coluna(linha, indice, padrao=None):
    return linha[indice] if indice is not None and indice < len(linha) else padrao


def main(caminho, limpar=False):
    caminho = Path(caminho)
    if not caminho.is_file():
        raise FileNotFoundError(f"Planilha não encontrada: {caminho}")
    wb = openpyxl.load_workbook(caminho, data_only=True, read_only=True)
    inseridos = 0
    abas_lidas = 0
    with app.app_context():
        db.create_all()
        if limpar:
            Produto.query.delete()
        for ws in wb.worksheets:
            linhas = ws.iter_rows(values_only=True)
            header_row = None
            cabecalhos = None
            for numero, row in enumerate(linhas, start=1):
                normalizados = [normalizar(v) for v in row]
                tem_codigo = any(h == "COD" or h.startswith("COD ") or h == "CODIGO" for h in normalizados)
                tem_produto = any("PRODUTO" in h or h == "NOME" for h in normalizados)
                if tem_codigo and tem_produto:
                    header_row, cabecalhos = numero, normalizados
                    break
            if not header_row:
                continue
            abas_lidas += 1
            indices = {
                "codigo": encontrar_coluna(cabecalhos, ["CODIGO", "COD"]),
                "nome": encontrar_coluna(cabecalhos, ["NOME DOS PRODUTOS", "NOME DO PRODUTO", "PRODUTO"]),
                "entradas": encontrar_coluna(cabecalhos, ["ENTRADAS"]),
                "devolvido": encontrar_coluna(cabecalhos, ["DEVOLVIDO"]),
                "nao_devolvido": encontrar_coluna(cabecalhos, ["NAO DEVOLVIDO"]),
                "reformar": encontrar_coluna(cabecalhos, ["REFORMAR"]),
                "estoque": encontrar_coluna(cabecalhos, ["RDA ESTOQUE", "ESTOQUE"]),
                "descarte": encontrar_coluna(cabecalhos, ["DESCARTE"]),
            }
            if indices["nome"] is None:
                continue
            for row in ws.iter_rows(min_row=header_row + 1, values_only=True):
                nome_valor = valor_coluna(row, indices["nome"])
                if nome_valor is None or not str(nome_valor).strip():
                    continue
                codigo_valor = valor_coluna(row, indices["codigo"])
                item = Produto(
                    codigo=inteiro(codigo_valor) if codigo_valor not in (None, "") else None,
                    nome=str(nome_valor).strip(), setor=ws.title.strip().upper() or "SEM SETOR",
                    entradas=inteiro(valor_coluna(row, indices["entradas"])),
                    devolvido=inteiro(valor_coluna(row, indices["devolvido"])),
                    nao_devolvido=inteiro(valor_coluna(row, indices["nao_devolvido"])),
                    reformar=inteiro(valor_coluna(row, indices["reformar"])),
                    estoque=inteiro(valor_coluna(row, indices["estoque"])),
                    descarte=inteiro(valor_coluna(row, indices["descarte"])),
                )
                db.session.add(item)
                inseridos += 1
        if abas_lidas == 0:
            db.session.rollback()
            raise ValueError("Nenhuma aba com cabeçalho reconhecido. Confira se existem colunas COD e PRODUTO.")
        db.session.commit()
    wb.close()
    print(f"Importação concluída: {inseridos} registro(s), em {abas_lidas} aba(s).")
    if not inseridos:
        print("Atenção: nenhum produto foi importado; confira os nomes das colunas e os dados da planilha.")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Uso: python importar_planilha.py APPY.xlsx [--limpar]")
        raise SystemExit(0 if len(sys.argv) >= 2 else 2)
    try:
        main(sys.argv[1], limpar="--limpar" in sys.argv[2:])
    except Exception as exc:
        print(f"ERRO: {exc}")
        raise SystemExit(1)
