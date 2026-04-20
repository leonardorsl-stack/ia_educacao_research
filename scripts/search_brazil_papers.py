"""
search_brazil_papers.py
------------------------
Busca via Semantic Scholar por pesquisas brasileiras sobre IA na Educacao.
Termos em portugues e ingles com filtro geografico (Brasil).

Salva em data/raw/brazil_research.json com classificacao:
  - Empirico: relatos de experiencia, estudos de caso, dados institucionais
  - Teorico:  artigos de periódicos brasileiros sobre etica, soberania digital
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from pathlib import Path

# -- Caminhos ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
OUT_PATH = BASE_DIR / "data" / "raw" / "brazil_research.json"

# -- Configuracao da API -------------------------------------------------------
SS_API_BASE   = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS        = "paperId,title,year,abstract,authors,venue,publicationTypes,referenceCount,citationCount,openAccessPdf,externalIds"
YEAR_FILTER   = "2020-2026"
TARGET_COUNT  = 30
DELAY_QUERIES = 8   # segundos entre queries

# Queries em portugues + ingles com contexto brasileiro
QUERIES = [
    # Empíricos
    "Inteligencia Artificial Educacao Brasil escola",
    "IA Generativa Ensino Superior Brasil universidade",
    "artificial intelligence education Brazil empirical",
    "ChatGPT educacao brasileira escola publica",
    # Teóricos / periódicos brasileiros
    "Inteligencia Artificial educacao etica soberania digital Brasil",
    "IA educacao formacao docente Brasil BNCC inclusao digital",
    "artificial intelligence education equity Brazil social justice",
    "tecnologia educacao desigualdade digital Brasil",
]

# Periódicos brasileiros de referencia (para classificacao de relevancia)
BRAZILIAN_VENUES = {
    "educação & sociedade", "educacao & sociedade",
    "cadernos de pesquisa", "interface",
    "revista brasileira de educacao", "reveduc",
    "ensaio", "pro-posicoes", "pro-posições",
    "educação em revista", "bolema",
    "revista ibero-americana", "linhas criticas",
    "educar em revista",
}

BRAZIL_KEYWORDS = [
    "brasil", "brazil", "brazilian", "brasileiro", "brasileira",
    "mec", "cgi.br", "bncc", "escola publica", "escola pública",
    "universidade federal", "universidade estadual", "usp", "unicamp",
    "ufmg", "ufrj", "ufpe", "ufba", "unesp", "puc",
    "ensino médio", "ensino fundamental", "ensino superior",
    "formacao docente", "formação docente",
    "inclusao digital", "inclusão digital",
    "soberania digital", "desigualdade digital",
]

EMPIRICAL_KEYWORDS = [
    "study", "trial", "experiment", "survey", "case study",
    "empirical", "relato", "experiencia", "experiência",
    "dados", "escola", "universidade", "alunos", "professores",
    "questionario", "questionário", "entrevista",
]

THEORETICAL_KEYWORDS = [
    "etica", "ética", "ethics", "teorico", "teórico", "theoretical",
    "conceptual", "soberania", "sovereignty", "critica", "crítica",
    "filosofia", "philosophical", "sociologico", "sociológico",
    "discurso", "discourse", "poder", "power", "equidade",
]

# -- Helpers -------------------------------------------------------------------
def fetch_papers(query: str, limit: int = 15, max_retries: int = 5) -> list[dict]:
    """Busca com retry + backoff exponencial."""
    params = urllib.parse.urlencode({
        "query":  query,
        "limit":  limit,
        "fields": FIELDS,
        "year":   YEAR_FILTER,
    })
    url = f"{SS_API_BASE}?{params}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ia-educacao-brazil-research/1.0 (academic project)"},
    )
    wait = 10
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("data", [])
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"    [!] 429 Rate limit — aguardando {wait}s (tentativa {attempt}/{max_retries})...")
                time.sleep(wait)
                wait *= 2
            else:
                body = e.read().decode("utf-8")
                print(f"    [!] HTTP {e.code}: {body[:100]}")
                return []
        except Exception as exc:
            print(f"    [!] Erro: {exc}")
            return []
    print(f"    [!] Max retries atingido.")
    return []


def is_brazil_related(paper: dict) -> bool:
    """Verifica se o paper tem relacao com o Brasil."""
    text = " ".join([
        (paper.get("title")    or ""),
        (paper.get("abstract") or ""),
        (paper.get("venue")    or ""),
    ]).lower()
    return any(kw in text for kw in BRAZIL_KEYWORDS)


def classify_type(paper: dict) -> str:
    """Classifica o paper como Empirico ou Teorico."""
    text = " ".join([
        (paper.get("title")    or ""),
        (paper.get("abstract") or ""),
    ]).lower()
    emp_score = sum(1 for kw in EMPIRICAL_KEYWORDS  if kw in text)
    teo_score = sum(1 for kw in THEORETICAL_KEYWORDS if kw in text)
    pub_types = paper.get("publicationTypes") or []
    if "Review" in pub_types:
        teo_score += 2
    return "Empirico" if emp_score >= teo_score else "Teorico"


def is_brazilian_venue(venue: str) -> bool:
    return venue.lower().strip() in BRAZILIAN_VENUES


def infer_institution(abstract: str) -> str:
    """Tenta identificar a instituicao brasileira no abstract."""
    instits = {
        "USP": ["universidade de sao paulo", "university of são paulo", "usp"],
        "UNICAMP": ["unicamp", "universidade estadual de campinas"],
        "UFMG": ["ufmg", "universidade federal de minas gerais"],
        "UFRJ": ["ufrj", "universidade federal do rio de janeiro"],
        "UFPE": ["ufpe", "universidade federal de pernambuco"],
        "UFBA": ["ufba", "universidade federal da bahia"],
        "UNESP": ["unesp"],
        "PUC": ["puc-rio", "puc-sp", "puc-mg", "puc-rs"],
        "UNIFESP": ["unifesp"],
        "UnB": ["universidade de brasilia", "unb"],
        "UFSC": ["ufsc", "universidade federal de santa catarina"],
        "UFRGS": ["ufrgs"],
    }
    text = abstract.lower()
    found = [name for name, variants in instits.items() if any(v in text for v in variants)]
    return "; ".join(found) if found else "Nao identificada"


def normalize_paper(p: dict, query_used: str) -> dict:
    """Normaliza paper para formato de saida."""
    authors = [a.get("name", "") for a in (p.get("authors") or [])]
    abstract = p.get("abstract") or ""
    venue    = p.get("venue")    or ""
    doc_type = classify_type(p)
    return {
        "paper_id":          p.get("paperId", ""),
        "title":             p.get("title", ""),
        "year":              p.get("year"),
        "venue":             venue,
        "is_brazilian_venue": is_brazilian_venue(venue),
        "abstract":          abstract,
        "authors":           authors,
        "institution_br":    infer_institution(abstract),
        "citation_count":    p.get("citationCount", 0),
        "reference_count":   p.get("referenceCount", 0),
        "publication_types": p.get("publicationTypes") or [],
        "open_access":       bool(p.get("openAccessPdf")),
        "doc_type":          doc_type,
        "source_query":      query_used,
        "collected_at":      datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


# -- Main ----------------------------------------------------------------------
def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    seen_ids: set[str] = set()
    collected: list[dict] = []

    print("[->] Iniciando busca por pesquisas brasileiras no Semantic Scholar...")
    print(f"     Filtro: {YEAR_FILTER} | Alvo: {TARGET_COUNT} artigos\n")

    for i, query in enumerate(QUERIES, start=1):
        if len(collected) >= TARGET_COUNT:
            print(f"\n[OK] Meta de {TARGET_COUNT} artigos atingida.")
            break

        print(f"[{i}/{len(QUERIES)}] Query: {query[:70]}")
        papers = fetch_papers(query, limit=15)
        print(f"       -> {len(papers)} resultados brutos")

        new_count = 0
        for p in papers:
            pid = p.get("paperId", "")
            if not pid or pid in seen_ids:
                continue
            if not is_brazil_related(p):
                continue
            year = p.get("year")
            if year and not (2020 <= int(year) <= 2026):
                continue
            seen_ids.add(pid)
            collected.append(normalize_paper(p, query))
            new_count += 1
            if len(collected) >= TARGET_COUNT:
                break

        print(f"       -> {new_count} novos artigos brasileiros (total: {len(collected)})")

        if i < len(QUERIES) and len(collected) < TARGET_COUNT:
            print(f"       ... aguardando {DELAY_QUERIES}s...")
            time.sleep(DELAY_QUERIES)

    # Estatisticas
    empiricos = sum(1 for p in collected if p["doc_type"] == "Empirico")
    teoricos  = sum(1 for p in collected if p["doc_type"] == "Teorico")
    br_venues = sum(1 for p in collected if p["is_brazilian_venue"])

    output = {
        "metadata": {
            "description":   "Pesquisas brasileiras — IA na Educacao",
            "queries_used":  QUERIES,
            "year_filter":   YEAR_FILTER,
            "total_papers":  len(collected),
            "empiricos":     empiricos,
            "teoricos":      teoricos,
            "br_venues":     br_venues,
            "generated_at":  datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "papers": collected,
    }

    OUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n-- Resumo ---------------------------------------------------")
    print(f"   Total coletado : {len(collected)} artigos")
    print(f"   Empiricos      : {empiricos}")
    print(f"   Teoricos       : {teoricos}")
    print(f"   Periód. BR     : {br_venues}")
    print(f"   Salvo em       : {OUT_PATH.relative_to(BASE_DIR)}")

    if collected:
        print(f"\n-- Primeiros 5 artigos --------------------------------------")
        for p in collected[:5]:
            print(f"   [{p['year']}] [{p['doc_type']}] {p['title'][:65]}")
            print(f"          Venue: {p['venue'][:40] or 'N/A'} | Inst BR: {p['institution_br']}")


if __name__ == "__main__":
    main()
