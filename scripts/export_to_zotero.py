"""
export_to_zotero.py  (versao unificada)
-----------------------------------------
Le todos os corpora gerados no projeto e produz um BibTeX mestre:
  references/BIBLIOGRAFIA_MESTRE_IA_EDU.bib

Corpora e tags:
  Global_Empirical   — data/processed/meta_analysis_matrix.csv
  Global_Theoretical — data/raw/theoretical_papers.json
  Brazil_Context     — data/processed/brazil_mapping.csv
"""

import csv
import json
import re
from datetime import datetime
from pathlib import Path

# -- Caminhos ------------------------------------------------------------------
BASE_DIR    = Path(__file__).resolve().parent.parent
META_CSV    = BASE_DIR / "data" / "processed" / "meta_analysis_matrix.csv"
THEORY_JSON = BASE_DIR / "data" / "raw"       / "theoretical_papers.json"
BRAZIL_CSV  = BASE_DIR / "data" / "processed" / "brazil_mapping.csv"
OUT_BIB     = BASE_DIR / "references" / "BIBLIOGRAFIA_MESTRE_IA_EDU.bib"


# -- Helpers -------------------------------------------------------------------
def load_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def make_key(uid: str, title: str, year: str) -> str:
    words = [w for w in re.split(r'\W+', title) if len(w) > 3]
    kw = words[0].capitalize() if words else "AI"
    safe = re.sub(r'[^A-Za-z0-9]', '', uid)[:10]
    return f"{safe}_{year}_{kw}"

def bib_escape(text: str) -> str:
    text = (text or "").replace("\\", "").replace('"', "''")
    # Preserve & in journal names inside braces
    return text

def make_entry(uid, title, year, journal, authors, abstract, keywords_list, corpus_tag) -> str:
    key = make_key(uid, title, str(year or "0000"))

    if isinstance(authors, list):
        author_str = " and ".join(a for a in authors[:5] if a) or "Author(s) to be verified"
    else:
        author_str = str(authors or "Author(s) to be verified")

    kw_full = ", ".join([corpus_tag] + [k for k in (keywords_list or []) if k.strip()])

    fields = {
        "title":    bib_escape(title    or ""),
        "author":   bib_escape(author_str),
        "year":     str(year or ""),
        "journal":  bib_escape(journal  or ""),
        "abstract": bib_escape((abstract or "")[:380]),
        "keywords": bib_escape(kw_full),
        "note":     f"Corpus: {corpus_tag}",
    }
    body = "\n".join(f"  {k:<10} = {{{v}}}," for k, v in fields.items())
    return f"@article{{{key},\n{body}\n}}"


# -- Corpus 1: Global_Empirical ------------------------------------------------
def entries_global_empirical(rows: list[dict]) -> list[str]:
    out = []
    for r in rows:
        kws = [
            r.get("methodology_type", ""),
            r.get("ai_type", ""),
            r.get("main_finding_direction", ""),
            "Inequity" if r.get("inequity","").lower() in ("true","1") else "",
            "Ethics"   if r.get("ethics","").lower()   in ("true","1") else "",
        ]
        out.append(make_entry(
            uid=r.get("paper_id",""),
            title=r.get("title",""),
            year=r.get("year",""),
            journal=r.get("venue",""),
            authors=r.get("authors","Author(s) to be verified"),
            abstract=r.get("abstract",""),
            keywords_list=kws,
            corpus_tag="Global_Empirical",
        ))
    return out


# -- Corpus 2: Global_Theoretical ----------------------------------------------
def entries_global_theoretical(papers: list[dict]) -> list[str]:
    out = []
    for p in papers:
        pub = " | ".join(p.get("publication_types") or [])
        kws = ["Theoretical", pub,
               "OpenAccess" if p.get("open_access") else ""]
        out.append(make_entry(
            uid=p.get("paper_id",""),
            title=p.get("title",""),
            year=p.get("year",""),
            journal=p.get("venue",""),
            authors=p.get("authors",[]),
            abstract=p.get("abstract",""),
            keywords_list=kws,
            corpus_tag="Global_Theoretical",
        ))
    return out


# -- Corpus 3: Brazil_Context --------------------------------------------------
def entries_brazil(rows: list[dict]) -> list[str]:
    out = []
    for r in rows:
        themes = [t.strip() for t in r.get("themes","").split("|") if t.strip()]
        kws = [r.get("doc_type",""), r.get("institution_br","")] + themes[:3]
        out.append(make_entry(
            uid=r.get("paper_id",""),
            title=r.get("title",""),
            year=r.get("year",""),
            journal=r.get("venue",""),
            authors=r.get("authors",""),
            abstract=r.get("abstract_short",""),
            keywords_list=kws,
            corpus_tag="Brazil_Context",
        ))
    return out


# -- Main ----------------------------------------------------------------------
def main():
    now   = datetime.now().strftime("%Y-%m-%d %H:%M")

    meta_rows    = load_csv(META_CSV)
    theory_data  = load_json(THEORY_JSON) if THEORY_JSON.exists() else {"papers":[]}
    theory_papers = theory_data.get("papers", [])
    brazil_rows  = load_csv(BRAZIL_CSV)

    n1, n2, n3 = len(meta_rows), len(theory_papers), len(brazil_rows)
    total = n1 + n2 + n3

    print(f"[->] Gerando BIBLIOGRAFIA_MESTRE_IA_EDU.bib")
    print(f"     Global_Empirical   : {n1} entradas")
    print(f"     Global_Theoretical : {n2} entradas")
    print(f"     Brazil_Context     : {n3} entradas")
    print(f"     TOTAL              : {total}\n")

    # Monta cabecalho
    header_lines = [
        f"%% BIBLIOGRAFIA_MESTRE_IA_EDU.bib",
        f"%% Gerado em {now} por scripts/export_to_zotero.py",
        f"%% Total de entradas: {total}",
        f"%%",
        f"%%  Tag                  | N    | Descricao",
        f"%%  ---------------------|------|------------------------------------",
        f"%%  Global_Empirical     | {n1:<4} | Estudos empiricos internacionais",
        f"%%  Global_Theoretical   | {n2:<4} | Artigos teoricos/conceituais",
        f"%%  Brazil_Context       | {n3:<4} | Pesquisa brasileira (2020-2026)",
        f"%%",
        f"%% Importar no Zotero: File > Import > BibTeX",
        f"%% Filtrar por tag no Zotero: use a coluna 'Keywords'",
        "",
    ]

    sep1 = [
        "",
        "%% " + "═"*57,
        f"%% CORPUS 1 — Global_Empirical ({n1} artigos)",
        "%% " + "═"*57,
        "",
    ]
    sep2 = [
        "",
        "%% " + "═"*57,
        f"%% CORPUS 2 — Global_Theoretical ({n2} artigos)",
        "%% " + "═"*57,
        "",
    ]
    sep3 = [
        "",
        "%% " + "═"*57,
        f"%% CORPUS 3 — Brazil_Context ({n3} artigos)",
        "%% " + "═"*57,
        "",
    ]

    all_entries = (
        "\n".join(header_lines)
        + "\n".join(sep1)
        + "\n\n".join(entries_global_empirical(meta_rows))
        + "\n".join(sep2)
        + "\n\n".join(entries_global_theoretical(theory_papers))
        + "\n".join(sep3)
        + "\n\n".join(entries_brazil(brazil_rows))
        + "\n"
    )

    OUT_BIB.parent.mkdir(parents=True, exist_ok=True)
    OUT_BIB.write_text(all_entries, encoding="utf-8")
    size_kb = OUT_BIB.stat().st_size // 1024
    print(f"[OK] {OUT_BIB.relative_to(BASE_DIR)} ({size_kb} KB, {total} entradas)")
    print(f"\n    Para importar no Zotero:")
    print(f"    File > Import > {OUT_BIB.name}")
    print(f"    Em seguida filtre por keyword: Global_Empirical | Global_Theoretical | Brazil_Context")


if __name__ == "__main__":
    main()
