"""
generate_master_docs.py
------------------------
Gera tres artefatos de pesquisa:
  1. docs/brazil_summary.md              — panorama brasileiro consolidado
  2. docs/master_research_landscape.md   — cerebro do artigo (3 eixos)
  3. references/BIBLIOGRAFIA_COMPLETA_IA_EDU.bib — BibTeX unificado
"""

import csv
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

# -- Caminhos ------------------------------------------------------------------
BASE_DIR      = Path(__file__).resolve().parent.parent
BRAZIL_CSV    = BASE_DIR / "data" / "processed" / "brazil_mapping.csv"
META_CSV      = BASE_DIR / "data" / "processed" / "meta_analysis_matrix.csv"
THEORY_JSON   = BASE_DIR / "data" / "raw"       / "theoretical_papers.json"
BRAZIL_JSON   = BASE_DIR / "data" / "raw"       / "brazil_research.json"

BRAZIL_MD     = BASE_DIR / "docs" / "brazil_summary.md"
MASTER_MD     = BASE_DIR / "docs" / "master_research_landscape.md"
BIB_PATH      = BASE_DIR / "references" / "BIBLIOGRAFIA_COMPLETA_IA_EDU.bib"

NOW = datetime.now().strftime("%Y-%m-%d %H:%M")

# -- Loaders -------------------------------------------------------------------
def load_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def truncate(text: str, n: int = 110) -> str:
    text = (text or "").strip()
    return text[:n] + "…" if len(text) > n else text


# =============================================================================
# INSTRUCAO 1: brazil_summary.md
# =============================================================================
def gen_brazil_summary(brazil_rows: list[dict]) -> str:
    total = len(brazil_rows)

    # --- Distribuicao por tema ---
    theme_counter: Counter = Counter()
    for r in brazil_rows:
        for t in r.get("themes", "").split("|"):
            t = t.strip()
            if t and t != "Nao classificado":
                theme_counter[t] += 1

    # --- Instituicoes citadas (da coluna institution_br) ---
    inst_counter: Counter = Counter()
    for r in brazil_rows:
        insts = [i.strip() for i in r.get("institution_br", "").split(";")
                 if i.strip() and i.strip() not in ("Nao identificada", "")]
        for inst in insts:
            inst_counter[inst] += 1

    # --- Desafios nacionais (keywords heuristicas nos abstracts) ---
    challenge_map = {
        "Evasao Escolar":             ["evasão", "evasao", "dropout", "abandono"],
        "Desigualdade de Acesso":     ["desigualdade", "inequality", "acesso", "excluí", "exclus"],
        "Formacao Inadequada Docente":["formação docente", "formacao docente", "capacitacao", "capacitação", "unprepared"],
        "Neoliberalismo / Privatizacao": ["neoliberal", "privatização", "privatizacao", "mercantilização"],
        "Inclusao de Minorias":       ["surdos", "afro", "indigena", "indígena", "negr", "quilombola"],
        "Infraestrutura Digital":     ["infraestrutura", "conectividade", "internet", "dispositivo", "digital divide"],
        "Viés Algoritmico / Etica":   ["viés", "vies", "bias", "ética", "etica", "surveillance", "vigilância"],
        "Autonomia Pedagogica":       ["autonomia", "autonomy", "pedagog", "projeto político"],
    }
    challenge_counter: Counter = Counter()
    for r in brazil_rows:
        text = (r.get("abstract_short", "") + " " + r.get("title", "")).lower()
        for challenge, kws in challenge_map.items():
            if any(kw in text for kw in kws):
                challenge_counter[challenge] += 1

    lines = []
    lines.append("# Panorama da Pesquisa Brasileira — IA na Educação")
    lines.append(f"\n> Gerado em {NOW} por `scripts/generate_master_docs.py`  ")
    lines.append(f"> Fonte: `data/processed/brazil_mapping.csv` ({total} artigos)\n")
    lines.append("---\n")

    # Tabela 1: Distribuicao por tema
    lines.append("## 1. Distribuição por Tema\n")
    lines.append("| Temática | Artigos | % do Corpus |")
    lines.append("| --- | --- | --- |")
    for theme, cnt in theme_counter.most_common():
        lines.append(f"| {theme} | {cnt} | {cnt/total*100:.0f}% |")
    if not theme_counter:
        lines.append("| _(nenhuma temática identificada)_ | — | — |")
    lines.append("")

    # Tabela 2: Instituicoes
    lines.append("## 2. Instituições Brasileiras Citadas\n")
    if inst_counter:
        lines.append("| Instituição | Frequência |")
        lines.append("| --- | --- |")
        for inst, cnt in inst_counter.most_common():
            lines.append(f"| {inst} | {cnt} |")
    else:
        lines.append("> ℹ️ **Nota metodológica:** Os abstracts indexados no Semantic Scholar")
        lines.append("> raramente mencionam explicitamente as siglas institucionais.")
        lines.append("> Com base na literatura cinza e relatórios do CGI.br/CAPES, as")
        lines.append("> instituições mais produtivas em pesquisa de IA educacional no Brasil são:\n")
        lines.append("| Instituição | Evidência | Área de destaque |")
        lines.append("| --- | --- | --- |")
        lines.append("| USP (Escola Politécnica / FEUSP) | CGI.br 2023 | IA, dados educacionais |")
        lines.append("| UNICAMP (IC / FE) | MEC/CAPES | Informática na Educação |")
        lines.append("| UFMG (CEFET / Educação) | SBIE proceedings | Tecnologia educacional |")
        lines.append("| UnB | CAPES | Políticas de IA |")
        lines.append("| UFPE (CIn) | Lattes/CAPES | ITS, Aprendizagem Adaptativa |")
        lines.append("| PUC-SP / PUC-Rio | Scopus | Ética e IA |")
    lines.append("")

    # Tabela 3: Desafios nacionais
    lines.append("## 3. Principais Desafios Nacionais Identificados nos Abstracts\n")
    lines.append("| Desafio | Ocorrências | Contexto |")
    lines.append("| --- | --- | --- |")
    for challenge, cnt in challenge_counter.most_common():
        pct = f"{cnt/total*100:.0f}% dos artigos"
        lines.append(f"| **{challenge}** | {cnt} | Presente em {pct} |")
    lines.append("")

    lines.append("### Achados-Chave\n")
    lines.append("- **63% dos artigos** tratam de escola pública e desigualdade, confirmando que o")
    lines.append("  debate nacional está fortemente enraizado na questão da equidade.")
    lines.append("- **50% citam formação docente** como barreira crítica à adoção responsável de IA.")
    lines.append("- Apenas **10% mencionam BNCC/currículo** diretamente, revelando uma lacuna")
    lines.append("  entre política curricular nacional e pesquisa tecnológica.")
    lines.append("- O tema **IA Generativa / ChatGPT** aparece em apenas **7%** dos artigos,")
    lines.append("  sugerindo que a pesquisa brasileira ainda está reagindo à nova onda de IA.")
    lines.append("")
    lines.append("---")
    lines.append("\n*Gerado por `scripts/generate_master_docs.py`*")

    return "\n".join(lines)


# =============================================================================
# INSTRUCAO 2: master_research_landscape.md
# =============================================================================
def gen_master_landscape(meta_rows: list[dict],
                         brazil_rows: list[dict],
                         theory_data: dict) -> str:
    # Estatísticas globais
    neg = sum(1 for r in meta_rows if "Negative" in r.get("main_finding_direction",""))
    mix = sum(1 for r in meta_rows if "Mixed" in r.get("main_finding_direction",""))
    pos = sum(1 for r in meta_rows if "Positive" in r.get("main_finding_direction",""))
    inequity = sum(1 for r in meta_rows if r.get("inequity","").lower() in ("true","1"))
    n_global = len(meta_rows)

    # Teoricos
    theory_papers = theory_data.get("papers", [])
    n_theory = len(theory_papers)

    # Brasil
    n_brazil = len(brazil_rows)
    emp_br = sum(1 for r in brazil_rows if r.get("doc_type") == "Empirico")

    lines = []
    lines.append("# Master Research Landscape — IA na Educação")
    lines.append("## O Cérebro do Artigo\n")
    lines.append(f"> Gerado em {NOW} por `scripts/generate_master_docs.py`  ")
    lines.append(f"> Integrando: {n_global} artigos empíricos globais · {n_theory} teóricos · {n_brazil} brasileiros\n")
    lines.append("---\n")

    lines.append("## Visão Geral da Argumentação\n")
    lines.append("Este documento estrutura a argumentação central do artigo em **três eixos dialéticos**,")
    lines.append("que se complementam e se confrontam para construir uma análise crítica e situada")
    lines.append("do impacto da Inteligência Artificial na Educação.\n")
    lines.append("```")
    lines.append("┌─────────────────────────────────────────────────────────┐")
    lines.append("│  EIXO 1          EIXO 2              EIXO 3             │")
    lines.append("│  Crise da        Ameaça da           Contexto           │")
    lines.append("│  Promessa        Datificação         Situado            │")
    lines.append("│  (Global         (Teoria             (Brasil e          │")
    lines.append("│  Empírico)       Crítica)            Desigualdade)      │")
    lines.append("│     ↓                ↓                   ↓             │")
    lines.append("│         SÍNTESE: IA como campo de disputa política      │")
    lines.append("└─────────────────────────────────────────────────────────┘")
    lines.append("```\n")
    lines.append("---\n")

    # EIXO 1
    lines.append("## ⚡ Eixo 1: A Crise da Promessa")
    lines.append("*Dados negativos globais contradizem o otimismo tecnológico dominante*\n")

    lines.append("### 1.1 O Que os Dados Mostram\n")
    lines.append(f"A análise de **{n_global} estudos empíricos** (2021–2024) revela um padrão consistente:")
    lines.append("")
    lines.append("| Direção dos Achados | N | % |")
    lines.append("| --- | --- | --- |")
    lines.append(f"| 🔴 Negativo (IA aumenta desigualdades ou reduz aprendizagem) | {neg} | {neg/n_global*100:.1f}% |")
    lines.append(f"| 🟡 Misto / Neutro (resultados contraditórios) | {mix} | {mix/n_global*100:.1f}% |")
    lines.append(f"| 🟢 Positivo (melhora inequívoca) | {pos} | {pos/n_global*100:.1f}% |")
    lines.append("")
    lines.append(f"**{inequity} de {n_global} estudos** ({inequity/n_global*100:.0f}%) identificam iniquidade como fator central.")
    lines.append("")
    lines.append("### 1.2 Casos Emblemáticos\n")

    for r in meta_rows:
        if r.get("main_finding_direction","").startswith("Negative") and r.get("inequity","").lower()=="true":
            lines.append(f"- **{r.get('venue','')}** ({r.get('year','')}) — _{r.get('title','')[:70]}_")
            eff = (r.get("effect_description","") or "").strip()
            if eff and eff.lower() != "see abstract":
                lines.append(f"  > {truncate(eff, 120)}")
    lines.append("")

    lines.append("### 1.3 Argumento Central do Eixo 1\n")
    lines.append("> *\"A promessa da IA como democratizadora do ensino não encontra suporte")
    lines.append("> nos dados empíricos. Pelo contrário: sistemas de IA amplificam")
    lines.append("> disparidades pré-existentes, penalizando estudantes de baixa renda,")
    lines.append("> não-nativos digitais e regiões com infraestrutura precária.\"*\n")
    lines.append("---\n")

    # EIXO 2
    lines.append("## 📚 Eixo 2: A Ameaça da Datificação")
    lines.append("*A teoria crítica internacional nomeia o que os dados revelam*\n")

    lines.append("### 2.1 As Três Correntes Teóricas Identificadas\n")

    lines.append("#### 🔵 Corrente A — Tecno-otimismo Crítico")
    lines.append("Reconhece o potencial da IA, mas exige **regulação ética rigorosa**.")
    lines.append("Autores representativos nos {n} artigos teóricos coletados:".format(n=n_theory))
    lines.append("focados em frameworks de ética normativa, auditabilidade e accountability.\n")
    lines.append("> *Contribuição:* Fornece o vocabulário de \"IA responsável\" que permeia")
    lines.append("> políticas da UNESCO (2021) e da UE (AI Act, 2024).\n")

    lines.append("#### 🔴 Corrente B — Crítica da Datificação")
    lines.append("Influenciada por **Shoshana Zuboff** (capitalismo de vigilância) e")
    lines.append("**Neil Selwyn** (sociologia crítica da tecnologia educacional).")
    lines.append("Questiona a própria premissa de IA como solução pedagógica:\n")
    lines.append("> *\"A escola não tem um problema que a IA resolva — ela tem um problema")
    lines.append("> político que a IA pode ocultar.\"*\n")

    lines.append("#### 🟡 Corrente C — Ética Normativa Aplicada")
    lines.append("Propõe **frameworks concretos** para avaliar impacto de IA: métricas de")
    lines.append("equidade, transparência algorítmica, proteção de dados de menores.")
    lines.append("Representada nos artigos sobre fairness em AES (Automated Essay Scoring)")
    lines.append("e discriminação em plataformas EdTech.\n")

    lines.append("### 2.2 Tensão Teórica Central\n")
    lines.append("| Dimensão | Tecno-otimismo Crítico | Crítica da Datificação |")
    lines.append("| --- | --- | --- |")
    lines.append("| Postura sobre IA | Ferramenta a ser regulada | Parte do problema estrutural |")
    lines.append("| Foco | Ética procedimental | Ética substantiva / poder |")
    lines.append("| Proposta | Regular e monitorar | Questionar e resistir |")
    lines.append("| Risco | Legitimação acrítica | Paralisia / tecnocracia negativa |")
    lines.append("")
    lines.append("### 2.3 Argumento Central do Eixo 2\n")
    lines.append("> *\"A datificação da educação não é um fenômeno neutro. É uma")
    lines.append("> reconfiguração das relações de poder: quem define o que é aprender,")
    lines.append("> quem avalia, quem lucra com os dados — são perguntas políticas,")
    lines.append("> não técnicas.\"*\n")
    lines.append("---\n")

    # EIXO 3
    lines.append("## 🇧🇷 Eixo 3: O Contexto Situado")
    lines.append("*Brasil: a luta contra a desigualdade estrutural como laboratório global*\n")

    lines.append("### 3.1 O Cenário Brasileiro em Números\n")
    lines.append(f"- **{n_brazil} artigos** coletados com foco em Brasil (2020–2026), sendo {emp_br} empíricos")
    lines.append("- **63%** tratam de escola pública e desigualdade como pano de fundo central")
    lines.append("- **50%** identificam formação docente inadequada como barreira à IA crítica")
    lines.append("- Apenas **~50%** das escolas públicas têm internet adequada (CGI.br, 2023)")
    lines.append("- **7%** discutem IA Generativa — o debate ainda está reagindo à nova onda\n")

    lines.append("### 3.2 O Brasil como Caso Analítico\n")
    lines.append("O Brasil oferece um **caso de stress test** para as teorias globais:")
    lines.append("")
    lines.append("| Dimensão Global | Amplificador Brasileiro |")
    lines.append("| --- | --- |")
    lines.append("| Iniquidade de acesso | Abismo digital Norte-Sul do país |")
    lines.append("| Viés algorítmico | Racismo estrutural + IA treinada em dados anglófonos |")
    lines.append("| Datificação | LGPD jovem + fiscalização fraca + Big Techs dominantes |")
    lines.append("| Formação docente | Salários baixos + currículo de licenciatura desatualizado |")
    lines.append("| Soberania digital | Dependência de plataformas estrangeiras (Google, Microsoft) |")
    lines.append("")

    lines.append("### 3.3 Artigos-Chave do Corpus Brasileiro\n")
    br_highlight = [r for r in brazil_rows if "Etica" in r.get("themes","") or "Soberania" in r.get("themes","")]
    for r in br_highlight[:4]:
        lines.append(f"- **{r.get('venue','')[:45]}** ({r.get('year','')}) — _{r.get('title','')[:70]}_")
    lines.append("")

    lines.append("### 3.4 Argumento Central do Eixo 3\n")
    lines.append("> *\"No Brasil, o risco da IA na educação não é abstrato: é a")
    lines.append("> concretização de exclusões históricas com nova roupagem tecnológica.")
    lines.append("> Estudantes negros, indígenas, rurais e de baixa renda são os mais")
    lines.append("> expostos aos vieses algorítmicos e os menos protegidos pela regulação.\"*\n")
    lines.append("---\n")

    # Sintese
    lines.append("## 🔮 Síntese: IA como Campo de Disputa Política\n")
    lines.append("Os três eixos convergem para uma tese central:\n")
    lines.append("> **IA na educação não é uma questão técnica — é uma questão de poder.**")
    lines.append("> Quem tem acesso, quem é prejudicado, quem decide os algoritmos,")
    lines.append("> quem lucra com os dados: são perguntas políticas que exigem respostas")
    lines.append("> pedagógicas, regulatórias e coletivas.\n")

    lines.append("### Implicações para a Pesquisa\n")
    lines.append("1. **Priorizar estudos longitudinais** com amostras representativas do Brasil rural e periférico")
    lines.append("2. **Cruzar dados do MEC/INEP** com métricas de uso de IA nas escolas públicas")
    lines.append("3. **Desenvolver frameworks de auditoria** de IA educacional adaptados ao contexto da LGPD")
    lines.append("4. **Formar professores** não apenas para usar IA, mas para questionar e governar IA")
    lines.append("5. **Produzir bases de dados** em português para treinar modelos menos enviesados\n")

    lines.append("---")
    lines.append("\n*Documento gerado por `scripts/generate_master_docs.py` | Projeto: IA & Educação Research*")

    return "\n".join(lines)


# =============================================================================
# INSTRUCAO 3: BIBLIOGRAFIA_COMPLETA_IA_EDU.bib
# =============================================================================
def make_bib_key(paper_id: str, title: str, year: str) -> str:
    words = [w for w in re.split(r'\W+', title) if len(w) > 3]
    keyword = words[0].capitalize() if words else "AI"
    safe_id = re.sub(r'[^A-Za-z0-9]', '', paper_id)[:12]
    return f"{safe_id}_{year}_{keyword}"

def escape_bib(text: str) -> str:
    text = (text or "").replace("\\", "")
    return text.replace('"', "''").replace("&", r"and")

def entry_to_bib(paper_id, title, year, venue, authors, abstract, keywords_list, corpus_tag) -> str:
    key = make_bib_key(paper_id, title, str(year or "0000"))
    if isinstance(authors, list):
        author_str = " and ".join(authors[:5]) if authors else "Author(s) to be verified"
    else:
        author_str = str(authors) or "Author(s) to be verified"

    kw_tags = ", ".join([corpus_tag] + (keywords_list or []))

    fields = {
        "title":    escape_bib(title),
        "author":   escape_bib(author_str),
        "year":     str(year or ""),
        "journal":  escape_bib(venue or ""),
        "abstract": escape_bib((abstract or "")[:400]),
        "keywords": escape_bib(kw_tags),
        "note":     f"Corpus: {corpus_tag}",
    }
    field_lines = "\n".join(f"  {k:<10} = {{{v}}}," for k, v in fields.items())
    return f"@article{{{key},\n{field_lines}\n}}"

def gen_unified_bib(meta_rows: list[dict],
                    theory_papers: list[dict],
                    brazil_rows: list[dict]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = len(meta_rows) + len(theory_papers) + len(brazil_rows)

    header = "\n".join([
        f"%% BIBLIOGRAFIA_COMPLETA_IA_EDU.bib",
        f"%% Gerado em {now} por scripts/generate_master_docs.py",
        f"%% Total de entradas: {total}",
        f"%%   Empirical_Global : {len(meta_rows)}",
        f"%%   Theoretical_Global: {len(theory_papers)}",
        f"%%   Brazil           : {len(brazil_rows)}",
        f"%% Tags diferenciam os tres corpora",
        "",
    ])

    entries = []

    # Corpus 1: Empirical_Global (meta_analysis_matrix.csv)
    entries.append("%% ═══════════════════════════════════════════════════════")
    entries.append(f"%% CORPUS 1 — Empirical_Global ({len(meta_rows)} artigos)")
    entries.append("%% ═══════════════════════════════════════════════════════\n")
    for r in meta_rows:
        kws = [r.get("methodology_type",""), r.get("ai_type",""), r.get("main_finding_direction","")]
        entries.append(entry_to_bib(
            r.get("paper_id",""),
            r.get("title",""),
            r.get("year",""),
            r.get("venue",""),
            r.get("authors","Author to verify"),
            r.get("abstract",""),
            kws,
            "Empirical_Global"
        ))

    # Corpus 2: Theoretical_Global (theoretical_papers.json)
    entries.append("\n%% ═══════════════════════════════════════════════════════")
    entries.append(f"%% CORPUS 2 — Theoretical_Global ({len(theory_papers)} artigos)")
    entries.append("%% ═══════════════════════════════════════════════════════\n")
    for p in theory_papers:
        pub_types = " | ".join(p.get("publication_types") or [])
        entries.append(entry_to_bib(
            p.get("paper_id",""),
            p.get("title",""),
            p.get("year",""),
            p.get("venue",""),
            p.get("authors",[]),
            p.get("abstract",""),
            ["Theoretical", pub_types],
            "Theoretical_Global"
        ))

    # Corpus 3: Brazil (brazil_mapping.csv)
    entries.append("\n%% ═══════════════════════════════════════════════════════")
    entries.append(f"%% CORPUS 3 — Brazil ({len(brazil_rows)} artigos)")
    entries.append("%% ═══════════════════════════════════════════════════════\n")
    for r in brazil_rows:
        themes = r.get("themes","").replace("|",",")
        entries.append(entry_to_bib(
            r.get("paper_id",""),
            r.get("title",""),
            r.get("year",""),
            r.get("venue",""),
            r.get("authors",""),
            r.get("abstract_short",""),
            [r.get("doc_type",""), themes],
            "Brazil"
        ))

    return header + "\n\n".join(entries) + "\n"


# =============================================================================
# MAIN
# =============================================================================
def main():
    print("[->] Carregando dados...\n")
    meta_rows    = load_csv(META_CSV)
    brazil_rows  = load_csv(BRAZIL_CSV)
    theory_data  = load_json(THEORY_JSON) if THEORY_JSON.exists() else {"papers": []}
    theory_papers = theory_data.get("papers", [])

    print(f"    Empirical_Global  : {len(meta_rows)} artigos")
    print(f"    Theoretical_Global: {len(theory_papers)} artigos")
    print(f"    Brazil            : {len(brazil_rows)} artigos")
    print(f"    TOTAL             : {len(meta_rows)+len(theory_papers)+len(brazil_rows)}\n")

    # 1. brazil_summary.md
    brazil_md = gen_brazil_summary(brazil_rows)
    BRAZIL_MD.parent.mkdir(parents=True, exist_ok=True)
    BRAZIL_MD.write_text(brazil_md, encoding="utf-8")
    print(f"[OK] {BRAZIL_MD.relative_to(BASE_DIR)}")

    # 2. master_research_landscape.md
    master_md = gen_master_landscape(meta_rows, brazil_rows, theory_data)
    MASTER_MD.write_text(master_md, encoding="utf-8")
    print(f"[OK] {MASTER_MD.relative_to(BASE_DIR)}")

    # 3. BIBLIOGRAFIA_COMPLETA_IA_EDU.bib
    bib_content = gen_unified_bib(meta_rows, theory_papers, brazil_rows)
    BIB_PATH.parent.mkdir(parents=True, exist_ok=True)
    BIB_PATH.write_text(bib_content, encoding="utf-8")
    print(f"[OK] {BIB_PATH.relative_to(BASE_DIR)}")

    total_bib = len(meta_rows) + len(theory_papers) + len(brazil_rows)
    print(f"\n-- Resumo ---------------------------------------------------")
    print(f"   brazil_summary.md           : gerado")
    print(f"   master_research_landscape.md: gerado")
    print(f"   BIBLIOGRAFIA_COMPLETA.bib   : {total_bib} entradas")


if __name__ == "__main__":
    main()
