# Protocolo PRISMA 2020 — Revisão Sistemática: IA na Educação

> **Versão:** 1.0  
> **Data de Registro:** 2026-04-20  
> **Status:** Pré-Registro (Locked — não alterar após início da coleta)  
> **Autores:** A preencher  
> **Afiliação:** A preencher  

---

## 1. Título e Objetivo

**Título provisório:**  
*Inteligência Artificial na Educação: Uma Revisão Sistemática sobre Impactos Pedagógicos, Éticos e Sociais (2020–2026)*

**Pergunta de Pesquisa (PICO adaptado):**  
> Em contextos educacionais formais e informais, **quais são os impactos mensuráveis** do uso de sistemas de Inteligência Artificial **no desempenho acadêmico, equidade de acesso e práticas pedagógicas**, conforme evidenciado pela literatura empírica revisada por pares entre 2020 e 2026?

**Objetivos específicos:**
1. Mapear as tipologias de aplicação de IA descritas na literatura (tutores inteligentes, LLMs, sistemas de recomendação, avaliação automatizada).
2. Identificar impactos pedagógicos positivos, negativos e neutros reportados.
3. Analisar lacunas éticas e metodológicas na produção científica vigente.
4. Identificar tendências geográficas e institucionais na produção acadêmica.

---

## 2. Fontes de Dados

| Base de Dados      | URL                                 | Acesso via      |
|--------------------|-------------------------------------|-----------------|
| Semantic Scholar   | https://api.semanticscholar.org     | API REST (JSON) |
| Google Scholar     | https://scholar.google.com          | `scholarly`     |
| ERIC               | https://api.ies.ed.gov/eric/        | API REST (JSON) |
| Scopus             | https://api.elsevier.com            | API (chave)     |

---

## 3. Strings de Busca

### String Principal (EN)

```
("Artificial Intelligence" OR "Machine Learning" OR "Deep Learning" OR "Generative AI" OR "Large Language Model")
AND
("Education" OR "Learning" OR "Teaching" OR "Pedagogy" OR "Classroom" OR "Higher Education" OR "K-12")
AND
("Social Impact" OR "Learning Outcomes" OR "Student Performance" OR "Equity" OR "Ethics" OR "Bias")
```

### String Secundária (PT-BR)

```
("Inteligência Artificial" OR "Aprendizado de Máquina" OR "IA Generativa")
AND
("Educação" OR "Ensino" OR "Aprendizagem" OR "Pedagogia")
AND
("Impacto Social" OR "Desempenho Acadêmico" OR "Equidade" OR "Ética")
```

### Filtros Aplicados

- **Período:** 2020–2026
- **Idiomas:** inglês, português, espanhol
- **Tipo de publicação:** artigos revisados por pares, conferências indexadas
- **Formato:** texto completo disponível OU abstract disponível

---

## 4. Critérios de Elegibilidade

### 4.1 Critérios de Inclusão (PICO)

| Dimensão    | Critério                                                                 |
|-------------|--------------------------------------------------------------------------|
| **P** (População)  | Estudantes, professores, instituições de ensino formal ou informal |
| **I** (Intervenção) | Sistema ou ferramenta baseado em IA aplicado ao contexto educacional |
| **C** (Comparador) | Contexto sem IA, método tradicional, ou grupo controle definido      |
| **O** (Outcome)    | Desempenho, engajamento, equidade, percepção, impacto ético          |

### 4.2 Critérios de Exclusão

- [ ] Artigos sem abstract disponível
- [ ] Literatura cinzenta não indexada (exceto preprints com revisão aberta)
- [ ] Artigos de opinião/editorial sem dados empíricos
- [ ] Artigos sobre IA na educação médica ou militar (fora do escopo)
- [ ] Duplicatas identificadas por DOI ou similaridade de título (≥ 90%)
- [ ] Publicações anteriores a janeiro de 2020

---

## 5. Fluxo de Triagem PRISMA

```
┌─────────────────────────────────────────────────────┐
│              IDENTIFICAÇÃO (Identification)          │
│  Registros identificados nas bases: N = ?           │
│  Registros removidos antes da triagem: N = ?        │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                 TRIAGEM (Screening)                  │
│  Registros triados: N = ?                           │
│  Registros excluídos (título/abstract): N = ?       │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              ELEGIBILIDADE (Eligibility)             │
│  Artigos avaliados em texto completo: N = ?         │
│  Artigos excluídos (texto completo): N = ?          │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                INCLUSÃO (Included)                   │
│  Estudos incluídos na síntese: N = ?                │
└─────────────────────────────────────────────────────┘
```

> **Nota:** Preencher os valores N após cada etapa da triagem automatizada (ver `scripts/data_collection.py`).

---

## 6. Extração de Dados

Para cada artigo incluído, extrair as seguintes variáveis:

| Campo              | Tipo         | Descrição                                        |
|--------------------|--------------|--------------------------------------------------|
| `paper_id`         | string       | ID único (DOI ou ID da base)                    |
| `title`            | string       | Título do artigo                                |
| `authors`          | lista        | Lista de autores                                |
| `year`             | inteiro      | Ano de publicação                               |
| `venue`            | string       | Periódico ou conferência                        |
| `abstract`         | texto        | Resumo completo                                 |
| `citation_count`   | inteiro      | Número de citações                              |
| `ai_type`          | categórico   | Tipo de IA (ML, DL, LLM, SIR, etc.)           |
| `education_level`  | categórico   | Nível educacional (Básico, Médio, Superior, EAD)|
| `outcome_reported` | booleano     | Reporta outcome mensurável?                    |
| `ethics_flag`      | booleano     | Discute questões éticas?                       |
| `country`          | string       | País do estudo                                  |

---

## 7. Avaliação de Qualidade

Todos os artigos incluídos serão avaliados usando a escala **Mixed Methods Appraisal Tool (MMAT)** adaptada:

- [ ] A questão de pesquisa é claramente formulada?
- [ ] O design metodológico é adequado à questão?
- [ ] O método de coleta de dados é descrito?
- [ ] Os resultados são apresentados com rigor estatístico?
- [ ] As limitações são discutidas?

**Escala:** 0–5 pontos. Artigos com pontuação < 3 serão marcados como `low_quality` e incluídos apenas na análise de sensibilidade.

---

## 8. Síntese dos Dados

| Método de Síntese            | Aplicação                                  |
|------------------------------|--------------------------------------------|
| Meta-síntese narrativa       | Para estudos qualitativos                  |
| Análise de agrupamento (NLP) | Clustering semântico de abstracts          |
| Análise bibliométrica        | Redes de co-citação, tendências temporais  |
| Mapa de evidências           | Visualização por nível educacional e tipo IA |

---

## 9. Desvios do Protocolo

> *Registrar aqui quaisquer desvios ocorridos após o início da coleta:*

| Data | Desvio | Justificativa |
|------|--------|---------------|
| —    | —      | —             |

---

## 10. Referências Metodológicas

- PAGE, M. J. et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. **BMJ**, v. 372, n. 71, 2021. DOI: 10.1136/bmj.n71
- MOHER, D. et al. Preferred reporting items for systematic reviews and meta-analyses: The PRISMA statement. **PLOS Medicine**, v. 6, n. 7, 2009.
- ZAWACKI-RICHTER, O. et al. Systematic review of research on artificial intelligence applications in higher education. **International Journal of Educational Technology in Higher Education**, v. 16, n. 39, 2019.
