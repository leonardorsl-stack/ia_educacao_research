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

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "figures")
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
# FIGURA 1 — Gráfico de setores: Direção dos Achados Empíricos
# ══════════════════════════════════════════════════════════════════════════════
def fig1_empirical_findings():
    """
    Gráfico de setores (donut) mostrando a dissonância entre a promessa
    tecnológica e a evidência científica nos 13 estudos empíricos globais.
    """
    labels  = ["Negativo", "Misto /\nNeutro", "Positivo"]
    sizes   = [53.8, 38.5, 7.7]
    ns      = [7, 5, 1]
    colors  = [RED, ORANGE, GREEN]
    explode = (0.05, 0.02, 0.08)

    fig, ax = plt.subplots(figsize=(8, 6.5), facecolor=BG_PAGE)
    ax.set_facecolor(BG_PAGE)

    wedges, _ = ax.pie(
        sizes,
        explode=explode,
        colors=colors,
        startangle=135,
        wedgeprops=dict(width=0.55, edgecolor="white", linewidth=3.0),
        pctdistance=0.78,
    )

    # Anotações externas com setas elegantes
    annot_params = dict(
        fontsize=10.5, fontfamily=FONT_FAMILY, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                  edgecolor=GRAY, linewidth=0.8, alpha=0.92),
        arrowprops=dict(arrowstyle="-", color=GRAY, lw=1.2),
        va="center",
    )

    # Posições manuais para cada fatia
    annotations = [
        # (ângulo_graus, texto, xy_offset_frac, xytext_offset)
        (135 - 53.8/2,   f"Negativo\n{sizes[0]:.1f}%  ({ns[0]})",  RED,    (-1.55, 0.65)),
        (135 - 53.8 - 38.5/2, f"Misto / Neutro\n{sizes[1]:.1f}%  ({ns[1]})", ORANGE, (1.55, 0.0)),
        (135 - 53.8 - 38.5 - 7.7/2, f"Positivo\n{sizes[2]:.1f}%  ({ns[2]})", GREEN,  (1.45, -0.75)),
    ]

    for ang_deg, txt, clr, (xt, yt) in annotations:
        ang = np.deg2rad(ang_deg)
        r   = 0.78
        ax.annotate(
            txt,
            xy=(r * np.cos(ang), r * np.sin(ang)),
            xytext=(xt, yt),
            fontsize=10.5, fontfamily=FONT_FAMILY, fontweight="bold",
            color=clr,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                      edgecolor=clr, linewidth=1.2, alpha=0.95),
            arrowprops=dict(arrowstyle="-", color=clr, lw=1.2,
                            connectionstyle="arc3,rad=0.1"),
            va="center", ha="center",
        )

    # Texto central
    ax.text(0, 0.12, "13", ha="center", va="center",
            fontsize=30, fontfamily=FONT_FAMILY, fontweight="bold",
            color=DARK)
    ax.text(0, -0.28, "estudos\nempíricos\nglobais", ha="center", va="center",
            fontsize=9.5, fontfamily=FONT_FAMILY, color=GRAY,
            multialignment="center")

    # Título
    ax.set_title(
        "Direção dos Achados nos 13 Estudos Empíricos Globais\n"
        "Revisão Sistemática PRISMA 2020  ·  Período: 2021–2024",
        fontsize=11.5, fontfamily=FONT_FAMILY, fontweight="bold",
        color=DARK, pad=20, loc="center",
    )

    # Nota de rodapé
    fig.text(
        0.5, 0.01,
        "Nota: 53,8% dos achados negativos estão associados a amplificação de desigualdades "
        "e erosão da agência pedagógica.\nFonte: elaboração própria.",
        ha="center", fontsize=8, color=GRAY, fontfamily=FONT_FAMILY,
        style="italic",
    )

    fig.tight_layout(rect=[0, 0.05, 1, 1])
    out = os.path.join(OUT_DIR, "fig1_empirical_findings.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=BG_PAGE)
    plt.close(fig)
    print(f"[✓] {out}")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURA 2 — Fluxo PRISMA 2020 adaptado para CSC
# ══════════════════════════════════════════════════════════════════════════════
def fig2_prisma_flow():
    """
    Diagrama PRISMA 2020 adaptado para Ciências Sociais Computacionais.
    Quatro etapas verticais + caixas laterais de exclusão.
    73 artigos selecionados a partir de N > 315 registros via API.
    """
    fig, ax = plt.subplots(figsize=(12, 8.5), facecolor=BG_PAGE)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8.5)
    ax.axis("off")
    ax.set_facecolor(BG_PAGE)

    # Cores por etapa
    C = {
        "id":   "#1B4F8A",   # Identificação
        "tri":  "#6C3483",   # Triagem
        "elig": "#117A65",   # Elegibilidade
        "inc":  "#922B21",   # Inclusão
        "excl": "#626567",   # Exclusões
        "head": DARK,
    }
    WHITE = "#FFFFFF"

    # ─── helpers ──────────────────────────────────────────────────────────────
    def draw_box(ax, x, y, w, h, color, lines, fsizes=None, bold_first=True):
        """Caixa arredondada com texto multi-linha."""
        box = mpatches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.14",
            facecolor=color, edgecolor="white",
            linewidth=2.5, zorder=3,
        )
        ax.add_patch(box)
        if fsizes is None:
            fsizes = [10] * len(lines)
        total_lines = len(lines)
        for i, (line, fs) in enumerate(zip(lines, fsizes)):
            fw = "bold" if (bold_first and i == 0) else "normal"
            ax.text(
                x + w / 2,
                y + h - (i + 0.7) * h / total_lines,
                line,
                ha="center", va="center",
                fontsize=fs, fontfamily=FONT_FAMILY,
                fontweight=fw, color=WHITE,
                zorder=4, multialignment="center",
            )

    def draw_arrow(ax, x1, y1, x2, y2, color=DARK, lw=2.0):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="-|>", color=color, lw=lw),
            zorder=2,
        )

    def draw_excl(ax, x, y, w, h, lines):
        box = mpatches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.1",
            facecolor=C["excl"], edgecolor="white",
            linewidth=1.5, linestyle="dashed", zorder=3,
        )
        ax.add_patch(box)
        for i, line in enumerate(lines):
            ax.text(
                x + w / 2,
                y + h - (i + 0.65) * h / len(lines),
                line,
                ha="center", va="center",
                fontsize=8.0, fontfamily=FONT_FAMILY,
                color=WHITE, zorder=4, multialignment="center",
            )

    # ─── caixas principais ────────────────────────────────────────────────────
    BW, BH = 5.2, 1.35
    BX     = 3.3
    GAP    = 0.55

    # y-coords (de cima para baixo)
    y_id   = 8.5 - BH - 0.35           # ≈ 6.80
    y_tri  = y_id  - BH - GAP          # ≈ 4.90
    y_elig = y_tri - BH - GAP          # ≈ 3.00
    y_inc  = y_elig - BH - GAP         # ≈ 1.10

    draw_box(ax, BX, y_id, BW, BH, C["id"],
             ["① IDENTIFICAÇÃO",
              "315+ registros coletados via API Semantic Scholar",
              "8 queries × 3 protocolos  ·  Strings EN + PT"],
             fsizes=[11, 9.5, 9.0])

    draw_box(ax, BX, y_tri, BW, BH, C["tri"],
             ["② TRIAGEM",
              "Deduplicação por paperId  ·  Filtro temporal 2020–2026",
              "Classificação NLP por tema e relevância"],
             fsizes=[11, 9.5, 9.0])

    draw_box(ax, BX, y_elig, BW, BH, C["elig"],
             ["③ ELEGIBILIDADE",
              "Leitura de título, resumo e texto completo",
              "Peer-reviewed  ·  Idiomas: EN / PT"],
             fsizes=[11, 9.5, 9.0])

    draw_box(ax, BX, y_inc, BW, BH, C["inc"],
             ["④ INCLUSÃO FINAL  —  73 artigos",
              "13 estudos empíricos globais  ·  30 artigos teóricos",
              "30 artigos da produção brasileira"],
             fsizes=[11.5, 9.5, 9.0])

    # ─── setas verticais ─────────────────────────────────────────────────────
    cx = BX + BW / 2
    draw_arrow(ax, cx, y_id,   cx, y_tri  + BH)
    draw_arrow(ax, cx, y_tri,  cx, y_elig + BH)
    draw_arrow(ax, cx, y_elig, cx, y_inc  + BH)

    # ─── caixas de exclusão ──────────────────────────────────────────────────
    EX, EW, EH = 9.1, 2.7, 1.05
    excl_y = [y_id + (BH - EH)/2, y_tri + (BH - EH)/2, y_elig + (BH - EH)/2]
    excl_texts = [
        ["Excluídos:", "Duplicatas / fora do", "período 2020–2026"],
        ["Excluídos:", "Sem peer-review /", "idioma irrelevante"],
        ["Excluídos:", "Sem foco em IA e", "Educação crítica"],
    ]
    for ey, etxt in zip(excl_y, excl_texts):
        draw_excl(ax, EX, ey, EW, EH, etxt)
        # seta horizontal
        ax.annotate("", xy=(EX, ey + EH/2),
                    xytext=(BX + BW, ey + EH/2),
                    arrowprops=dict(arrowstyle="-|>",
                                   color=C["excl"], lw=1.4),
                    zorder=2)

    # ─── rótulos de fase (lado esquerdo) ─────────────────────────────────────
    phase_labels = [
        (y_id,   "FASE 1", C["id"]),
        (y_tri,  "FASE 2", C["tri"]),
        (y_elig, "FASE 3", C["elig"]),
        (y_inc,  "FASE 4", C["inc"]),
    ]
    for yp, lbl, clr in phase_labels:
        ax.text(BX - 0.22, yp + BH/2, lbl,
                ha="right", va="center",
                fontsize=8, fontfamily=FONT_FAMILY,
                fontweight="bold", color=clr,
                rotation=90, zorder=5)

    # ─── título ──────────────────────────────────────────────────────────────
    ax.text(6.0, 8.38,
            "Fluxo Metodológico PRISMA 2020 — Ciências Sociais Computacionais",
            ha="center", va="top",
            fontsize=12.5, fontfamily=FONT_FAMILY,
            fontweight="bold", color=DARK, zorder=5)

    # ─── nota rodapé ─────────────────────────────────────────────────────────
    fig.text(
        0.5, 0.005,
        "Fonte: elaboração própria. Protocolo adaptado de Page et al. (2021) "
        "para coleta automatizada via API e filtragem por NLP.",
        ha="center", fontsize=8, color=GRAY, fontfamily=FONT_FAMILY,
        style="italic",
    )

    fig.tight_layout(rect=[0, 0.03, 1, 1])
    out = os.path.join(OUT_DIR, "fig2_prisma_flow.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=BG_PAGE)
    plt.close(fig)
    print(f"[✓] {out}")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURA 3 — Master Research Landscape (Eixos Dialéticos)
# ══════════════════════════════════════════════════════════════════════════════
def fig3_dialectical_axes():
    """
    Mapa conceitual com os três eixos analíticos articulados dialeticamente:
    ① Crise da Promessa  ·  ② Ameaça da Datificação  ·  ③ Contexto Brasileiro
    Converge para as 5 teses de política pública.
    """
    BG = "#0D1B2A"
    WHITE = "#E8EAF6"
    GOLD  = "#F0A500"

    C_AX1 = "#E74C3C"   # vermelho — Crise da Promessa
    C_AX2 = "#8E44AD"   # roxo — Datificação
    C_AX3 = "#27AE60"   # verde — Contexto BR
    C_CTR = GOLD        # dourado — centro

    fig, ax = plt.subplots(figsize=(13, 8.5), facecolor=BG)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8.5)
    ax.axis("off")
    ax.set_facecolor(BG)

    # ─── helper: painel temático ──────────────────────────────────────────────
    def panel(cx, cy, w, h, edge_color, title, items, badge=None):
        # sombra
        shadow = mpatches.FancyBboxPatch(
            (cx - w/2 + 0.06, cy - h/2 - 0.06), w, h,
            boxstyle="round,pad=0.18",
            facecolor="#000000", alpha=0.35, zorder=2,
        )
        ax.add_patch(shadow)

        # painel
        box = mpatches.FancyBboxPatch(
            (cx - w/2, cy - h/2), w, h,
            boxstyle="round,pad=0.18",
            facecolor=edge_color + "1A",
            edgecolor=edge_color, linewidth=2.8, zorder=3,
        )
        ax.add_patch(box)

        # faixa de título
        title_band = mpatches.FancyBboxPatch(
            (cx - w/2 + 0.06, cy + h/2 - 0.52), w - 0.12, 0.46,
            boxstyle="round,pad=0.05",
            facecolor=edge_color + "55",
            edgecolor="none", zorder=4,
        )
        ax.add_patch(title_band)

        ax.text(cx, cy + h/2 - 0.29, title,
                ha="center", va="center",
                fontsize=10.5, fontfamily=FONT_FAMILY,
                fontweight="bold", color=edge_color, zorder=5)

        for i, item in enumerate(items):
            ax.text(cx, cy + h/2 - 0.80 - i * 0.46,
                    f"• {item}",
                    ha="center", va="top",
                    fontsize=8.8, fontfamily=FONT_FAMILY,
                    color=WHITE + "CC", zorder=5,
                    multialignment="center")

        if badge:
            bx = cx + w/2 - 0.02
            by = cy + h/2 - 0.02
            bc = plt.Circle((bx, by), 0.32,
                             facecolor=edge_color,
                             edgecolor="white", linewidth=1.5, zorder=6)
            ax.add_patch(bc)
            ax.text(bx, by, badge,
                    ha="center", va="center",
                    fontsize=7.5, fontfamily=FONT_FAMILY,
                    fontweight="bold", color="white", zorder=7)

    # ─── conector dialético ────────────────────────────────────────────────────
    def connect(x1, y1, x2, y2, color, style="arc3,rad=0.15"):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(
                        arrowstyle="<->", color=color,
                        lw=2.0, connectionstyle=style,
                    ), zorder=2)

    # ─── círculo central ──────────────────────────────────────────────────────
    CX, CY = 6.5, 4.25
    for r, alpha in [(1.35, 0.06), (1.05, 0.10), (0.80, 0.18)]:
        glow = plt.Circle((CX, CY), r,
                           facecolor=C_CTR, alpha=alpha,
                           edgecolor="none", zorder=4)
        ax.add_patch(glow)
    core = plt.Circle((CX, CY), 0.80,
                       facecolor=C_CTR + "22",
                       edgecolor=C_CTR, linewidth=2.8, zorder=5)
    ax.add_patch(core)
    ax.text(CX, CY + 0.22, "IA &\nEDUCAÇÃO",
            ha="center", va="center",
            fontsize=10.5, fontweight="bold",
            color=C_CTR, fontfamily=FONT_FAMILY, zorder=6)
    ax.text(CX, CY - 0.38, "73 artigos\nPRISMA 2020",
            ha="center", va="center",
            fontsize=7.5, color=WHITE + "88",
            fontfamily=FONT_FAMILY, zorder=6)

    # ─── três painéis ─────────────────────────────────────────────────────────
    panel(
        1.95, 6.30, 3.60, 3.20,
        C_AX1,
        "① CRISE DA PROMESSA",
        [
            "13 estudos empíricos globais",
            "53,8% achados negativos",
            "38,5% resultados mistos",
            "IA amplifica desigualdades",
            "D003, D008, D011 (evidências)",
        ],
        badge="n=13",
    )

    panel(
        11.05, 6.30, 3.60, 3.20,
        C_AX2,
        "② AMEAÇA DA DATIFICAÇÃO",
        [
            "30 artigos teóricos int'l",
            "Van Dijck · Zuboff · Noble",
            "Capitalismo de vigilância",
            "Colonialismo de dados",
            "97%: solucionismo crítico",
        ],
        badge="n=30",
    )

    panel(
        6.50, 1.45, 4.00, 2.50,
        C_AX3,
        "③ CONTEXTO BRASILEIRO",
        [
            "30 artigos nacionais  ·  63,3%: escola pública",
            "50,0%: formação docente  ·  ≈50% sem internet",
            "Soberania pedagógica  ·  LGPD insuficiente",
        ],
        badge="n=30",
    )

    # ─── conectores eixo↔centro ───────────────────────────────────────────────
    connect(3.60, 6.00, 5.72, 4.80, C_AX1, "arc3,rad=-0.1")
    connect(8.85, 6.00, 7.28, 4.80, C_AX2, "arc3,rad=0.1")
    connect(6.50, 2.70, 6.50, 3.46, C_AX3, "arc3,rad=0.0")

    # conector eixo1↔eixo2 (arco superior)
    ax.annotate("", xy=(8.70, 6.55), xytext=(3.75, 6.55),
                arrowprops=dict(arrowstyle="<->",
                                color=WHITE + "33", lw=1.5,
                                linestyle="dashed",
                                connectionstyle="arc3,rad=-0.25"),
                zorder=2)

    # ─── 5 teses (rodapé interno) ─────────────────────────────────────────────
    ax.text(CX, 0.48,
            "⟶  5 Teses para Políticas Públicas  ·  Agenda de Pesquisa Prioritária",
            ha="center", va="bottom",
            fontsize=9, color=C_CTR,
            fontfamily=FONT_FAMILY, fontstyle="italic",
            fontweight="bold", zorder=5)

    # ─── título ───────────────────────────────────────────────────────────────
    ax.text(CX, 8.42,
            "Master Research Landscape — Articulação Dialética dos Três Eixos Analíticos",
            ha="center", va="top",
            fontsize=12.5, fontfamily=FONT_FAMILY,
            fontweight="bold", color=WHITE, zorder=5)

    # ─── nota de rodapé ───────────────────────────────────────────────────────
    fig.text(
        0.5, 0.005,
        "Fonte: elaboração própria. Os conectores bidirecionais (⟷) indicam relações "
        "dialéticas de tensão e mútua determinação entre os eixos.",
        ha="center", fontsize=8, color=WHITE + "88",
        fontfamily=FONT_FAMILY, style="italic",
    )

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
    fig1_empirical_findings()
    fig2_prisma_flow()
    fig3_dialectical_axes()
    print("=" * 60)
    print(f"  Todas as figuras salvas em: {os.path.abspath(OUT_DIR)}")
    print("=" * 60)
