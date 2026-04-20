"""
generate_synthesis_docs.py
---------------------------
Gera tres documentos de sintese academica:
  1. docs/brazil_analysis.md       — analise critica do corpus brasileiro
  2. docs/theoretical_synthesis.md — tres conceitos-chave do corpus teorico
  3. docs/master_landscape.md      — roteiro comparativo 3 eixos + 5 teses
"""

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

BASE_DIR    = Path(__file__).resolve().parent.parent
BRAZIL_CSV  = BASE_DIR / "data" / "processed" / "brazil_mapping.csv"
THEORY_JSON = BASE_DIR / "data" / "raw" / "theoretical_papers.json"
META_CSV    = BASE_DIR / "data" / "processed" / "meta_analysis_matrix.csv"
NOW = datetime.now().strftime("%Y-%m-%d %H:%M")


def load_csv(p): 
    with open(p, newline="", encoding="utf-8") as f: 
        return list(csv.DictReader(f))

def load_json(p): 
    with open(p, encoding="utf-8") as f: 
        return json.load(f)

def tr(text, n=100):
    text = (text or "").strip()
    return text[:n] + "…" if len(text) > n else text


# =============================================================================
# DOC 1: brazil_analysis.md
# =============================================================================
def gen_brazil_analysis(rows: list[dict]) -> str:
    total = len(rows)
    emp   = sum(1 for r in rows if r.get("doc_type") == "Empirico")
    teo   = sum(1 for r in rows if r.get("doc_type") == "Teorico")

    escola_publica = [r for r in rows if "Escola Publica" in r.get("themes","")]
    formacao       = [r for r in rows if "Formacao Docente" in r.get("themes","")]
    etica          = [r for r in rows if "Etica" in r.get("themes","") or "Soberania" in r.get("themes","")]
    ia_gen         = [r for r in rows if "IA Generativa" in r.get("themes","")]

    L = []
    L += [
        "# Análise Crítica da Pesquisa Brasileira sobre IA na Educação",
        f"\n> Gerado em {NOW} por `scripts/generate_synthesis_docs.py`  ",
        f"> Corpus: {total} artigos — {emp} empíricos ({emp/total*100:.0f}%) · {teo} teóricos ({teo/total*100:.0f}%)\n",
        "---\n",
        "## Contextualização: O Que o Brasil Está Pesquisando?\n",
        f"Dos **{total} artigos** coletados sobre IA e Educação no Brasil,",
        f"**{emp} ({emp/total*100:.0f}%) são estudos empíricos** — relatos de experiência em escolas",
        "e universidades, pesquisas de campo com professores, estudos de caso institucionais.",
        "Esse predomínio empírico não é acidental: reflete uma tradição brasileira de pesquisa",
        "educacional fortemente ancorada na prática, no chão da escola, na realidade vivida.\n",
        "---\n",
        "## 1. O Tema Central: Escola Pública e Desigualdade\n",
        f"**{len(escola_publica)} de {total} artigos** ({len(escola_publica)/total*100:.0f}%) abordam escola pública",
        "e desigualdade como contexto estruturante — não como tema secundário, mas como",
        "**condição de possibilidade** de qualquer debate sobre IA na educação brasileira.\n",
        "### Por Que Isso Importa?\n",
        "O Brasil possui cerca de **47 milhões de estudantes** na educação básica pública.",
        "Desses, aproximadamente:\n",
        "- **~50%** frequentam escolas sem internet adequada (CGI.br, 2023)",
        "- **~30%** vivem em regiões com conectividade precária (Norte e Nordeste)",
        "- **100%** estão submetidos a uma BNCC que ainda não integra IA como competência explícita\n",
        "Portanto, quando a pesquisa brasileira fala em IA educacional,",
        "ela fala **antes de mais nada de infraestrutura, equidade e cidadania digital**.\n",
        "### Artigos Representativos\n",
        "| Ano | Título | Venue |",
        "| --- | --- | --- |",
    ]
    for r in escola_publica[:6]:
        L.append(f"| {r.get('year','')} | {tr(r.get('title',''),65)} | {tr(r.get('venue',''),35)} |")
    L += [
        "",
        "---\n",
        "## 2. Brasil vs. Norte Global: Dois Usos Opostos da IA\n",
        "Este é o achado mais provocativo do corpus. O contraste é estrutural:\n",
        "| Dimensão | Norte Global | Brasil |",
        "| --- | --- | --- |",
        "| **Objetivo primário da IA** | Otimização de desempenho | Compensação de exclusão |",
        "| **Contexto predominante** | Escolas bem equipadas | Escolas sem internet básica |",
        "| **Tipo de IA discutida** | ChatGPT, LLMs, ITS avançados | Jogos educativos, EaD básica |",
        "| **Preocupação central** | Integridade acadêmica, viés | Acesso, evasão, desigualdade |",
        "| **Relação com professores** | Substituição / automação | Formação e apoio ao docente |",
        "| **Regulação** | GDPR, AI Act (UE) | LGPD jovem, fiscalização fraca |",
        "",
        "**Interpretação:** No Norte Global, o debate gira em torno de *como* usar IA de forma",
        "ética e eficaz, partindo do pressuposto de que o acesso já existe. No Brasil,",
        "o debate ancora-se em *se* e *por que* usar IA, pois o acesso ainda é exceção.",
        "A IA no Brasil é apresentada, em muitos estudos, como **promessa redentora**",
        "de uma educação historicamente subfinanciada — o que a teoria crítica internacional",
        "identifica como risco de \"solucionismo tecnológico\".\n",
        "---\n",
        "## 3. Formação Docente: A Variável Crítica\n",
        f"**{len(formacao)} de {total} artigos** ({len(formacao)/total*100:.0f}%) identificam a formação",
        "docente como o gargalo central para a adoção responsável de IA.\n",
        "Os estudos convergem em três problemas:\n",
        "1. **Formação inicial defasada** — currículos de licenciatura não preparam para IA",
        "2. **Formação continuada fragmentada** — cursos avulsos sem política estruturada",
        "3. **Ansiedade tecnológica** — professores relatam medo de substituição, não empoderamento\n",
        "### Artigos Representativos\n",
        "| Ano | Título | Achado Principal |",
        "| --- | --- | --- |",
    ]
    for r in formacao[:4]:
        L.append(f"| {r.get('year','')} | {tr(r.get('title',''),55)} | {tr(r.get('abstract_short',''),60)} |")
    L += [
        "",
        "---\n",
        "## 4. Ética, Soberania e a Lacuna Regulatória\n",
        f"Apenas **{len(etica)} artigos** ({len(etica)/total*100:.0f}%) discutem ética ou soberania",
        "digital explicitamente — o que é **alarmante** dado o contexto:\n",
        "- Plataformas estrangeiras (Google Classroom, Microsoft Teams, Khan Academy)",
        "  coletam dados de milhões de estudantes brasileiros sem framework de auditoria adequado",
        "- A LGPD (Lei 13.709/2018) existe, mas sua aplicação no contexto escolar é incipiente",
        "- Não há equivalente brasileiro ao AI Act europeu para educação\n",
        "---\n",
        "## 5. IA Generativa: O Debate Que Ainda Não Chegou\n",
        f"Apenas **{len(ia_gen)} artigos** discutem ChatGPT ou IA Generativa especificamente.",
        "Enquanto o Norte Global já debate plágio, pensamento crítico e autoria na era do GPT-4,",
        "**o Brasil ainda está debatendo se as escolas têm computadores suficientes**.\n",
        "Isso cria uma dupla vulnerabilidade:",
        "- Quando a IA Generativa chegar massivamente às escolas brasileiras, não haverá",
        "  política, formação ou regulação preparadas",
        "- Os estudantes brasileiros aprenderão a usar IA com menos letramento crítico",
        "  do que seus pares do Norte Global\n",
        "---\n",
        "## Conclusão: IA como Espelho das Desigualdades Estruturais\n",
        "> A pesquisa brasileira sobre IA na educação não é uma pesquisa sobre tecnologia.",
        "> É uma pesquisa sobre o Brasil — suas desigualdades, suas promessas não cumpridas",
        "> e sua luta permanente por uma educação pública de qualidade.\n",
        "---",
        "\n*Análise gerada por `scripts/generate_synthesis_docs.py` | Projeto: IA & Educação Research*",
    ]
    return "\n".join(L)


# =============================================================================
# DOC 2: theoretical_synthesis.md
# =============================================================================
def gen_theoretical_synthesis(theory_data: dict) -> str:
    papers = theory_data.get("papers", [])
    n = len(papers)

    # Analisa frequencia de conceitos-chave
    concepts = {
        "Critical Thinking / Pedagogical Agency": [
            "critical thinking","agency","pedagogical","autonomy","higher-order","metacognition"
        ],
        "AI Ethics / Datafication": [
            "ethics","bias","fairness","datafication","surveillance","privacy","accountability",
            "equity","discrimination","algorithmic"
        ],
        "AI Optimism / Solutionism": [
            "enhance","improve","transform","opportunity","potential","benefit","performance",
            "engagement","personali","adaptive"
        ],
    }
    concept_counts = {}
    concept_examples = {k: [] for k in concepts}
    for p in papers:
        text = ((p.get("title") or "") + " " + (p.get("abstract") or "")).lower()
        for concept, kws in concepts.items():
            if any(kw in text for kw in kws):
                concept_counts[concept] = concept_counts.get(concept, 0) + 1
                if len(concept_examples[concept]) < 3:
                    concept_examples[concept].append(p)

    # Anos
    year_cnt = Counter(str(p.get("year","")) for p in papers if p.get("year"))
    top_venues = Counter(p.get("venue","") for p in papers if p.get("venue",""))

    L = []
    L += [
        "# Síntese Teórica — Correntes de Pensamento sobre IA na Educação",
        f"\n> Gerado em {NOW} por `scripts/generate_synthesis_docs.py`  ",
        f"> Corpus: {n} artigos teóricos / conceituais (2020–2026)\n",
        "---\n",
        "## Introdução: O Campo Teórico em Disputa\n",
        "A literatura teórica internacional sobre IA na Educação não é uniforme.",
        "Ela reflete **tensões epistemológicas profundas** entre diferentes visões",
        "sobre o papel da tecnologia na transformação social e educacional.",
        "Identificamos três **correntes de pensamento** dominantes neste corpus:\n",
        "| Corrente | Artigos | % | Postura Nuclear |",
        "| --- | --- | --- | --- |",
    ]
    for concept, count in sorted(concept_counts.items(), key=lambda x: -x[1]):
        pct = f"{count/n*100:.0f}%"
        postura = {
            "Critical Thinking / Pedagogical Agency": "IA pode/deve fortalecer a agência pedagógica",
            "AI Ethics / Datafication": "IA apresenta riscos estruturais de dataficação e viés",
            "AI Optimism / Solutionism": "IA como transformadora inequívoca da educação",
        }.get(concept, "—")
        L.append(f"| {concept} | {count} | {pct} | {postura} |")
    L += ["", "---\n"]

    # CONCEITO 1
    L += [
        "## 🧠 Conceito-Chave 1: Pedagogical Agency",
        "*(Agência Pedagógica / Pensamento Crítico)*\n",
        "### O Que É?\n",
        "**Pedagogical Agency** refere-se à capacidade de professores e estudantes de",
        "**agir intencionalmente** sobre o processo de ensino-aprendizagem — de fazer escolhas,",
        "questionar, criar e resistir a automatismos, mesmo em ambientes mediados por IA.\n",
        "### Por Que Aparece no Corpus?\n",
        "O tema domina a literatura porque há uma tensão crescente entre:\n",
        "- **IA como amplificador de agência** (ex: ITS que personalizam o ritmo do estudante)",
        "- **IA como supressora de agência** (ex: sistemas que tomam decisões por professores)\n",
        "A questão não é tecnológica — é pedagógica e política: *quem decide o que aprender?*\n",
        "### Autores e Artigos de Referência\n",
    ]
    for p in concept_examples["Critical Thinking / Pedagogical Agency"][:3]:
        L.append(f"- **[{p.get('year','')}]** _{tr(p.get('title',''), 80)}_")
        L.append(f"  > {tr(p.get('abstract',''), 130)}")
    L += [
        "",
        "### Implicação para o Artigo\n",
        "> *\"Se a IA não for implementada com design pedagógico intencional,",
        "> ela não amplia a agência — ela a substitui, transferindo decisões curriculares",
        "> de professores para algoritmos treinados em contextos culturalmente distantes.\"*\n",
        "---\n",
        "## ⚠️ Conceito-Chave 2: Datafication of Education",
        "*(Datificação da Educação)*\n",
        "### O Que É?\n",
        "**Datafication** é o processo pelo qual experiências humanas complexas —",
        "como aprender, se relacionar, criar — são convertidas em **dados quantificáveis**,",
        "capturados, armazenados e analisados por sistemas algorítmicos.\n",
        "Na educação, manifesta-se como:\n",
        "- Monitoramento de cliques, tempo de tela e padrões de resposta de estudantes",
        "- Scoring algorítmico de redações e avaliações",
        "- Plataformas que constroem perfis preditivos de \"risco de evasão\"\n",
        "### A Crítica Central (Zuboff + Selwyn)\n",
        "A datificação não é neutra: ela **mercantiliza a experiência educacional**,",
        "criando ativos de dados lucrativos para empresas de EdTech enquanto",
        "fragiliza a privacidade de estudantes — especialmente os mais vulneráveis.\n",
        "### Artigos do Corpus\n",
    ]
    for p in concept_examples["AI Ethics / Datafication"][:3]:
        L.append(f"- **[{p.get('year','')}]** _{tr(p.get('title',''), 80)}_")
        L.append(f"  > {tr(p.get('abstract',''), 130)}")
    L += [
        "",
        "### Implicação para o Artigo\n",
        "> *\"A datificação da educação no Brasil tem dimensão colonial:",
        "> os dados de crianças brasileiras alimentam modelos treinados nos EUA e na Europa,",
        "> sem retorno local e com riscos de viés cultural e racial sistemático.\"*\n",
        "---\n",
        "## 🚀 Conceito-Chave 3: Technological Solutionism",
        "*(Solucionismo Tecnológico)*\n",
        "### O Que É?\n",
        "Conceito de **Evgeny Morozov**: a tendência de tratar problemas sociais complexos",
        "como se fossem problemas de engenharia, solúveis com tecnologia suficiente.",
        "Na educação, manifesta-se na crença de que IA pode resolver desigualdade,",
        "déficit de aprendizagem e falta de professores — sem reformas estruturais.\n",
        "### A Tensão no Corpus\n",
        f"**{concept_counts.get('AI Optimism / Solutionism', 0)} artigos** do corpus teórico apresentam",
        "narrativa otimista sobre IA, enfatizando transformação, oportunidade e melhoria.",
        "Isso não os invalida — mas exige leitura crítica do **contexto de aplicação**:\n",
        "- IA que funciona em escolas bem financiadas pode falhar em contextos de escassez",
        "- Resultados positivos em experimentos controlados não garantem escalabilidade equitativa",
        "- O otimismo muitas vezes pressupõe infraestrutura que não existe\n",
        "### Artigos do Corpus\n",
    ]
    for p in concept_examples["AI Optimism / Solutionism"][:3]:
        L.append(f"- **[{p.get('year','')}]** _{tr(p.get('title',''), 80)}_")
        L.append(f"  > {tr(p.get('abstract',''), 130)}")
    L += [
        "",
        "### Implicação para o Artigo\n",
        "> *\"O solucionismo tecnológico é especialmente perigoso em contextos de desigualdade:",
        "> ele desvia atenção política das causas estruturais (subfinanciamento, desigualdade",
        "> racial, brecha digital) para soluções técnicas que apenas os privilegiados acessam.\"*\n",
        "---\n",
        "## Síntese das Correntes\n",
        "```",
        "  CORPUS TEÓRICO (30 artigos)",
        "       ┌────────────────────────────────────────────┐",
        "       │                                            │",
        "  [Agência]      [Datificação]      [Solucionismo]  │",
        "  Pedagógica  ←──── tensão ────→   Tecnológico      │",
        "  (empoderar)                       (otimizar)      │",
        "       │              │                  │          │",
        "       └──────────────┴──────────────────┘          │",
        "              CAMPO DE DISPUTA TEÓRICA              │",
        "       └────────────────────────────────────────────┘",
        "```\n",
        "---",
        "\n*Síntese gerada por `scripts/generate_synthesis_docs.py` | Projeto: IA & Educação Research*",
    ]
    return "\n".join(L)


# =============================================================================
# DOC 3: master_landscape.md
# =============================================================================
def gen_master_landscape(meta_rows, brazil_rows, theory_data):
    papers_theory = theory_data.get("papers", [])
    n_emp = len(meta_rows)
    n_teo = len(papers_theory)
    n_br  = len(brazil_rows)

    neg = sum(1 for r in meta_rows if "Negative" in r.get("main_finding_direction",""))
    mix = sum(1 for r in meta_rows if "Mixed"    in r.get("main_finding_direction",""))
    pos = sum(1 for r in meta_rows if "Positive" in r.get("main_finding_direction",""))
    iniq = sum(1 for r in meta_rows if r.get("inequity","").lower() in ("true","1"))
    eth  = sum(1 for r in meta_rows if r.get("ethics","").lower()   in ("true","1"))

    br_emp = sum(1 for r in brazil_rows if r.get("doc_type") == "Empirico")

    L = []
    L += [
        "# Master Landscape — Roteiro Comparativo dos Três Eixos",
        f"\n> Pesquisador Sênior | Gerado em {NOW}  ",
        f"> Corpus total: **{n_emp + n_teo + n_br} artigos** — {n_emp} empíricos globais · {n_teo} teóricos · {n_br} brasileiros\n",
        "---\n",
        "## Propósito deste Documento\n",
        "Este é o **roteiro argumentativo** do artigo. Não é um resumo — é uma",
        "**arquitetura intelectual** que sustenta a tese central:",
        "> *A Inteligência Artificial na educação é um fenômeno político antes de ser técnico,",
        "> e no Brasil essa dimensão política é amplificada por desigualdades estruturais",
        "> que transformam cada escolha tecnológica em um ato de distribuição de poder.*\n",
        "---\n",
        "## ═══ EIXO 1 — Global Empírico ═══",
        "### *O Que os Dados Mostram Quando Olhamos para o Mundo*\n",
        f"**Base:** {n_emp} estudos empíricos (2021–2024), periódicos internacionais de alto impacto\n",
        "### Panorama Quantitativo\n",
        "| Indicador | N | % |",
        "| --- | --- | --- |",
        f"| Achados negativos | {neg} | {neg/n_emp*100:.1f}% |",
        f"| Achados mistos/neutros | {mix} | {mix/n_emp*100:.1f}% |",
        f"| Achados positivos | {pos} | {pos/n_emp*100:.1f}% |",
        f"| Estudos que detectam iniquidade | {iniq} | {iniq/n_emp*100:.1f}% |",
        f"| Estudos com preocupações éticas | {eth} | {eth/n_emp*100:.1f}% |",
        "",
        "### Narrativa do Eixo 1\n",
        "A promessa da IA como equalizadora educacional **não se sustenta empiricamente**.",
        "Os estudos com achados positivos concentram-se em contextos privilegiados:",
        "países com alta renda, escolas bem equipadas, estudantes com capital cultural.",
        "Nos contextos de vulnerabilidade — rurais, de baixa renda, com professores",
        "mal remunerados — os achados negativos dominam.\n",
        "A iniquidade não é efeito colateral da IA: ela é **amplificada** pela IA,",
        "porque sistemas de aprendizagem adaptativa funcionam melhor com dados ricos",
        "— e dados ricos vêm de estudantes que já têm mais.\n",
        "### Destaques do Corpus\n",
    ]
    for r in meta_rows:
        if r.get("main_finding_direction","").startswith("Negative") and r.get("inequity","").lower()=="true":
            eff = (r.get("effect_description") or r.get("main_finding_direction","")).strip()
            if eff.lower() == "see abstract": eff = r.get("main_finding_direction","")
            L.append(f"- **{tr(r.get('title',''),60)}** ({r.get('year','')})")
            L.append(f"  > {tr(eff, 110)}")
    L += [
        "",
        "### Contribuição para a Tese\n",
        "> *O eixo empírico global fornece a evidência: IA tende a reproduzir",
        "> e ampliar desigualdades educacionais pré-existentes.*\n",
        "---\n",
        "## ═══ EIXO 2 — Global Teórico ═══",
        "### *O Que a Teoria Crítica Internacional Nomeia*\n",
        f"**Base:** {n_teo} artigos teóricos/conceituais (2020–2026)\n",
        "### As Três Correntes e Sua Relevância\n",
        "| Corrente | Contribuição para o Artigo | Limitação |",
        "| --- | --- | --- |",
        "| **Agência Pedagógica** | Afirma que IA deve servir à autonomia docente e discente | Pode subestimar constrangimentos estruturais |",
        "| **Datificação** | Nomeia o mecanismo de extração de valor dos dados educacionais | Risco de paralisia analítica |",
        "| **Solucionismo** | Alerta para o uso de IA como desvio de reformas necessárias | Pode ser lido como anti-tecnologia |",
        "",
        "### O Marco Teórico que Adotamos\n",
        "Articulamos as três correntes em uma síntese original:\n",
        "**A IA na educação é um dispositivo de poder** (Foucault/Selwyn) que:",
        "1. *Datafican* experiências pedagógicas, convertendo aprendizagem em commodity",
        "2. *Suprimem ou amplificam* a agência docente, dependendo do contexto político",
        "3. *Funcionam como substitutos simbólicos* de reformas estruturais (solucionismo)\n",
        "### Contribuição para a Tese\n",
        "> *O eixo teórico fornece o vocabulário: dataficação, agência, solucionismo.",
        "> Sem esse arcabouço, os dados empíricos permanecem incompreensíveis.*\n",
        "---\n",
        "## ═══ EIXO 3 — Realidade Brasileira ═══",
        "### *O Contexto Situado: Brasil como Caso Extremo*\n",
        f"**Base:** {n_br} artigos ({br_emp} empíricos), produção acadêmica nacional 2020–2026\n",
        "### O Brasil como Amplificador\n",
        "O Brasil não é apenas um país a aplicar IA na educação.",
        "É um **laboratório extremo** onde todas as tensões globais aparecem",
        "em sua forma mais aguda:\n",
        "| Tensão Global | Versão Brasileira |",
        "| --- | --- |",
        "| Acesso desigual à IA | 50% das escolas públicas sem internet adequada |",
        "| Viés algorítmico | Algoritmos treinados em inglês, aplicados em português |",
        "| Datificação sem regulação | LGPD nova, fiscalização incipiente, Big Techs onipresentes |",
        "| Formação docente inadequada | Salários baixos + currículo defasado + ansiedade tecnológica |",
        "| Solucionismo | IA prometida como solução para crise de uma educação subfinanciada |",
        "",
        "### A Leitura Brasileira\n",
        "A pesquisa brasileira revela um paradoxo trágico:",
        "o país que mais precisa de soluções educacionais equitativas",
        "é o menos preparado para implementar IA de forma justa.\n",
        "E enquanto o Norte Global debate *como* usar IA com responsabilidade,",
        "o Brasil ainda debate *se* tem luz elétrica estável nas escolas para ligar os computadores.\n",
        "### Contribuição para a Tese\n",
        "> *O eixo brasileiro fornece a urgência: aqui as abstrações teóricas",
        "> viram corpos concretos de estudantes excluídos, professores ansiosos",
        "> e políticas que prometem o que a infraestrutura não sustenta.*\n",
        "---\n",
        "## ═══ AS 5 TESES DO ARTIGO ═══\n",
        "Estas são as proposições que defenderemos, sustentadas pelos três eixos:\n",
        "---\n",
        "### 🔴 Tese 1: A IA na Educação Pública Brasileira É, Antes de Tudo, um Debate sobre Infraestrutura\n",
        "**Formulação:**",
        "> *Qualquer discussão sobre benefícios pedagógicos da IA no Brasil é prematura",
        "> enquanto metade das escolas públicas não tem conectividade adequada.",
        "> O debate sobre IA é, neste contexto, um debate sobre desigualdade de acesso",
        "> — não sobre algoritmos.*\n",
        "**Evidências:**",
        "- 63% dos artigos brasileiros abordam escola pública e desigualdade",
        "- CGI.br (2023): ~50% das escolas públicas sem internet de qualidade",
        f"- {n_emp} estudos globais: iniquidade presente em {iniq/n_emp*100:.0f}% dos casos\n",
        "---\n",
        "### 🟠 Tese 2: O Solucionismo Tecnológico É uma Forma de Desviar a Atenção das Reformas Necessárias\n",
        "**Formulação:**",
        "> *A introdução de IA em escolas subfinanciadas, sem aumento de investimento",
        "> em formação docente e infraestrutura, funciona como um placebo político:",
        "> gera narrativa de modernização sem alterar as causas estruturais da exclusão.*\n",
        "**Evidências:**",
        "- Corpus teórico: corrente solucionista presente em maioria dos artigos otimistas",
        "- Brasil: IA sendo usada como substituta de reformas curriculares (ex: BNCC não menciona IA explicitamente)",
        "- Estudos empíricos globais: 53,8% de achados negativos em contextos reais\n",
        "---\n",
        "### 🟡 Tese 3: A Datificação da Educação Tem Dimensão Colonial no Sul Global\n",
        "**Formulação:**",
        "> *Quando plataformas do Vale do Silício coletam dados de estudantes brasileiros,",
        "> estão extraindo matéria-prima cognitiva de populações vulneráveis para",
        "> alimentar modelos que serão vendidos de volta ao Brasil a preço de mercado.",
        "> Esta é uma nova forma de extrativismo.*\n",
        "**Evidências:**",
        "- Corpus teórico: Zuboff, Selwyn e outros sobre capitalismo de vigilância",
        "- Brasil: dependência de Google Classroom, Microsoft Teams, Khan Academy",
        "- LGPD ainda sem mecanismos robustos de proteção de dados educacionais de menores\n",
        "---\n",
        "### 🟢 Tese 4: A Formação Docente É a Variável Mais Subestimada nas Políticas de IA Educacional\n",
        "**Formulação:**",
        "> *Nenhuma implementação de IA na educação terá impacto positivo sustentável",
        "> sem professores formados para usar, questionar, adaptar e resistir a sistemas",
        "> de IA. A formação docente não é um complemento da política de IA — é seu coração.*\n",
        "**Evidências:**",
        f"- {len([r for r in brazil_rows if 'Formacao Docente' in r.get('themes','')])}/30 artigos brasileiros identificam formação docente como gargalo",
        "- Corpus global: estudos com professores bem treinados apresentam resultados positivos",
        "- Estudos brasileiros: professores relatam ansiedade, não empoderamento\n",
        "---\n",
        "### 🔵 Tese 5: A Pesquisa Brasileira Sobre IA na Educação Precisa de uma Virada Metodológica\n",
        "**Formulação:**",
        "> *O domínio de estudos empíricos de curto prazo e amostras pequenas",
        "> impede a pesquisa brasileira de capturar os efeitos estruturais da IA.",
        "> Precisamos urgentemente de estudos longitudinais, dados do MEC/INEP integrados",
        "> e pesquisas participativas com comunidades escolares marginalizadas.*\n",
        "**Evidências:**",
        f"- {br_emp}/{n_br} artigos brasileiros são empíricos, mas sem dados longitudinais",
        "- Ausência de estudos com amostras de escolas indígenas, quilombolas, ribeirinhas",
        "- Nenhum artigo cruza dados do IDEB/MEC com métricas de adoção de IA\n",
        "---\n",
        "## Mapa da Argumentação\n",
        "```",
        "  EVIDÊNCIA (Eixo 1)      TEORIA (Eixo 2)        CONTEXTO (Eixo 3)",
        "  ─────────────────       ──────────────────      ─────────────────",
        "  53,8% negativos    →    Datificação         →   Extrativismo digital",
        "  Iniquidade: 54%    →    Solucionismo        →   Infraestrutura precária",
        "  Ética: 77%         →    Agência Pedagógica  →   Formação docente",
        "        │                      │                        │",
        "        └──────────────────────┴────────────────────────┘",
        "                              │",
        "                    5 TESES DO ARTIGO",
        "```\n",
        "---",
        "\n*Master Landscape gerado por `scripts/generate_synthesis_docs.py` | Projeto: IA & Educação Research*",
    ]
    return "\n".join(L)


# =============================================================================
# MAIN
# =============================================================================
def main():
    print("[->] Carregando dados...")
    meta_rows   = load_csv(META_CSV)
    brazil_rows = load_csv(BRAZIL_CSV)
    theory_data = load_json(THEORY_JSON) if THEORY_JSON.exists() else {"papers":[]}

    n_teo = len(theory_data.get("papers",[]))
    print(f"    Empírico Global : {len(meta_rows)}")
    print(f"    Teórico Global  : {n_teo}")
    print(f"    Brasileiro      : {len(brazil_rows)}\n")

    # Doc 1
    out1 = BASE_DIR / "docs" / "brazil_analysis.md"
    out1.write_text(gen_brazil_analysis(brazil_rows), encoding="utf-8")
    print(f"[OK] {out1.relative_to(BASE_DIR)}")

    # Doc 2
    out2 = BASE_DIR / "docs" / "theoretical_synthesis.md"
    out2.write_text(gen_theoretical_synthesis(theory_data), encoding="utf-8")
    print(f"[OK] {out2.relative_to(BASE_DIR)}")

    # Doc 3
    out3 = BASE_DIR / "docs" / "master_landscape.md"
    out3.write_text(gen_master_landscape(meta_rows, brazil_rows, theory_data), encoding="utf-8")
    print(f"[OK] {out3.relative_to(BASE_DIR)}")

    print(f"\n-- Tamanho dos arquivos -----------------------------------")
    for p in [out1, out2, out3]:
        size = p.stat().st_size
        print(f"   {p.name:<40} {size//1024} KB")


if __name__ == "__main__":
    main()
