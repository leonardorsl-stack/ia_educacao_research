"""
generate_summary.py
--------------------
Lê data/processed/meta_analysis_matrix.csv e salva um relatório de análise
em docs/analysis_summary.md com as seguintes tabelas de frequência:
  1. Direção dos achados (main_finding_direction)
  2. Nível educacional (education_level)
  3. Cruzamento Metodologia × Iniquidade (methodology_type × inequity)
"""

import sys
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

# ── Caminhos e Imports ────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.utils import load_csv
from src.markdown_utils import freq_table, crosstab

CSV_PATH = BASE_DIR / "data" / "processed" / "meta_analysis_matrix.csv"
OUT_PATH = BASE_DIR / "docs" / "analysis_summary.md"


# ── Geração do relatório ───────────────────────────────────────────────────────
def generate_report(records: list[dict]) -> str:
    n_total = len(records)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 1. Direção dos achados
    direction_counter = Counter(r["main_finding_direction"] for r in records)

    # 2. Nível educacional – simplificando rótulos
    def simplify_edu(val: str) -> str:
        v = val.strip()
        if "Higher" in v or "Universit" in v or "University" in v:
            return "Higher Ed"
        if "K-12" in v or "Basic" in v or "Elementary" in v:
            return "K-12"
        return v if v else "Not Specified"

    edu_counter = Counter(simplify_edu(r["education_level"]) for r in records)

    # 3. Cruzamento Metodologia × Iniquidade
    def simplify_method(val: str) -> str:
        v = val.strip()
        return v if v else "Not Specified"

    def simplify_inequity(val: str) -> str:
        v = val.strip().lower()
        if v in ("true", "1", "yes"):
            return "Sim"
        if v in ("false", "0", "no"):
            return "Não"
        return "N/A"

    crosstab_records = [
        {
            "Metodologia": simplify_method(r["methodology_type"]),
            "Iniquidade": simplify_inequity(r["inequity"]),
        }
        for r in records
    ]

    lines = []
    lines.append("# Relatório de Análise — Meta-Analysis Matrix")
    lines.append(f"\n> Gerado automaticamente em {now}  ")
    lines.append(f"> Arquivo fonte: `data/processed/meta_analysis_matrix.csv`  ")
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
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {CSV_PATH}")

    records = load_csv(CSV_PATH)
    print(f"[✓] {len(records)} artigos carregados de {CSV_PATH.name}")

    report = generate_report(records)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(report, encoding="utf-8")
    print(f"[✓] Relatório salvo em {OUT_PATH.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
