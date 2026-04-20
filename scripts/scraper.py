#!/usr/bin/env python3
# =============================================================================
# Script: scraper.py
# Autor: Equipe de Pesquisa — IA na Educação
# Data: 2026-04-20
# Finalidade Sociológica: Coleta bibliométrica em bases indexadas (Google Scholar
#   e Semantic Scholar), permitindo o mapeamento do estado da arte sobre IA na
#   Educação. Os dados coletados alimentam a triagem PRISMA documentada em
#   docs/protocol/prisma_protocol.md.
# =============================================================================

import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Iterator

try:
    from scholarly import scholarly, ProxyGenerator
    SCHOLARLY_AVAILABLE = True
except ImportError:
    SCHOLARLY_AVAILABLE = False

import requests

# ---------------------------------------------------------------------------
# Configuração do Logger
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path("data/raw")
DELAY_BETWEEN_REQUESTS = 5  # Segundos (evitar bloqueio de IP)

SEARCH_QUERIES = [
    '"artificial intelligence" AND "education" AND "learning outcomes"',
    '"machine learning" AND "pedagogy" AND "student performance"',
    '"generative AI" AND "higher education"',
    '"intelligent tutoring system" AND "equity"',
    '"AI ethics" AND "education"',
]

YEAR_LOW = 2020
YEAR_HIGH = 2026


# ---------------------------------------------------------------------------
# Google Scholar (via scholarly)
# ---------------------------------------------------------------------------

def search_google_scholar(query: str, max_results: int = 50) -> list[dict]:
    """
    Busca artigos no Google Scholar via biblioteca scholarly.

    Args:
        query (str): String de busca.
        max_results (int): Número máximo de resultados.

    Returns:
        list[dict]: Lista de artigos encontrados.
    """
    if not SCHOLARLY_AVAILABLE:
        logger.warning("Biblioteca 'scholarly' não instalada. Pulando Google Scholar.")
        return []

    results = []
    logger.info(f"Google Scholar: buscando → {query[:60]}...")

    try:
        search_gen = scholarly.search_pubs(query)
        for i, pub in enumerate(search_gen):
            if i >= max_results:
                break

            year = pub.get("bib", {}).get("pub_year")
            if year and not (YEAR_LOW <= int(year) <= YEAR_HIGH):
                continue

            results.append({
                "source": "google_scholar",
                "title": pub.get("bib", {}).get("title", ""),
                "abstract": pub.get("bib", {}).get("abstract", ""),
                "authors": pub.get("bib", {}).get("author", []),
                "year": year,
                "venue": pub.get("bib", {}).get("venue", ""),
                "citation_count": pub.get("num_citations", 0),
                "url": pub.get("pub_url", ""),
                "collected_at": datetime.now().isoformat(),
            })
            time.sleep(DELAY_BETWEEN_REQUESTS)

    except Exception as e:
        logger.error(f"Erro ao buscar no Google Scholar: {e}")

    logger.info(f"Google Scholar: {len(results)} artigos coletados.")
    return results


# ---------------------------------------------------------------------------
# Semantic Scholar (API REST)
# ---------------------------------------------------------------------------

def search_semantic_scholar(
    query: str,
    max_results: int = 100,
    session: requests.Session | None = None,
) -> list[dict]:
    """
    Busca artigos na API do Semantic Scholar.

    Args:
        query (str): String de busca.
        max_results (int): Número máximo de resultados.
        session: Sessão HTTP reutilizável.

    Returns:
        list[dict]: Lista de artigos encontrados.
    """
    if session is None:
        session = requests.Session()
        session.headers["User-Agent"] = "ia-educacao-research/1.0"

    results = []
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    fields = "paperId,title,abstract,year,authors,venue,citationCount"

    offset = 0
    limit = min(100, max_results)

    while offset < max_results:
        params = {
            "query": query,
            "fields": fields,
            "limit": limit,
            "offset": offset,
            "year": f"{YEAR_LOW}-{YEAR_HIGH}",
        }
        try:
            response = session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            batch = data.get("data", [])

            if not batch:
                break

            for paper in batch:
                results.append({
                    "source": "semantic_scholar",
                    "paper_id": paper.get("paperId", ""),
                    "title": paper.get("title", ""),
                    "abstract": paper.get("abstract", ""),
                    "authors": [a.get("name", "") for a in paper.get("authors", [])],
                    "year": paper.get("year"),
                    "venue": paper.get("venue", ""),
                    "citation_count": paper.get("citationCount", 0),
                    "collected_at": datetime.now().isoformat(),
                })

            offset += limit
            time.sleep(3)

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição Semantic Scholar (offset={offset}): {e}")
            break

    logger.info(f"Semantic Scholar: {len(results)} artigos coletados para query.")
    return results


# ---------------------------------------------------------------------------
# Deduplicação
# ---------------------------------------------------------------------------

def deduplicate(papers: list[dict]) -> list[dict]:
    """Remove duplicatas por título normalizado."""
    seen = set()
    unique = []
    for paper in papers:
        key = paper.get("title", "").lower().strip()[:80]
        if key and key not in seen:
            seen.add(key)
            unique.append(paper)
    return unique


# ---------------------------------------------------------------------------
# Pipeline Principal
# ---------------------------------------------------------------------------

def run_scraper() -> None:
    """Orquestra a coleta em múltiplas bases e queries."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "ia-educacao-research/1.0"

    all_papers = []

    for query in SEARCH_QUERIES:
        logger.info(f"\n{'='*60}\nProcessando query: {query}\n{'='*60}")

        # Semantic Scholar
        ss_papers = search_semantic_scholar(query, max_results=100, session=session)
        all_papers.extend(ss_papers)

        # Google Scholar (opcional, mais lento)
        gs_papers = search_google_scholar(query, max_results=20)
        all_papers.extend(gs_papers)

        time.sleep(5)

    # Deduplicação global
    unique_papers = deduplicate(all_papers)
    logger.info(f"\nTotal bruto: {len(all_papers)} | Únicos: {len(unique_papers)}")

    # Persistência
    output_file = OUTPUT_DIR / "scraper_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(unique_papers, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ Resultados salvos em: {output_file}")


if __name__ == "__main__":
    run_scraper()
