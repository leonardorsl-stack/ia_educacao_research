"""
search_theoretical_papers.py
------------------------------
Busca artigos teoricos/conceituais via API do Semantic Scholar focados em:
  ('Artificial Intelligence' OR 'Generative AI') AND ('Education') AND
  ('Critical Theory' OR 'Sociological Perspective' OR 'Ethics')

Filtra por publicacoes do tipo Review ou JournalArticle (2020-2026).
Salva os resultados em data/raw/theoretical_papers.json.

Implementa retry com backoff exponencial para contornar rate limit (HTTP 429).
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
OUT_PATH = BASE_DIR / "data" / "raw" / "theoretical_papers.json"

# -- Configuracao da API -------------------------------------------------------
SS_API_BASE  = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS       = "paperId,title,year,abstract,authors,venue,publicationTypes,referenceCount,citationCount,openAccessPdf"
YEAR_FILTER  = "2020-2026"
TARGET_COUNT = 30   # numero maximo de artigos desejados
DELAY_BETWEEN_QUERIES = 6  # segundos entre queries para evitar 429

# Consultas sequenciais — cobrindo o escopo teorico/conceitual
QUERIES = [
    'Artificial Intelligence Education "Critical Theory"',
    'Generative AI Education Ethics "Sociological"',
    'AI Education "Critical Pedagogy" "Social Justice"',
    '"Artificial Intelligence" Education Ethics "Theoretical Framework"',
    '"Generative AI" Education "Philosophical" "Conceptual"',
]

# -- Helpers -------------------------------------------------------------------
def fetch_papers(query: str, limit: int = 15, max_retries: int = 4) -> list[dict]:
    """Chama a API do Semantic Scholar com retry + backoff exponencial para 429."""
    params = urllib.parse.urlencode({
        "query":            query,
        "limit":            limit,
        "fields":           FIELDS,
        "year":             YEAR_FILTER,
        "publicationTypes": "Review,JournalArticle",
    })
    url = f"{SS_API_BASE}?{params}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ia-educacao-research/1.0 (academic project)"},
    )
    wait = 8  # segundos iniciais de espera em caso de 429
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("data", [])
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"  [!] 429 Rate limit — aguardando {wait}s (tentativa {attempt}/{max_retries})...")
                time.sleep(wait)
                wait *= 2  # backoff: 8 -> 16 -> 32 -> 64 s
            else:
                body = e.read().decode("utf-8")
                print(f"  [!] HTTP {e.code} para query '{query[:50]}': {body[:120]}")
                return []
        except Exception as exc:
            print(f"  [!] Erro na query '{query[:50]}': {exc}")
            return []
    print(f"  [!] Maximo de retries atingido para '{query[:50]}'")
    return []


def is_theoretical(paper: dict) -> bool:
    """
    Heuristica para identificar artigos conceituais/teoricos:
    - Abstract ou titulo menciona palavras-chave teoricas, OU
    - Tipo de publicacao e Review
    """
    abstract = (paper.get("abstract") or "").lower()
    title    = (paper.get("title")    or "").lower()
    theory_keywords = [
        "critical theory", "sociolog", "philosophical", "conceptual",
        "theoretical", "ethics", "equity", "social justice", "critical pedagogy",
        "discourse", "power", "hegemony", "intersectionality", "epistemolog",
        "normative", "ethical framework", "digital divide", "datafication",
        "surveillance", "algorithmic", "bias", "fairness", "accountability",
    ]
    text_hit  = any(kw in abstract or kw in title for kw in theory_keywords)
    is_review = "Review" in (paper.get("publicationTypes") or [])
    return text_hit or is_review


def normalize_paper(p: dict, query_used: str) -> dict:
    """Normaliza e enriquece um paper do Semantic Scholar para o formato de saida."""
    authors = [a.get("name", "") for a in (p.get("authors") or [])]
    return {
        "paper_id":          p.get("paperId", ""),
        "title":             p.get("title", ""),
        "year":              p.get("year"),
        "venue":             p.get("venue", ""),
        "abstract":          p.get("abstract", ""),
        "authors":           authors,
        "citation_count":    p.get("citationCount", 0),
        "reference_count":   p.get("referenceCount", 0),
        "publication_types": p.get("publicationTypes") or [],
        "open_access":       bool(p.get("openAccessPdf")),
        "source_query":      query_used,
        "paper_type":        "Theoretical / Conceptual",
        "collected_at":      datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


# -- Main ----------------------------------------------------------------------
def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    seen_ids: set[str] = set()
    collected: list[dict] = []

    print("[->] Iniciando busca no Semantic Scholar...")
    print(f"     Filtro: {YEAR_FILTER} | Tipos: Review, JournalArticle\n")

    for i, query in enumerate(QUERIES, start=1):
        if len(collected) >= TARGET_COUNT:
            print(f"\n[OK] Meta de {TARGET_COUNT} artigos atingida. Encerrando.")
            break

        print(f"[{i}/{len(QUERIES)}] Query: {query[:70]}")
        papers = fetch_papers(query, limit=15)
        print(f"       -> {len(papers)} resultados brutos recebidos")

        new_count = 0
        for p in papers:
            pid = p.get("paperId", "")
            if not pid or pid in seen_ids:
                continue
            if not is_theoretical(p):
                continue
            year = p.get("year")
            if year and not (2020 <= int(year) <= 2026):
                continue
            seen_ids.add(pid)
            collected.append(normalize_paper(p, query))
            new_count += 1
            if len(collected) >= TARGET_COUNT:
                break

        print(f"       -> {new_count} novos artigos adicionados (total acumulado: {len(collected)})")

        if i < len(QUERIES) and len(collected) < TARGET_COUNT:
            print(f"       ... aguardando {DELAY_BETWEEN_QUERIES}s para proxima query...")
            time.sleep(DELAY_BETWEEN_QUERIES)

    # Salva resultado
    output = {
        "metadata": {
            "description":  "Artigos teoricos/conceituais — IA na Educacao",
            "queries_used": QUERIES,
            "year_filter":  YEAR_FILTER,
            "pub_types":    ["Review", "JournalArticle"],
            "total_papers": len(collected),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "papers": collected,
    }

    OUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n-- Resumo ---------------------------------------------------")
    print(f"   Artigos coletados : {len(collected)}")
    print(f"   Arquivo salvo em  : {OUT_PATH.relative_to(BASE_DIR)}")

    if collected:
        print(f"\n-- Primeiros 5 titulos --------------------------------------")
        for p in collected[:5]:
            authors_str = ", ".join(p["authors"][:2]) or "N/A"
            print(f"   [{p['year']}] {p['title'][:75]}")
            print(f"          Venue: {p['venue'] or 'N/A'} | Cit.: {p['citation_count']}")


if __name__ == "__main__":
    main()
