# IA na Educação — Pesquisa de Revisão Sistemática

> **Título do artigo:** *Inteligência Artificial na Educação: Datificação, Desigualdade e a Urgência de Soberania Pedagógica*  
> **Metodologia:** Revisão sistemática (PRISMA 2020) + Ciências Sociais Computacionais  
> **Corpus:** 73 artigos — 13 empíricos globais · 30 teóricos · 30 brasileiros (2020–2026)

---

## Achado Central

De 13 estudos empíricos internacionais analisados, **53,8% apresentaram achados negativos** — a introdução de IA no ambiente educacional amplificou desigualdades pré-existentes. Apenas 7,7% reportaram melhoria inequívoca.

---

## Estrutura do Repositório

```
ia_educacao_research/
│
├── data/
│   ├── raw/                    # Dados brutos coletados via API
│   │   ├── brazil_research.json        # 30 artigos brasileiros
│   │   ├── theoretical_papers.json     # 30 artigos teóricos
│   │   └── search_results.json         # Resultados brutos das buscas
│   ├── processed/              # Dados processados / codificados
│   │   ├── meta_analysis_matrix.csv    # Matriz de meta-análise (13 empíricos)
│   │   ├── brazil_mapping.csv          # Mapeamento temático brasileiro
│   │   └── empirical_papers.csv        # Corpus empírico processado
│   └── metadata/
│       └── search_metadata.json        # Metadados das buscas
│
├── docs/                       # Documentos analíticos
│   ├── analysis_summary.md             # Resumo quantitativo global
│   ├── brazil_analysis.md              # Análise crítica do corpus brasileiro
│   ├── brazil_summary.md               # Panorama temático brasileiro
│   ├── brazil_research_map.md          # Mapa da pesquisa nacional
│   ├── master_landscape.md             # Roteiro comparativo dos 3 eixos + 5 teses
│   ├── theoretical_synthesis.md        # Síntese dos 3 conceitos-chave
│   ├── research_log.md                 # Diário de pesquisa
│   └── protocol/
│       └── prisma_protocol.md          # Protocolo PRISMA pré-registrado
│
├── references/
│   └── BIBLIOGRAFIA_MESTRE_IA_EDU.bib  # BibTeX unificado (73 entradas)
│                                        # Tags: Global_Empirical | Global_Theoretical | Brazil_Context
│
├── results/
│   ├── figures/                # Visualizações geradas
│   └── tables/
│       ├── evidence_table.md           # Tabela de evidências
│       └── evidence_table.tex          # Versão LaTeX
│
├── scripts/                    # Pipeline de coleta e análise
│   ├── data_collection.py              # Coleta via API Semantic Scholar
│   ├── data_enrichment.py              # Enriquecimento de metadados
│   ├── empirical_analysis.py           # Análise do corpus empírico
│   ├── nlp_pipeline.py                 # Processamento de linguagem natural
│   ├── process_brazil.py               # Processamento do corpus brasileiro
│   ├── search_brazil_papers.py         # Busca de artigos brasileiros
│   ├── search_theoretical_papers.py    # Busca de artigos teóricos
│   ├── generate_summary.py             # Geração de resumo analítico
│   ├── generate_tables.py              # Geração de tabelas de evidências
│   ├── generate_master_docs.py         # Geração de documentos master
│   ├── generate_synthesis_docs.py      # Geração de sínteses acadêmicas
│   ├── export_to_zotero.py             # Exportação BibTeX unificada
│   ├── upload_to_zotero.py             # Upload para biblioteca Zotero
│   ├── upload_brazil_to_zotero.py      # Upload corpus BR para Zotero
│   └── scraper.py                      # Web scraper auxiliar
│
├── notebooks/                  # Análises exploratórias
│   ├── 01_coleta_dados.ipynb
│   ├── 02_analise_textual.ipynb
│   └── 03_visualizacao_resultados.ipynb
│
├── requirements.txt            # Dependências Python
└── .gitignore
```

---

## Os Três Eixos Analíticos

| Eixo | Base | Argumento Central |
|---|---|---|
| ⚡ **Crise da Promessa** | 13 empíricos globais | 53,8% negativos — IA amplifica desigualdades |
| 📚 **Ameaça da Datificação** | 30 teóricos | Zuboff + Selwyn: IA não é neutra, é política |
| 🇧🇷 **Contexto Situado** | 30 brasileiros | Brasil como *stress-test* global da exclusão digital |

---

## Metodologia

- **Coleta:** API pública do [Semantic Scholar](https://api.semanticscholar.org) com controle de *rate limit*
- **Triagem:** Protocolo PRISMA 2020 adaptado para revisões computacionalmente assistidas
- **Análise NLP:** Análise de frequência léxica (*keyword matching*) + co-ocorrência temática
- **Gestão bibliográfica:** BibTeX com tags por corpus (`Global_Empirical`, `Global_Theoretical`, `Brazil_Context`)

---

## Instalação

```bash
git clone https://github.com/leonardorsl/ia_educacao_research.git
cd ia_educacao_research
pip install -r requirements.txt
```

---

## Reproduzir a Análise

```bash
# 1. Gerar resumo analítico global
python scripts/generate_summary.py

# 2. Gerar documentos de síntese (Brazil + Teórico + Master Landscape)
python scripts/generate_synthesis_docs.py

# 3. Exportar BibTeX unificado
python scripts/export_to_zotero.py
```

---

## Principais Achados

| Indicador | Valor |
|---|---|
| Achados negativos (empírico global) | **53,8%** |
| Achados mistos | 38,5% |
| Estudos sem nível educacional declarado | **69,2%** |
| Artigos brasileiros sobre escola pública/desigualdade | **63,3%** |
| Artigos brasileiros sobre formação docente | 50,0% |
| Total de referências BibTeX | **73** |

---

## Licença

Este projeto é distribuído sob licença **MIT** para fins de pesquisa acadêmica.  
Os dados coletados via API do Semantic Scholar estão sujeitos aos [termos de uso da plataforma](https://www.semanticscholar.org/product/api).

---

*Projeto em desenvolvimento ativo — Versão 1.0*
