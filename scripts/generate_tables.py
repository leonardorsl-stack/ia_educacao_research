"""
generate_tables.py
-------------------
Lê data/processed/meta_analysis_matrix.csv e gera dois arquivos:
  - results/tables/evidence_table.md   → tabela Markdown limpa
  - results/tables/evidence_table.tex  → tabela LaTeX (booktabs + tabularx)

Colunas exportadas:
  ID | Metodologia | Tecnologia de IA | Efeito Empírico (resumo)
"""

import csv
import textwrap
from datetime import datetime
from pathlib import Path

# ── Caminhos ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "processed" / "meta_analysis_matrix.csv"
OUT_DIR  = BASE_DIR / "results" / "tables"
MD_PATH  = OUT_DIR / "evidence_table.md"
TEX_PATH = OUT_DIR / "evidence_table.tex"


# ── Helpers ───────────────────────────────────────────────────────────────────
def load_matrix(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def truncate(text: str, max_len: int = 90) -> str:
    """Trunca texto longo adicionando '…' ao final."""
    text = text.strip()
    return text if len(text) <= max_len else text[:max_len].rstrip() + "…"


def escape_latex(text: str) -> str:
    """Escapa os caracteres especiais do LaTeX.
    IMPORTANTE: a barra invertida deve ser escapada PRIMEIRO para não
    converter as barras geradas pelos demais escapes."""
    # 1. Barra invertida deve vir antes de tudo
    text = text.replace("\\", r"\textbackslash{}")
    # 2. Demais caracteres especiais
    replacements = [
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
        ("…", r"\ldots{}"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def build_rows(records: list[dict]) -> list[tuple[str, str, str, str]]:
    """Retorna lista de (id, metodologia, ai_type, efeito) para cada artigo."""
    rows = []
    for r in records:
        paper_id  = r["paper_id"].strip()
        method    = r["methodology_type"].strip() or "Not Specified"
        ai_type   = r["ai_type"].strip() or "Not Specified"
        direction = r["main_finding_direction"].strip()
        effect    = r["effect_description"].strip() or r["main_finding_direction"].strip()

        # Monta descrição resumida do efeito
        if effect.lower() in ("see abstract", ""):
            effect = direction
        else:
            effect = truncate(f"{direction} – {effect}", 95)

        rows.append((paper_id, method, ai_type, effect))
    return rows


# ── Geração Markdown ───────────────────────────────────────────────────────────
def generate_markdown(rows: list[tuple], now: str) -> str:
    header  = "| ID | Metodologia | Tecnologia de IA | Efeito Empírico |\n"
    divider = "| --- | --- | --- | --- |\n"
    body = "".join(
        f"| {pid} | {method} | {ai} | {effect} |\n"
        for pid, method, ai, effect in rows
    )
    preamble = (
        f"<!-- Gerado automaticamente em {now} por scripts/generate_tables.py -->\n\n"
        "# Tabela de Evidências — Meta-Análise\n\n"
    )
    return preamble + header + divider + body


# ── Geração LaTeX ──────────────────────────────────────────────────────────────
def generate_latex(rows: list[tuple], now: str) -> str:
    indent = "    "  # 4 espaços para linhas do corpo (alinhado com \toprule)
    body_lines = []
    for pid, method, ai, effect in rows:
        cols = " & ".join([
            escape_latex(pid),
            escape_latex(method),
            escape_latex(ai),
            escape_latex(effect),
        ])
        body_lines.append(f"{indent}{cols} \\\\")
    body = "\n".join(body_lines)

    lines = [
        f"% Gerado automaticamente em {now} por scripts/generate_tables.py",
        r"% Requer: \usepackage{booktabs}, \usepackage{tabularx}",
        r"\begin{table}[htbp]",
        r"  \centering",
        r"  \caption{Tabela de Evidências --- Meta-Análise de IA na Educação}",
        r"  \label{tab:evidence}",
        r"  \small",
        r"  \begin{tabularx}{\textwidth}{l l l X}",
        r"    \toprule",
        r"    \textbf{ID} & \textbf{Metodologia} & \textbf{IA Utilizada} & \textbf{Efeito Empírico} \\",
        r"    \midrule",
        body,
        r"    \bottomrule",
        r"  \end{tabularx}",
        r"\end{table}",
    ]
    return "\n".join(lines) + "\n"


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {CSV_PATH}")

    records = load_matrix(CSV_PATH)
    print(f"[✓] {len(records)} artigos carregados de {CSV_PATH.name}")

    rows = build_rows(records)
    now  = datetime.now().strftime("%Y-%m-%d %H:%M")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Markdown
    md_content = generate_markdown(rows, now)
    MD_PATH.write_text(md_content, encoding="utf-8")
    print(f"[✓] Markdown salvo em {MD_PATH.relative_to(BASE_DIR)}")

    # LaTeX
    tex_content = generate_latex(rows, now)
    TEX_PATH.write_text(tex_content, encoding="utf-8")
    print(f"[✓] LaTeX salvo em   {TEX_PATH.relative_to(BASE_DIR)}")

    # Preview: primeiros 3 itens
    print("\n── Preview: primeiros 3 itens da tabela Markdown ──────────────────")
    header  = "| ID | Metodologia | Tecnologia de IA | Efeito Empírico |"
    divider = "| --- | --- | --- | --- |"
    print(header)
    print(divider)
    for pid, method, ai, effect in rows[:3]:
        print(f"| {pid} | {method} | {ai} | {effect} |")


if __name__ == "__main__":
    main()
