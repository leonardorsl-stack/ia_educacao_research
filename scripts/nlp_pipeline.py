#!/usr/bin/env python3
# =============================================================================
# Script: nlp_pipeline.py
# Autor: Equipe de Pesquisa — IA na Educação
# Data: 2026-04-20
# Finalidade Sociológica: Pipeline de Processamento de Linguagem Natural (NLP)
#   aplicado aos títulos e resumos dos artigos triados. Realiza classificação
#   temática, extração de entidades e detecção de padrões discursivos relevantes
#   para a análise sociológica do campo da IA na Educação.
# =============================================================================

import json
import logging
import re
from pathlib import Path
from typing import Optional

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize

try:
    import spacy
    NLP_MODEL = None  # Carregado sob demanda
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

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
INPUT_FILE = Path("data/processed/papers_triados.csv")
OUTPUT_FILE = Path("data/processed/papers_nlp.csv")

N_CLUSTERS = 6
MAX_TFIDF_FEATURES = 1000
SPACY_MODEL = "en_core_web_sm"

# Taxonomia sociológica de termos de interesse
SOCIOLOGICAL_TAXONOMY = {
    "impacto_pedagogico": [
        "learning outcome", "student performance", "achievement", "engagement",
        "motivation", "retention", "dropout", "graduation", "academic success",
    ],
    "equidade_acesso": [
        "equity", "inequality", "bias", "fairness", "underrepresented",
        "marginalized", "digital divide", "access", "inclusion", "diversity",
    ],
    "dimensao_etica": [
        "ethics", "ethical", "privacy", "surveillance", "accountability",
        "transparency", "explainability", "autonomy", "harm", "risk",
    ],
    "tecnologia_ia": [
        "artificial intelligence", "machine learning", "deep learning",
        "neural network", "natural language processing", "chatgpt", "llm",
        "generative ai", "recommendation system", "intelligent tutoring",
    ],
    "metodologia": [
        "randomized controlled trial", "quasi-experiment", "survey",
        "meta-analysis", "systematic review", "qualitative", "mixed methods",
        "longitudinal", "case study",
    ],
}


# ---------------------------------------------------------------------------
# Funções de Pré-Processamento
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Normaliza o texto para análise NLP.

    Args:
        text (str): Texto bruto.

    Returns:
        str: Texto limpo e normalizado.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r"https?://\S+", " ", text)         # Remove URLs
    text = re.sub(r"\s+", " ", text)                   # Normaliza espaços
    text = re.sub(r"[^\w\s\-]", " ", text)            # Remove pontuação especial
    return text.strip()


def load_spacy_model() -> Optional[object]:
    """Carrega o modelo spaCy de forma lazy."""
    global NLP_MODEL
    if not SPACY_AVAILABLE:
        logger.warning("spaCy não instalado. Usando regex como fallback.")
        return None
    if NLP_MODEL is None:
        try:
            NLP_MODEL = spacy.load(SPACY_MODEL)
            logger.info(f"Modelo spaCy carregado: {SPACY_MODEL}")
        except OSError:
            logger.warning(
                f"Modelo '{SPACY_MODEL}' não encontrado. "
                f"Execute: python -m spacy download {SPACY_MODEL}"
            )
            NLP_MODEL = None
    return NLP_MODEL


# ---------------------------------------------------------------------------
# Análise Temática
# ---------------------------------------------------------------------------

def tag_sociological_categories(text: str) -> dict[str, bool]:
    """
    Aplica a taxonomia sociológica ao texto.

    Args:
        text (str): Texto limpo para análise.

    Returns:
        dict[str, bool]: Dicionário com flags por categoria.
    """
    tags = {}
    for category, keywords in SOCIOLOGICAL_TAXONOMY.items():
        tags[f"flag_{category}"] = any(kw in text for kw in keywords)
    return tags


def extract_entities_spacy(text: str, nlp_model) -> dict[str, list[str]]:
    """
    Extrai entidades nomeadas com spaCy.

    Args:
        text (str): Texto para análise.
        nlp_model: Modelo spaCy carregado.

    Returns:
        dict[str, list[str]]: Entidades por tipo (ORG, GPE, PERSON, etc.).
    """
    if not nlp_model or not text:
        return {}
    doc = nlp_model(text[:1000])  # Limitar tokens para performance
    entities = {}
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        if ent.text not in entities[ent.label_]:
            entities[ent.label_].append(ent.text)
    return entities


# ---------------------------------------------------------------------------
# Clustering Semântico
# ---------------------------------------------------------------------------

def run_tfidf_clustering(df: pd.DataFrame, text_col: str = "text_combined") -> pd.DataFrame:
    """
    Executa vetorização TF-IDF e clustering K-Means.

    Args:
        df (pd.DataFrame): DataFrame com coluna de texto.
        text_col (str): Nome da coluna de texto.

    Returns:
        pd.DataFrame: DataFrame com colunas de cluster adicionadas.
    """
    logger.info(f"Iniciando clustering TF-IDF com {N_CLUSTERS} clusters...")

    vectorizer = TfidfVectorizer(
        max_features=MAX_TFIDF_FEATURES,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True,
    )

    texts = df[text_col].fillna("").tolist()
    tfidf_matrix = vectorizer.fit_transform(texts)
    tfidf_normalized = normalize(tfidf_matrix)

    kmeans = KMeans(
        n_clusters=N_CLUSTERS,
        random_state=42,
        n_init=15,
        max_iter=300,
    )
    df = df.copy()
    df["cluster_id"] = kmeans.fit_predict(tfidf_normalized)

    # Extrair termos representativos por cluster
    feature_names = vectorizer.get_feature_names_out()
    cluster_terms = {}
    for i in range(N_CLUSTERS):
        center = kmeans.cluster_centers_[i]
        top_indices = center.argsort()[-8:][::-1]
        cluster_terms[i] = [feature_names[j] for j in top_indices]
        logger.info(f"Cluster {i}: {', '.join(cluster_terms[i])}")

    df["cluster_terms"] = df["cluster_id"].map(
        lambda c: "; ".join(cluster_terms.get(c, []))
    )

    return df


# ---------------------------------------------------------------------------
# Pipeline Principal
# ---------------------------------------------------------------------------

def run_nlp_pipeline() -> None:
    """
    Orquestra o pipeline NLP completo:
    1. Leitura dos dados triados
    2. Limpeza e normalização
    3. Tagging sociológico
    4. Extração de entidades (se spaCy disponível)
    5. Clustering semântico
    6. Exportação dos dados enriquecidos
    """
    logger.info("=" * 60)
    logger.info("INÍCIO DO PIPELINE NLP")
    logger.info("=" * 60)

    # 1. Carregar dados
    if not INPUT_FILE.exists():
        logger.error(f"Arquivo não encontrado: {INPUT_FILE}")
        logger.error("Execute primeiro: python scripts/data_collection.py")
        return

    df = pd.read_csv(INPUT_FILE, encoding="utf-8")
    logger.info(f"Dados carregados: {len(df)} artigos")

    # 2. Limpeza
    df["title_clean"] = df["title"].apply(clean_text)
    df["abstract_clean"] = df["abstract"].apply(clean_text)
    df["text_combined"] = df["title_clean"] + " " + df["abstract_clean"]
    logger.info("Textos normalizados.")

    # 3. Tagging sociológico
    logger.info("Aplicando taxonomia sociológica...")
    tag_results = df["text_combined"].apply(tag_sociological_categories)
    tag_df = pd.DataFrame(tag_results.tolist())
    df = pd.concat([df, tag_df], axis=1)

    for col in tag_df.columns:
        count = df[col].sum()
        logger.info(f"  {col}: {count} artigos ({count/len(df)*100:.1f}%)")

    # 4. Extração de entidades spaCy (opcional)
    nlp_model = load_spacy_model()
    if nlp_model:
        logger.info("Extraindo entidades nomeadas com spaCy...")
        df["entities"] = df["abstract_clean"].apply(
            lambda t: json.dumps(extract_entities_spacy(t, nlp_model), ensure_ascii=False)
        )

    # 5. Clustering semântico
    if len(df) >= N_CLUSTERS:
        df = run_tfidf_clustering(df, text_col="text_combined")
    else:
        logger.warning(f"Poucos artigos ({len(df)}) para {N_CLUSTERS} clusters.")

    # 6. Exportar
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    cols_to_drop = ["title_clean", "abstract_clean", "text_combined"]
    df.drop(columns=[c for c in cols_to_drop if c in df.columns]).to_csv(
        OUTPUT_FILE, index=False, encoding="utf-8"
    )
    logger.info(f"✅ Dados NLP exportados: {OUTPUT_FILE}")
    logger.info("=" * 60)
    logger.info("PIPELINE NLP FINALIZADO")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_nlp_pipeline()
