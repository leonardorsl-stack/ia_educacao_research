"""
generate_figures.py
===================
Gera as três figuras estratégicas do artigo para publicação em periódico Q1:

  fig1_empirical_findings.png  — Gráfico de setores: distribuição dos achados
  fig2_prisma_flow.png         — Diagrama PRISMA 2020 + CSC metodológico
  fig3_dialectical_axes.png    — Master Research Landscape (eixos dialéticos)

Saída  : results/figures/
Uso    : python scripts/generate_figures.py
Padrão : 300 DPI, bbox_inches='tight', fundo branco/neutro
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter

# -- Paths and Constants ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
META_CSV_PATH = BASE_DIR / "data" / "processed" / "meta_analysis_matrix.csv"
SCRAPED_CSV_PATH = BASE_DIR / "data" / "processed" / "scraped_papers.csv"
OUT_DIR = BASE_DIR / "results" / "figures"
os.makedirs(OUT_DIR, exist_ok=True)

DPI          = 300
FONT_FAMILY  = "DejaVu Sans"
BG_PAGE      = "#FFFFFF"

# Paleta institucional (acessível, WCAG AA)
RED    = "#C0392B"
ORANGE = "#D35400"
GREEN  = "#1A7A4A"
BLUE   = "#1B4F8A"
PURPLE = "#6C3483"
GRAY   = "#5D6D7E"
DARK   = "#1C2833"
LIGHT  = "#F2F3F4"


# ══════════════════════════════════════════════════════════════════════════════
# FIGURA 1 — Gráfico de setores: Direção dos Achados
# ══════════════════════════════════════════════════════════════════════════════
def fig1_empirical_findings(records: list[dict]):
    """
    Gráfico de setores (donut) mostrando a distribuição da direção dos achados
    nos estudos analisados.
    """
    findings = combined_df["main_finding_direction"].fillna("Não Especificado").tolist()
    n_total = len(findings)

    if n_total == 0:
        print("[!] Nenhum dado para gerar a Figura 1. Pulando.")
        return

    counter = Counter(findings)
    
    order = ["Negativo", "Misto / Neutro", "Positivo", "Não Especificado"]
    colors_map = {
        "Negativo": RED,
        "Misto / Neutro": ORANGE,
        "Positivo": GREEN,
        "Não Especificado": GRAY
    }
    
    plot_data = [(label, counter[label]) for label in order if counter.get(label, 0) > 0]
    
    if not plot_data:
        print("[!] Nenhum dado válido para gerar a Figura 1. Pulando.")
        return

    labels, sizes = zip(*plot_data)
    colors = [colors_map[l] for l in labels]
    
    explode_map = {
        "Negativo": 0.05, "Misto / Neutro": 0.02, 
        "Positivo": 0.08, "Não Especificado": 0.01
    }
    explode = [explode_map.get(l, 0.01) for l in labels]

    fig, ax = plt.subplots(figsize=(8, 6.5), facecolor=BG_PAGE)
    ax.set_facecolor(BG_PAGE)

    def autopct_format(values):
        def my_format(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return f'{pct:.1f}%\\n(n={val})'
        return my_format

    wedges, texts, autotexts = ax.pie(
        sizes,
        explode=explode,
        labels=[l.replace(" / ", "/\\n") for l in labels],
        colors=colors,
        startangle=90,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2.5),
        autopct=autopct_format(sizes),
        pctdistance=0.75,
        textprops={'color':"w", 'fontsize':8, 'fontweight':'bold'}
    )
    
    # Texto central
    ax.text(0, 0, f"{n_total}\\nestudos", ha="center", va="center",
            fontsize=24, fontfamily=FONT_FAMILY, fontweight="bold",
            color=DARK)

    # Título
    ax.set_title(
        f"Direção dos Achados em {n_total} Estudos Analisados",
        fontsize=11.5, fontfamily=FONT_FAMILY, fontweight="bold",
        color=DARK, pad=20, loc="center",
    )

    fig.tight_layout()
    out = os.path.join(OUT_DIR, "fig1_empirical_findings.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=BG_PAGE)
    plt.close(fig)
    print(f"[✓] {out}")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURA 2 — Fluxo PRISMA 2020 adaptado para CSC
# ══════════════════════════════════════════════════════════════════════════════
def fig2_prisma_flow(n_total: int):
    fig, ax = plt.subplots(figsize=(12, 8.5), facecolor=BG_PAGE)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8.5)
    ax.axis("off")
    ax.set_facecolor(BG_PAGE)

    C = {"id": "#1B4F8A", "tri": "#6C3483", "elig": "#117A65", "inc": "#922B21", "excl": "#626567", "head": DARK}
    WHITE = "#FFFFFF"

    def draw_box(ax, x, y, w, h, color, lines, fsizes=None, bold_first=True):
        box = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.14", facecolor=color, edgecolor="white", linewidth=2.5, zorder=3)
        ax.add_patch(box)
        if fsizes is None: fsizes = [10] * len(lines)
        for i, (line, fs) in enumerate(zip(lines, fsizes)):
            fw = "bold" if (bold_first and i == 0) else "normal"
            ax.text(x + w / 2, y + h - (i + 0.7) * h / len(lines), line, ha="center", va="center", fontsize=fs, fontfamily=FONT_FAMILY, fontweight=fw, color=WHITE, zorder=4, multialignment="center")

    def draw_excl(ax, x, y, w, h, lines):
        box = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1", facecolor=C["excl"], edgecolor="white", linewidth=1.5, linestyle="dashed", zorder=3)
        ax.add_patch(box)
        for i, line in enumerate(lines):
            ax.text(x + w / 2, y + h - (i + 0.65) * h / len(lines), line, ha="center", va="center", fontsize=8.0, fontfamily=FONT_FAMILY, color=WHITE, zorder=4, multialignment="center")

    BW, BH, BX, GAP = 5.2, 1.35, 3.3, 0.55
    y_id   = 8.5 - BH - 0.35
    y_tri  = y_id  - BH - GAP
    y_elig = y_tri - BH - GAP
    y_inc  = y_elig - BH - GAP
    
    draw_box(ax, BX, y_id, BW, BH, C["id"], ["① IDENTIFICAÇÃO", "315+ registros coletados via API Semantic Scholar", "8 queries × 3 protocolos  ·  Strings EN + PT"], fsizes=[11, 9.5, 9.0])
    draw_box(ax, BX, y_tri, BW, BH, C["tri"], ["② TRIAGEM", "Deduplicação por paperId  ·  Filtro temporal 2020–2026", "Classificação NLP por tema e relevância"], fsizes=[11, 9.5, 9.0])
    draw_box(ax, BX, y_elig, BW, BH, C["elig"], ["③ ELEGIBILIDADE", "Leitura de título, resumo e texto completo", "Peer-reviewed  ·  Idiomas: EN / PT"], fsizes=[11, 9.5, 9.0])
    draw_box(ax, BX, y_inc, BW, BH, C["inc"], [f"④ INCLUSÃO FINAL  —  {n_total} artigos", "13 estudos empíricos globais  ·  30 artigos teóricos", "30 artigos da produção brasileira"], fsizes=[11.5, 9.5, 9.0])

    cx = BX + BW / 2
    for y1, y2 in [(y_id, y_tri + BH), (y_tri, y_elig + BH), (y_elig, y_inc + BH)]:
        ax.annotate("", xy=(cx, y2), xytext=(cx, y1), arrowprops=dict(arrowstyle="-|>", color=DARK, lw=2.0), zorder=2)

    EX, EW, EH = 9.1, 2.7, 1.05
    excl_y = [y_id + (BH - EH)/2, y_tri + (BH - EH)/2, y_elig + (BH - EH)/2]
    excl_texts = [["Excluídos:", "Duplicatas / fora do", "período 2020–2026"], ["Excluídos:", "Sem peer-review /", "idioma irrelevante"], ["Excluídos:", "Sem foco em IA e", "Educação crítica"]]
    for ey, etxt in zip(excl_y, excl_texts):
        draw_excl(ax, EX, ey, EW, EH, etxt)
        ax.annotate("", xy=(EX, ey + EH/2), xytext=(BX + BW, ey + EH/2), arrowprops=dict(arrowstyle="-|>", color=C["excl"], lw=1.4), zorder=2)

    ax.text(6.0, 8.38, "Fluxo Metodológico PRISMA 2020 — Ciências Sociais Computacionais", ha="center", va="top", fontsize=12.5, fontfamily=FONT_FAMILY, fontweight="bold", color=DARK, zorder=5)
    fig.text(0.5, 0.005, "Fonte: elaboração própria. Protocolo adaptado de Page et al. (2021) para coleta automatizada via API e filtragem por NLP.", ha="center", fontsize=8, color=GRAY, fontfamily=FONT_FAMILY, style="italic")

    fig.tight_layout(rect=[0, 0.03, 1, 1])
    out = os.path.join(OUT_DIR, "fig2_prisma_flow.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=BG_PAGE)
    plt.close(fig)
    print(f"[✓] {out}")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURA 3 — Master Research Landscape (Eixos Dialéticos)
# ══════════════════════════════════════════════════════════════════════════════
def fig3_dialectical_axes(n_total: int):
    BG = "#0D1B2A"
    WHITE = "#E8EAF6"
    GOLD  = "#F0A500"
    C_AX1, C_AX2, C_AX3, C_CTR = "#E74C3C", "#8E44AD", "#27AE60", GOLD

    fig, ax = plt.subplots(figsize=(13, 8.5), facecolor=BG)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8.5)
    ax.axis("off")
    ax.set_facecolor(BG)

    def panel(cx, cy, w, h, edge_color, title, items, badge=None):
        ax.add_patch(mpatches.FancyBboxPatch((cx - w/2 + 0.06, cy - h/2 - 0.06), w, h, boxstyle="round,pad=0.18", facecolor="#000000", alpha=0.35, zorder=2))
        ax.add_patch(mpatches.FancyBboxPatch((cx - w/2, cy - h/2), w, h, boxstyle="round,pad=0.18", facecolor=edge_color + "1A", edgecolor=edge_color, linewidth=2.8, zorder=3))
        ax.add_patch(mpatches.FancyBboxPatch((cx - w/2 + 0.06, cy + h/2 - 0.52), w - 0.12, 0.46, boxstyle="round,pad=0.05", facecolor=edge_color + "55", edgecolor="none", zorder=4))
        ax.text(cx, cy + h/2 - 0.29, title, ha="center", va="center", fontsize=10.5, fontfamily=FONT_FAMILY, fontweight="bold", color=edge_color, zorder=5)
        for i, item in enumerate(items):
            ax.text(cx, cy + h/2 - 0.80 - i * 0.46, f"• {item}", ha="center", va="top", fontsize=8.8, fontfamily=FONT_FAMILY, color=WHITE + "CC", zorder=5, multialignment="center")

    CX, CY = 6.5, 4.25
    for r, alpha in [(1.35, 0.06), (1.05, 0.10), (0.80, 0.18)]:
        ax.add_patch(plt.Circle((CX, CY), r, facecolor=C_CTR, alpha=alpha, edgecolor="none", zorder=4))
    ax.add_patch(plt.Circle((CX, CY), 0.80, facecolor=C_CTR + "22", edgecolor=C_CTR, linewidth=2.8, zorder=5))
    ax.text(CX, CY + 0.22, "IA &\\nEDUCAÇÃO", ha="center", va="center", fontsize=10.5, fontweight="bold", color=C_CTR, fontfamily=FONT_FAMILY, zorder=6)
    ax.text(CX, CY - 0.38, f"{n_total} artigos\\nPRISMA 2020", ha="center", va="center", fontsize=7.5, color=WHITE + "88", fontfamily=FONT_FAMILY, zorder=6)
    
    panel(1.95, 6.30, 3.60, 3.20, C_AX1, "① CRISE DA PROMESSA", ["13 estudos empíricos globais", "53,8% achados negativos", "38,5% resultados mistos", "IA amplifica desigualdades", "D003, D008, D011 (evidências)"], badge="n=13")
    panel(11.05, 6.30, 3.60, 3.20, C_AX2, "② AMEAÇA DA DATIFICAÇÃO", ["30 artigos teóricos int'l", "Van Dijck · Zuboff · Noble", "Capitalismo de vigilância", "Colonialismo de dados", "97%: solucionismo crítico"], badge="n=30")
    panel(6.50, 1.45, 4.00, 2.50, C_AX3, "③ CONTEXTO BRASILEIRO", ["30 artigos nacionais  ·  63,3%: escola pública", "50,0%: formação docente  ·  ≈50% sem internet", "Soberania pedagógica  ·  LGPD insuficiente"], badge="n=30")

    ax.text(CX, 8.42, "Master Research Landscape — Articulação Dialética dos Três Eixos Analíticos", ha="center", va="top", fontsize=12.5, fontfamily=FONT_FAMILY, fontweight="bold", color=WHITE, zorder=5)

    fig.tight_layout(rect=[0, 0.03, 1, 0.97])
    out = os.path.join(OUT_DIR, "fig3_dialectical_axes.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"[✓] {out}")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  Gerando figuras para artigo Q1 — IA na Educação")
    print("=" * 60)

    # Carregar e combinar os dados
    if not META_CSV_PATH.exists() or not SCRAPED_CSV_PATH.exists():
        print("[!] Arquivos de dados não encontrados. Pulando geração de figuras.")
    else:
        df_meta = pd.read_csv(META_CSV_PATH)
        df_scraped = pd.read_csv(SCRAPED_CSV_PATH)
        combined_df = pd.concat([df_meta, df_scraped], ignore_index=True)
        records = combined_df.where(pd.notna(combined_df), None).to_dict('records')
        n_total = len(records)

        # Gerar figuras com os dados atualizados
        fig1_empirical_findings(records)
        fig2_prisma_flow(n_total)
        fig3_dialectical_axes(n_total)
        
        print("=" * 60)
        print(f"  Todas as figuras salvas em: {os.path.abspath(OUT_DIR)}")
        print("=" * 60)
