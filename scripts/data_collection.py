#!/usr/bin/env python3
# =============================================================================
# Script: data_collection.py
# Autor: Equipe de Pesquisa — IA na Educação
# Data: 2026-04-20
# Finalidade Sociológica: Coleta sistemática de evidências empíricas sobre o
#   impacto da Inteligência Artificial na educação, via API do Semantic Scholar.
#   Segue protocolo PRISMA 2020. Os dados brutos coletados são insumo primário
#   da revisão sistemática de literatura (RSL).
# =============================================================================

import json
import time
import logging
from pathlib import Path
from datetime import datetime

import requests
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Configuração do Logger
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("data_collection.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes e Parâmetros
# ---------------------------------------------------------------------------
BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# String de busca conforme protocolo PRISMA (docs/protocol/prisma_protocol.md)
QUERY = (
    '("Artificial Intelligence" OR "Generative AI") '
    'AND ("Education") '
    'AND ("Social Impact")'
)

# Filtros temporais (conforme protocolo)
YEAR_START = 2020
YEAR_END = 2026

# Campos a recuperar para cada artigo
FIELDS = [
    "paperId",
    "title",
    "abstract",
    "year",
    "authors",
    "venue",
    "citationCount",
    "externalIds",
    "publicationTypes",
    "openAccessPdf",
]

# Chave de API (opcional — obtida em https://www.semanticscholar.org/product/api)
# Defina a variável de ambiente SS_API_KEY para usar chave própria
import os as _os
SS_API_KEY = _os.getenv("SS_API_KEY", "")

# Controle de paginação
LIMIT_PER_REQUEST = 100   # Máximo permitido pela API
MAX_RESULTS = 1000         # Limite total de resultados por execução
REQUEST_DELAY_SECONDS = 5  # Respeito ao rate limit da API (sem chave: ~1 req/s)
MAX_RETRIES = 4            # Tentativas com backoff exponencial

# Caminhos de saída
OUTPUT_DIR = Path("data/raw")
OUTPUT_FILE = OUTPUT_DIR / "search_results.json"
METADATA_FILE = Path("data/metadata") / "search_metadata.json"


# ---------------------------------------------------------------------------
# Funções Auxiliares
# ---------------------------------------------------------------------------

def build_request_params(offset: int) -> dict:
    """Monta os parâmetros da requisição HTTP para a API Semantic Scholar."""
    return {
        "query": QUERY,
        "fields": ",".join(FIELDS),
        "limit": LIMIT_PER_REQUEST,
        "offset": offset,
        "year": f"{YEAR_START}-{YEAR_END}",
    }


def fetch_page(offset: int, session: requests.Session) -> dict | None:
    """
    Executa uma requisição à API com retry e backoff exponencial.

    Args:
        offset (int): Posição de início na lista de resultados.
        session (requests.Session): Sessão HTTP reutilizável.

    Returns:
        dict | None: Dados JSON ou None em caso de falha definitiva.
    """
    params = build_request_params(offset)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            logger.info(
                f"Página coletada: offset={offset}, status={response.status_code}"
                f" (tentativa {attempt})"
            )
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                wait = 30 * (2 ** (attempt - 1))  # 30s, 60s, 120s, 240s
                logger.warning(
                    f"Rate limit 429 (tentativa {attempt}/{MAX_RETRIES}). "
                    f"Aguardando {wait}s..."
                )
                time.sleep(wait)
            else:
                logger.error(f"Erro HTTP {response.status_code} (offset={offset}): {e}")
                return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Erro de conexão (offset={offset}, tentativa {attempt}): {e}")
            time.sleep(10 * attempt)
        except requests.exceptions.Timeout:
            logger.error(f"Timeout (offset={offset}, tentativa {attempt})")
            time.sleep(10 * attempt)

    logger.error(f"Falha definitiva após {MAX_RETRIES} tentativas (offset={offset}).")
    return None


def filter_by_relevance(papers: list[dict]) -> list[dict]:
    """
    Filtra artigos sem abstract e sem tipo de publicação acadêmica.
    Critério de exclusão conforme protocolo PRISMA (Seção 4.2).

    Args:
        papers (list[dict]): Lista bruta de artigos.

    Returns:
        list[dict]: Lista filtrada.
    """
    filtered = []
    excluded_no_abstract = 0
    excluded_no_title = 0

    for paper in papers:
        if not paper.get("title"):
            excluded_no_title += 1
            continue
        if not paper.get("abstract"):
            excluded_no_abstract += 1
            continue
        filtered.append(paper)

    logger.info(
        f"Filtragem: {len(papers)} brutos → {len(filtered)} válidos | "
        f"sem título: {excluded_no_title} | sem abstract: {excluded_no_abstract}"
    )
    return filtered


def save_results(papers: list[dict], metadata: dict) -> None:
    """
    Persiste os resultados coletados em disco (JSON).

    Args:
        papers (list[dict]): Lista de artigos coletados e filtrados.
        metadata (dict): Metadados da sessão de coleta.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    Path("data/metadata").mkdir(parents=True, exist_ok=True)

    # Salvar artigos
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ Resultados salvos em: {OUTPUT_FILE} ({len(papers)} artigos)")

    # Salvar metadados da coleta
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ Metadados salvos em: {METADATA_FILE}")


# ---------------------------------------------------------------------------
# Pipeline Principal
# ---------------------------------------------------------------------------

def run_collection() -> None:
    """
    Orquestra a coleta completa: paginação, filtragem e persistência.
    Segue a ordem de execução definida no docs/protocol/prisma_protocol.md.
    """
    logger.info("=" * 60)
    logger.info("INÍCIO DA COLETA — API Semantic Scholar")
    logger.info(f"Query: {QUERY}")
    logger.info(f"Período: {YEAR_START}–{YEAR_END}")
    logger.info("=" * 60)

    all_papers: list[dict] = []
    total_raw = 0
    offset = 0

    session = requests.Session()
    headers = {"User-Agent": "ia-educacao-research/1.0 (revisao-sistematica@pesquisa.br)"}
    if SS_API_KEY:
        headers["x-api-key"] = SS_API_KEY
        logger.info("✅ API Key detectada — limite elevado ativo.")
    else:
        logger.warning("⚠️  Sem API Key — rate limit público (~1 req/s). Defina SS_API_KEY.")
    session.headers.update(headers)

    with tqdm(total=MAX_RESULTS, desc="Coletando artigos", unit="artigo") as pbar:
        while offset < MAX_RESULTS:
            data = fetch_page(offset, session)

            if data is None:
                logger.warning(f"Requisição falhou em offset={offset}. Encerrando.")
                break

            papers_batch = data.get("data", [])
            if not papers_batch:
                logger.info("Nenhum resultado adicional encontrado. Coleta concluída.")
                break

            total_raw += len(papers_batch)
            valid_batch = filter_by_relevance(papers_batch)
            all_papers.extend(valid_batch)

            pbar.update(len(papers_batch))
            offset += LIMIT_PER_REQUEST

            # Respeitar rate limit da API
            time.sleep(REQUEST_DELAY_SECONDS)

    # Metadados da sessão (auditoria científica)
    metadata = {
        "collection_date": datetime.now().isoformat(),
        "query": QUERY,
        "year_range": f"{YEAR_START}-{YEAR_END}",
        "total_raw_results": total_raw,
        "total_filtered_results": len(all_papers),
        "exclusion_rate_pct": round((1 - len(all_papers) / max(total_raw, 1)) * 100, 2),
        "api_source": "Semantic Scholar Graph API v1",
        "protocol_reference": "docs/protocol/prisma_protocol.md",
    }

    save_results(all_papers, metadata)

    logger.info("=" * 60)
    logger.info(f"COLETA FINALIZADA")
    logger.info(f"  Total bruto:     {total_raw}")
    logger.info(f"  Total filtrado:  {len(all_papers)}")
    logger.info(f"  Taxa de exclusão: {metadata['exclusion_rate_pct']}%")
    logger.info("=" * 60)


# ---------------------------------------------------------------------------
# Ponto de Entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_collection()
