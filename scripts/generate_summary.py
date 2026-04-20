"""
generate_summary.py
--------------------
Lê data/processed/meta_analysis_matrix.csv e salva um relatório de análise
em docs/analysis_summary.md com as seguintes tabelas de frequência:
  1. Direção dos achados (main_finding_direction)
  2. Nível educacional (education_level)
  3. Cruzamento Metodologia × Iniquidade (methodology_type × inequity)
"""

import csv
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

# ── Caminhos ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "processed" / "meta_analysis_matrix.csv"
OUT_PATH = BASE_DIR / "docs" / "analysis_summary.md"

# ── Leitura do CSV ─────────────────────────────────────────────────────────────
def load_matrix(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


# ── Helpers para Markdown ──────────────────────────────────────────────────────
def md_table(headers: list[str], rows: list[list]) -> str:
    """Gera uma tabela Markdown a partir de cabeçalhos e linhas."""
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    header_row = "| " + " | ".join(str(h) for h in headers) + " |"
    body = "\n".join(
        "| " + " | ".join(str(c) for c in row) + " |" for row in rows
    )
    return "\n".join([header_row, sep, body])


def freq_table(counter: Counter, col_label: str) -> str:
    """Converte um Counter em tabela Markdown com contagem e percentual."""
    total = sum(counter.values())
    rows = []
    for value, count in sorted(counter.items(), key=lambda x: -x[1]):
        pct = f"{count / total * 100:.1f}%"
        rows.append([value, count, pct])
    rows.append(["**Total**", total, "100%"])
    return md_table([col_label, "Contagem", "%"], rows)


def crosstab(records: list[dict], row_key: str, col_key: str) -> str:
    """Tabela cruzada Markdown entre duas variáveis categóricas."""
    row_vals = sorted(set(r[row_key] for r in records))
    col_vals = sorted(set(r[col_key] for r in records))

    # Contagem
    cell: dict[tuple, int] = Counter()
    for r in records:
        cell[(r[row_key], r[col_key])] += 1

    headers = [row_key + " \\ " + col_key] + col_vals + ["Total"]
    rows = []
    col_totals = Counter()
    for rv in row_vals:
        row_data = [rv]
        row_sum = 0
        for cv in col_vals:
            n = cell.get((rv, cv), 0)
            row_data.append(n)
            row_sum += n
            col_totals[cv] += n
        row_data.append(row_sum)
        rows.append(row_data)

    # Linha de totais
    total_row = ["**Total**"] + [col_totals[cv] for cv in col_vals]
    total_row.append(sum(col_totals.values()))
    rows.append(total_row)

    return md_table(headers, rows)


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

    records = load_matrix(CSV_PATH)
    print(f"[✓] {len(records)} artigos carregados de {CSV_PATH.name}")

    report = generate_report(records)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(report, encoding="utf-8")
    print(f"[✓] Relatório salvo em {OUT_PATH.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
