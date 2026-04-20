"""
generate_figures.py
===================
Gera as três figuras estratégicas do artigo:

  fig1_empirical_findings.png  — Donut: distribuição de achados empíricos
  fig2_prisma_flow.png         — Fluxo PRISMA + CSC metodológico
  fig3_dialectical_axes.png    — Eixos dialéticos (Master Research Landscape)

Saída: results/figures/
Uso  : python scripts/generate_figures.py
"""

import os
import matplotlib
matplotlib.use("Agg")          # backend sem display
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "figures")
os.makedirs(OUT_DIR, exist_ok=True)

DPI = 300
FONT_FAMILY = "DejaVu Sans"

# ──────────────────────────────────────────────────────────────────────────────
# FIGURA 1 — Donut: distribuição dos achados empíricos
# ──────────────────────────────────────────────────────────────────────────────
def fig1_empirical_findings():
    labels   = ["Negativo\n53,8%", "Misto / Neutro\n38,5%", "Positivo\n7,7%"]
    sizes    = [53.8, 38.5, 7.7]
    colors   = ["#C0392B", "#E67E22", "#27AE60"]
    explode  = (0.04, 0.02, 0.06)

    fig, ax = plt.subplots(figsize=(7, 6), facecolor="#FAFAFA")
    wedges, texts = ax.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        startangle=140,
        wedgeprops=dict(width=0.52, edgecolor="white", linewidth=2.5),
        textprops=dict(fontsize=11, fontfamily=FONT_FAMILY, fontweight="bold"),
    )

    # rótulo central
    ax.text(0, 0, "13\nestudos\nempíricos",
            ha="center", va="center", fontsize=13,
            fontfamily=FONT_FAMILY, fontweight="bold", color="#2C3E50")

    ax.set_title(
        "Distribuição dos Achados Empíricos Globais\n"
        "(Revisão Sistemática — PRISMA 2020)",
        fontsize=13, fontfamily=FONT_FAMILY, fontweight="bold",
        color="#2C3E50", pad=18,
    )

    # legenda extra
    legend_patches = [
        mpatches.Patch(color=colors[0], label="Negativo — 7 estudos (53,8%)"),
        mpatches.Patch(color=colors[1], label="Misto / Neutro — 5 estudos (38,5%)"),
        mpatches.Patch(color=colors[2], label="Positivo — 1 estudo (7,7%)"),
    ]
    ax.legend(handles=legend_patches, loc="lower center",
              bbox_to_anchor=(0.5, -0.12), ncol=1,
              fontsize=9.5, framealpha=0.8)

    fig.tight_layout()
    out = os.path.join(OUT_DIR, "fig1_empirical_findings.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor="#FAFAFA")
    plt.close(fig)
    print(f"[✓] {out}")


# ──────────────────────────────────────────────────────────────────────────────
# FIGURA 2 — Fluxo PRISMA + CSC
# ──────────────────────────────────────────────────────────────────────────────
def fig2_prisma_flow():
    fig, ax = plt.subplots(figsize=(10, 7), facecolor="#FAFAFA")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # ─── cores ───────────────────────────────────────────────────────────────
    C_HEADER  = "#1A252F"
    C_BOX1    = "#2980B9"   # identificação
    C_BOX2    = "#8E44AD"   # triagem
    C_BOX3    = "#16A085"   # elegibilidade
    C_BOX4    = "#C0392B"   # inclusão final
    C_SIDE    = "#7F8C8D"   # caixas laterais de exclusão
    WHITE     = "white"

    def rect(x, y, w, h, color, text, fontsize=10):
        r = mpatches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.12",
            facecolor=color, edgecolor=WHITE,
            linewidth=2.2, zorder=3,
        )
        ax.add_patch(r)
        ax.text(x + w/2, y + h/2, text,
                ha="center", va="center",
                fontsize=fontsize, color=WHITE,
                fontfamily=FONT_FAMILY, fontweight="bold",
                multialignment="center", zorder=4)

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>",
                                   color="#2C3E50", lw=2),
                    zorder=2)

    def side_box(x, y, w, h, text):
        r = mpatches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.1",
            facecolor=C_SIDE, edgecolor=WHITE,
            linewidth=1.5, linestyle="--", zorder=3,
        )
        ax.add_patch(r)
        ax.text(x + w/2, y + h/2, text,
                ha="center", va="center",
                fontsize=8.5, color=WHITE,
                fontfamily=FONT_FAMILY,
                multialignment="center", zorder=4)

    # ─── caixas principais (coluna central) ──────────────────────────────────
    #          x,   y,   w,   h
    rect(2.8, 8.2, 4.4, 1.2, C_BOX1,
         "① IDENTIFICAÇÃO\n315+ registros — API Semantic Scholar\n(8 queries × 3 protocolos NLP)")

    rect(2.8, 6.1, 4.4, 1.2, C_BOX2,
         "② TRIAGEM\nDeduplicação por paperId\nFiltro temporal 2020-2026 | Keyword NLP")

    rect(2.8, 4.0, 4.4, 1.2, C_BOX3,
         "③ ELEGIBILIDADE\nAvaliação por título, resumo e corpus\nPeer-reviewed | EN + PT")

    rect(2.8, 1.9, 4.4, 1.2, C_BOX4,
         "④ INCLUSÃO FINAL\n73 artigos selecionados\n13 empíricos · 30 teóricos · 30 BR")

    # ─── setas verticais ─────────────────────────────────────────────────────
    arrow(5.0, 8.2,  5.0, 7.35)
    arrow(5.0, 6.1,  5.0, 5.25)
    arrow(5.0, 4.0,  5.0, 3.15)

    # ─── caixas laterais (exclusões) ─────────────────────────────────────────
    side_box(7.6, 7.9, 1.9, 0.9,  "Excluídos:\nDuplicatas /\nFora do período")
    side_box(7.6, 5.8, 1.9, 0.9,  "Excluídos:\nSem peer-review /\nIdioma irrelevante")
    side_box(7.6, 3.7, 1.9, 0.9,  "Excluídos:\nSem foco em IA\ne Educação")

    # setas laterais
    for y_center in [8.35, 6.25, 4.15]:
        ax.annotate("", xy=(7.6, y_center), xytext=(7.2, y_center),
                    arrowprops=dict(arrowstyle="-|>", color=C_SIDE, lw=1.5),
                    zorder=2)
        ax.plot([7.2, 7.2], [y_center, y_center - 0.75], color=C_SIDE, lw=1.5, zorder=2)

    # ─── título ──────────────────────────────────────────────────────────────
    ax.set_title(
        "Fluxo Metodológico — PRISMA 2020 adaptado para\n"
        "Ciências Sociais Computacionais (CSC)",
        fontsize=13, fontfamily=FONT_FAMILY, fontweight="bold",
        color=C_HEADER, pad=8,
    )

    fig.tight_layout()
    out = os.path.join(OUT_DIR, "fig2_prisma_flow.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor="#FAFAFA")
    plt.close(fig)
    print(f"[✓] {out}")


# ──────────────────────────────────────────────────────────────────────────────
# FIGURA 3 — Eixos dialéticos (Master Research Landscape)
# ──────────────────────────────────────────────────────────────────────────────
def fig3_dialectical_axes():
    fig, ax = plt.subplots(figsize=(11, 7.5), facecolor="#12232E")
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    # ─── cores ───────────────────────────────────────────────────────────────
    C_AXIS1 = "#E74C3C"   # Crise da Promessa
    C_AXIS2 = "#9B59B6"   # Datificação
    C_AXIS3 = "#27AE60"   # Contexto BR
    C_CTR   = "#F39C12"   # centro
    BG      = "#12232E"
    WHITE   = "#ECF0F1"

    def hex_box(cx, cy, w, h, color, title, bullets, fontsize_title=10.5):
        """Caixa arredondada com título e bullets."""
        r = mpatches.FancyBboxPatch(
            (cx - w/2, cy - h/2), w, h,
            boxstyle="round,pad=0.15",
            facecolor=color + "22",   # transparência
            edgecolor=color, linewidth=2.5, zorder=3,
        )
        ax.add_patch(r)
        # título
        ax.text(cx, cy + h/2 - 0.28, title,
                ha="center", va="top",
                fontsize=fontsize_title, color=color,
                fontfamily=FONT_FAMILY, fontweight="bold", zorder=4)
        # bullets
        bullet_text = "\n".join(f"• {b}" for b in bullets)
        ax.text(cx, cy - h/2 + 0.18, bullet_text,
                ha="center", va="bottom",
                fontsize=8.5, color=WHITE,
                fontfamily=FONT_FAMILY, zorder=4,
                multialignment="center")

    def connector(x1, y1, x2, y2, color):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="<->",
                                   color=color, lw=2.2,
                                   connectionstyle="arc3,rad=0.08"),
                    zorder=2)

    # ─── círculo central ────────────────────────────────────────────────────
    cx, cy = 5.5, 3.75
    circle = plt.Circle((cx, cy), 0.95,
                         facecolor=C_CTR + "33",
                         edgecolor=C_CTR, linewidth=2.5, zorder=5)
    ax.add_patch(circle)
    ax.text(cx, cy + 0.18, "IA &\nEDUCAÇÃO",
            ha="center", va="center",
            fontsize=10, fontweight="bold",
            color=C_CTR, fontfamily=FONT_FAMILY, zorder=6)
    ax.text(cx, cy - 0.42, "73 artigos\nPRISMA 2020",
            ha="center", va="center",
            fontsize=7.5, color=WHITE + "99",
            fontfamily=FONT_FAMILY, zorder=6)

    # ─── Eixo 1 — Crise da Promessa (esquerda) ───────────────────────────────
    hex_box(1.6, 5.8, 3.0, 2.8, C_AXIS1,
            "① CRISE DA PROMESSA",
            ["13 estudos empíricos globais",
             "53,8% achados negativos",
             "38,5% resultados mistos",
             "IA amplifica desigualdades"])

    # ─── Eixo 2 — Datificação (direita) ─────────────────────────────────────
    hex_box(9.4, 5.8, 3.0, 2.8, C_AXIS2,
            "② AMEAÇA DA DATIFICAÇÃO",
            ["30 artigos teóricos",
             "Van Dijck · Zuboff · Noble",
             "Capitalismo de vigilância",
             "Colonialismo de dados"])

    # ─── Eixo 3 — Contexto BR (baixo) ────────────────────────────────────────
    hex_box(5.5, 1.1, 3.2, 2.5, C_AXIS3,
            "③ CONTEXTO BRASILEIRO",
            ["30 artigos nacionais",
             "63,3%: escola pública",
             "50,0%: formação docente",
             "Soberania pedagógica"])

    # ─── conectores entre eixos e centro ─────────────────────────────────────
    connector(3.1, 5.5, 4.6, 4.5, C_AXIS1)
    connector(7.9, 5.5, 6.4, 4.5, C_AXIS2)
    connector(5.5, 2.35, 5.5, 2.8, C_AXIS3)

    # ─── conector Eixo 1 ↔ Eixo 2 ────────────────────────────────────────────
    ax.annotate("", xy=(7.85, 5.65), xytext=(3.15, 5.65),
                arrowprops=dict(arrowstyle="<->",
                                color=WHITE + "44", lw=1.5,
                                linestyle="dashed"),
                zorder=2)

    # ─── rótulo das 5 teses ──────────────────────────────────────────────────
    ax.text(5.5, 0.26,
            "5 Teses para Políticas Públicas  ·  Agenda de Pesquisa (5 itens)",
            ha="center", va="bottom",
            fontsize=8.5, color=C_CTR,
            fontfamily=FONT_FAMILY, fontstyle="italic")

    # ─── título ──────────────────────────────────────────────────────────────
    ax.set_title(
        "Master Research Landscape — Eixos Dialéticos da Pesquisa",
        fontsize=13.5, fontfamily=FONT_FAMILY, fontweight="bold",
        color=WHITE, pad=10,
    )

    fig.tight_layout()
    out = os.path.join(OUT_DIR, "fig3_dialectical_axes.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"[✓] {out}")


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Gerando figuras do artigo...")
    fig1_empirical_findings()
    fig2_prisma_flow()
    fig3_dialectical_axes()
    print("Todas as figuras salvas em results/figures/")
