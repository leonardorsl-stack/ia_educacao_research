# Resumo dos Novos Dados Empíricos e Metodologia de Extração

Este documento consolida os dados obtidos após a expansão do corpus e descreve a metodologia automatizada de extração e classificação utilizada para a revisão sistemática.

## 1. Resumo Quantitativo
- **Total de Artigos Analisados:** 216
- **Artigos Incluídos na Meta-Análise Empírica (n):** 40 (anteriormente 13)
- **Período de Coleta:** 2020 – 2026
- **Fontes de Dados:** 
    - **Scopus API:** Corpus acadêmico global (via DOI/Identifier).
    - **Google Scholar (Scraping):** Cobertura de preprints e conferências recentes (190 artigos).
    - **Semantic Scholar:** Foco no contexto brasileiro e pesquisa regional (26 novos artigos).

## 2. Direção dos Achados Empíricos
Com base na classificação automatizada dos 40 estudos empíricos:
- **Resultados Mistos / Neutros:** 57,5%
- **Resultados Negativos (ampliação de desigualdade, viés, perda de desempenho):** 37,5%
- **Resultados Positivos:** 5,0%

## 3. Metodologia de Extração e Análise

### A. Coleta Automatizada (Identificação)
- **Strings de Busca Expandidas:** Inclusão de termos metodológicos (`"case study"`, `"experiment"`, `"survey"`, `"qualitative"`, `"quantitative"`) para garantir a captura de estudos empíricos.
- **Pipeline de Consolidação:** Fusão automatizada de datasets de três fontes distintas, com remoção de duplicatas baseada em DOI e similaridade de títulos.

### B. Filtragem Empírica (Triagem)
- **Scoring por Palavras-Chave:** Artigos classificados como "Empíricos" se contivessem ao menos dois acertos em grupos semânticos distintos:
    - **Impacto:** `impact`, `evidence`, `trial`, `performance`.
    - **Desigualdade:** `access gap`, `disparity`, `marginalized`, `Global South`.
    - **Ética:** `bias`, `fairness`, `transparency`, `discrimination`.
    - **Metodologia:** `methodology`, `case study`, `survey`, `mixed methods`.

### C. Modelagem Temática (Análise)
- **LDA (Latent Dirichlet Allocation):** Aplicado aos resumos dos 40 estudos empíricos para identificar 5 clusters principais:
    1. Equidade & Acesso (Foco no Sul Global)
    2. IA Generativa & Desempenho Acadêmico
    3. Ética, Viés & Preocupações com Privacidade
    4. Carga Docente & Práticas Pedagógicas
    5. Tutores Inteligentes & Engajamento

### D. Avaliação de Qualidade (Appraisal)
- **Quality Score Simplificado (0-5):** Atribuição de nota heurística baseada na presença de:
    - **Amostra Definida** (ex: "n=45")
    - **Design Robusto** (ex: "control group", "RCT")
    - **Rigor Estatístico** (ex: "p < 0.05")
    - **Transparência Metodológica** (menção explícita a "methodology")
    - **Densidade do Resumo** (detalhamento textual)

## 4. Relevância para o Manuscrito
A transição de **n=13** para **n=40** confere maior robustez estatística ao argumento central. Embora a tendência crítica se mantenha (37,5% de achados negativos), a presença majoritária de resultados mistos (57,5%) permite uma análise mais matizada das contradições da IA na educação, respondendo às críticas de viés de seleção e "PRISMA washing".

---
*Gerado em 2026-04-22 | Projeto: Pesquisa IA & Educação*
