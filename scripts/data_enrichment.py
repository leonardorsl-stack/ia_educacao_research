#!/usr/bin/env python3
# =============================================================================
# Script: data_enrichment.py
# Autor: Equipe de Pesquisa — IA na Educação
# Data: 2026-04-20
# Finalidade: Enriquecer empirical_papers.csv com dimensões metodológicas e de
#   impacto para a meta-análise sociológica da revisão sistemática PRISMA 2020.
#   Input:  data/processed/empirical_papers.csv
#   Output: data/processed/meta_analysis_matrix.csv
# =============================================================================

import re
import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

INPUT_CSV  = "data/processed/empirical_papers.csv"
OUTPUT_CSV = "data/processed/meta_analysis_matrix.csv"


# ---------------------------------------------------------------------------
# Dimensão A — Metodológica
# ---------------------------------------------------------------------------

def extrair_metadados_texto(text: str) -> pd.Series:
    """
    Extrai variáveis para a meta-análise sociológica via regex + NLP léxico.

    Retorna pd.Series com:
      sample_size, methodology_type, education_level, geographic_focus
    """
    t = text.lower() if text else ""

    # A1 — Tamanho da amostra
    sample = re.search(
        r"(?:n\s*=\s*|sample\s+of\s+|sample\s+size\s+of\s+|"
        r"(?:involving|with|among|from)\s+)(\d{2,5})\s*(?:students?|teachers?|participants?|universities|schools)?",
        text, re.I
    )
    # Tenta também padrões como "45 empirical studies" ou "12 universities"
    if not sample:
        sample = re.search(r"\b(\d{2,4})\s+(?:empirical\s+)?(?:studies|students|teachers|universities|schools|participants)\b", text, re.I)
    n_size = sample.group(1) if sample else "N/A"

    # A2 — Tipo de metodologia
    if re.search(r"mixed[- ]method|mixed method|qualitative.{0,30}quantitative|quantitative.{0,30}qualitative", t):
        method = "Mixed Methods"
    elif re.search(r"qualitative|case study|interview|thematic|ethnograph|grounded theory|narrative", t):
        method = "Qualitative"
    elif re.search(r"quantitative|experiment|trial|rct|regression|survey|questionnaire|meta.analysis|effect size|statistical", t):
        method = "Quantitative"
    else:
        method = "Not Specified"

    # A3 — Nível educacional
    if re.search(r"university|higher education|college|undergraduate|postgraduate|graduate\b|phd", t):
        edu_level = "Higher Education"
    elif re.search(r"k-12|primary|secondary|high school|elementary|middle school|basic education|escola básica|ensino médio|ensino fundamental", t):
        edu_level = "K-12 (Basic)"
    elif re.search(r"technical|vocational|professional\s+training|tvet", t):
        edu_level = "Technical/Vocational"
    else:
        edu_level = "Not Specified"

    # A4 — Foco geográfico
    geo_map = {
        "Brazil / South America":   r"brazil|brazilian|brasil|south america|latin america",
        "Sub-Saharan Africa":       r"sub.saharan|africa|african|nigeria|kenya|ghana|ethiopia",
        "Global South (general)":   r"global south|developing countr|low.income countr|emerging econom",
        "USA / North America":      r"\busa\b|united states|american|north america|u\.s\.",
        "Europe":                   r"europe|european|uk\b|england|germany|france|spain|italy",
        "Asia":                     r"\bchina\b|chinese|india|indian|japan|japanese|asian|southeast asia",
        "Global / Multi-country":   r"global\b|worldwide|international|cross.national|multi.countr",
    }
    geo = "Not Specified"
    for region, pattern in geo_map.items():
        if re.search(pattern, t):
            geo = region
            break

    return pd.Series([n_size, method, edu_level, geo])


# ---------------------------------------------------------------------------
# Dimensão B — Impacto e Evidência
# ---------------------------------------------------------------------------

def extrair_impacto(row: pd.Series) -> pd.Series:
    """
    Extrai dimensões de impacto e evidência a partir do título + abstract.

    Retorna pd.Series com:
      ai_type, main_finding_direction, effect_description, inequity_evidence
    """
    text  = str(row.get("abstract", "")) + " " + str(row.get("title", ""))
    t     = text.lower()

    # B1 — Tipo de IA
    ai_map = {
        "ChatGPT / LLM (Generative AI)": r"chatgpt|gpt|llm|large language model|generative ai|gemini|claude|bard",
        "ITS (Intelligent Tutoring)":    r"intelligent tutoring|its\b|tutor system|adaptive tutoring|cognitive tutor",
        "Recommendation System":         r"recommendation system|content recommendation|personali[sz]ed learning|adaptive learning system",
        "Automated Assessment (AES)":    r"automated essay|automated assessment|automated scoring|essay scoring|auto.grade",
        "Predictive Analytics":          r"predict|early warning|learning analytics|data-driven|performance forecast",
        "AI (Generic / Multiple)":       r"artificial intelligence|machine learning|deep learning|algorithm|neural network",
    }
    ai_type = "Not Specified"
    for label, pattern in ai_map.items():
        if re.search(pattern, t):
            ai_type = label
            break

    # B2 — Direção do achado principal
    positive_kws = r"improv|increas|positive|benefit|effective|significan.{0,10}(gain|improve|higher|better)|" \
                   r"reduc.{0,15}(workload|burden|time)|higher performance|better outcome"
    negative_kws = r"reduc.{0,15}(autonomy|critical thinking|performance)|negativ|harm|risk|" \
                   r"bias|discriminat|inequit|disparit" # Removido 'limit', 'concern', 'challeng', 'barrier' que são normais em qualquer artigo

    positive = re.search(positive_kws, t)
    negative = re.search(negative_kws, t)

    if positive and negative:
        direction = "Mixed / Neutral"
    elif positive:
        direction = "Positive"
    elif negative:
        direction = "Negative"
    else:
        direction = "Mixed / Neutral"

    # B3 — Descrição sucinta do efeito
    quant = re.search(
        r"(\d+\s*%\s*\w[\w\s]{0,40}|effect size[^\.,]{0,40}|d\s*=\s*[\d\.]+[^\.,]{0,30}|"
        r"\d+\s*(?:point|percent|fold|times)[^\.,]{0,40})",
        text, re.I
    )
    if quant:
        effect_desc = quant.group(0).strip()[:120]
    else:
        sent = re.search(r"[^.]*(?:result|finding|show|reveal|indicate|suggest)[^.]{0,150}\.", text, re.I)
        effect_desc = sent.group(0).strip()[:120] if sent else "See abstract"

    # B4 — Evidência de desigualdade
    inequity_flag = bool(row.get("inequity", False))
    if not inequity_flag:
        inequity_ev = "Not reported"
    else:
        ineq_sent = re.search(
            r"[^.]*(?:inequit|inequalit|disparit|gap|access barrier|rural|low.income|"
            r"marginali|global south|developing|underserved|exclusion)[^.]{0,180}\.",
            text, re.I
        )
        inequity_ev = ineq_sent.group(0).strip()[:160] if ineq_sent else "Flagged in abstract (see full text)"

    # B5 — Qualidade Metodológica Simplificada (Novo)
    # Pontuação de 0 a 5 com base em evidências no abstract
    quality_score = 0
    if re.search(r"n\s*=\s*\d+|sample\s+of", t): quality_score += 1 # Amostra definida
    if re.search(r"control group|randomized|experiment|rct", t): quality_score += 1 # Design robusto
    if re.search(r"statistically significant|p\s*<\s*0", t): quality_score += 1 # Rigor estatístico
    if re.search(r"methodology|mixed methods|qualitative|quantitative", t): quality_score += 1 # Metodologia explícita
    if len(t) > 500: quality_score += 1 # Detalhamento do abstract

    return pd.Series([ai_type, direction, effect_desc, inequity_ev, quality_score])


# ---------------------------------------------------------------------------
# Pipeline Principal
# ---------------------------------------------------------------------------

def run_enrichment() -> pd.DataFrame:
    logger.info("=" * 60)
    logger.info("INÍCIO — Enriquecimento de Metadados (Meta-análise)")
    logger.info("=" * 60)

    df = pd.read_csv(INPUT_CSV)
    logger.info(f"Artigos carregados: {len(df)}")

    # --- Dimensão A ---
    logger.info("Extraindo dimensões metodológicas (A)...")
    df[["sample_size", "methodology_type", "education_level", "geographic_focus"]] = \
        df["abstract"].fillna("").apply(extrair_metadados_texto)

    # --- Dimensão B ---
    logger.info("Extraindo dimensões de impacto (B)...")
    df[["ai_type", "main_finding_direction", "effect_description", "inequity_evidence", "quality_score"]] = \
        df.apply(extrair_impacto, axis=1)

    # --- Reordenar colunas para leitura científica ---
    col_order = [
        "paper_id", "title", "year", "venue", "citation_count",
        # Dimensão A
        "methodology_type", "education_level", "geographic_focus", "sample_size",
        # Dimensão B
        "ai_type", "main_finding_direction", "effect_description", "quality_score",
        "impact", "inequity", "ethics", "inequity_evidence",
        # Cluster
        "cluster", "cluster_label",
        # Abstract (por último para legibilidade)
        "abstract",
    ]
    df = df[[c for c in col_order if c in df.columns]]

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    logger.info(f"✅ Matriz salva: {OUTPUT_CSV} ({len(df)} registros · {len(df.columns)} colunas)")
    logger.info("=" * 60)

    return df


if __name__ == "__main__":
    run_enrichment()
    print(f"\n✅ Matriz de Meta-análise gerada com sucesso em '{OUTPUT_CSV}'")
