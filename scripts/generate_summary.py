"""
generate_summary.py
--------------------
Lê data/processed/meta_analysis_matrix.csv e data/processed/scraped_papers.csv,
e salva um relatório de análise em docs/analysis_summary.md com as seguintes
tabelas de frequência:
  1. Direção dos achados (main_finding_direction)
  2. Nível educacional (education_level)
  3. Cruzamento Metodologia × Iniquidade (methodology_type × inequity)
"""

import sys
import os
from collections import Counter
from datetime import datetime
from pathlib import Path
import pandas as pd


# ── Caminhos e Imports ────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.markdown_utils import freq_table, crosstab

META_CSV_PATH = BASE_DIR / "data" / "processed" / "meta_analysis_matrix.csv"
SCRAPED_CSV_PATH = BASE_DIR / "data" / "processed" / "scraped_papers.csv"
OUT_PATH = BASE_DIR / "docs" / "analysis_summary.md"


# ── Geração do relatório ───────────────────────────────────────────────────────
def generate_report(records: list[dict]) -> str:
    n_total = len(records)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 1. Direção dos achados
    direction_counter = Counter(r.get("main_finding_direction", "Not Specified") for r in records)

    # 2. Nível educacional – simplificando rótulos
    def simplify_edu(val: str) -> str:
        v = str(val).strip() if val else ""
        if "Higher" in v or "Universit" in v or "University" in v:
            return "Higher Ed"
        if "K-12" in v or "Basic" in v or "Elementary" in v:
            return "K-12"
        return v if v else "Not Specified"

    edu_counter = Counter(simplify_edu(r.get("education_level")) for r in records)

    # 3. Cruzamento Metodologia × Iniquidade
    def simplify_method(val: str) -> str:
        v = str(val).strip() if val else ""
        return v if v else "Not Specified"

    def simplify_inequity(val: str) -> str:
        v = str(val).strip().lower() if val else ""
        if v in ("true", "1", "yes"):
            return "Sim"
        if v in ("false", "0", "no"):
            return "Não"
        return "N/A"

    crosstab_records = [
        {
            "Metodologia": simplify_method(r.get("methodology_type")),
            "Iniquidade": simplify_inequity(r.get("inequity")),
        }
        for r in records
    ]

    lines = []
    lines.append("# Relatório de Análise — Meta-Analysis Matrix + Scraped Data")
    lines.append(f"\n> Gerado automaticamente em {now}  ")
    lines.append(f"> Arquivos fonte: `data/processed/meta_analysis_matrix.csv`, `data/processed/scraped_papers.csv`  ")
    lines.append(f"> Total de artigos: **{n_total}**\n")
    lines.append("---\n")

    lines.append("## 1. Direção dos Achados (`main_finding_direction`)\n")
    lines.append(freq_table(direction_counter, "Direção"))
    lines.append("")

    lines.append("## 2. Nível Educacional (`education_level`)\n")
    lines.append(freq_table(edu_counter, "Nível Educacional"))
    lines.append("")

    lines.append("## 3. Metodologia × Iniquidade (`methodology_type × inequity`)\n")
    lines.append(crosstab(crosstab_records, "Metodologia", "Iniquidade"))
    lines.append("")

    lines.append("---")
    lines.append("\n*Relatório gerado por `scripts/generate_summary.py`*")

    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    if not META_CSV_PATH.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {META_CSV_PATH}")
    if not SCRAPED_CSV_PATH.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {SCRAPED_CSV_PATH}")

    df_meta = pd.read_csv(META_CSV_PATH)
    print(f"[✓] {len(df_meta)} artigos carregados de {META_CSV_PATH.name}")

    df_scraped = pd.read_csv(SCRAPED_CSV_PATH)
    print(f"[✓] {len(df_scraped)} artigos carregados de {SCRAPED_CSV_PATH.name}")

    combined_df = pd.concat([df_meta, df_scraped], ignore_index=True)
    records = combined_df.where(pd.notna(combined_df), None).to_dict('records')

    report = generate_report(records)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(report, encoding="utf-8")
    print(f"[✓] Relatório salvo em {OUT_PATH.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
