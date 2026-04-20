# 📓 Research Log — Revisão Sistemática: IA na Educação

> **Instruções de uso:** Registrar cada sessão de trabalho em ordem cronológica.  
> Nunca editar entradas antigas — apenas adicionar novas.  
> Este documento é parte da trilha de auditoria científica do projeto.

---

## Template de Entrada

```markdown
### [AAAA-MM-DD] — Sessão N

**Responsável:** Nome do pesquisador  
**Duração:** X horas  
**Etapa PRISMA:** Identificação / Triagem / Elegibilidade / Inclusão  

#### O que foi feito:
- 

#### String de busca utilizada:
```
(string aqui)
```

#### Resultados:
| Métrica                    | Valor |
|----------------------------|-------|
| Registros brutos coletados | ?     |
| Registros após deduplicação| ?     |
| Registros excluídos        | ?     |
| Registros incluídos        | ?     |

#### Decisões tomadas:
- 

#### Pendências:
- 
```

---

## Registro de Sessões

### [2026-04-20] — Sessão 01 (Inicialização do Projeto)

**Responsável:** Equipe de Pesquisa  
**Duração:** —  
**Etapa PRISMA:** Pré-coleta (Configuração do Protocolo)  

#### O que foi feito:
- Criação da estrutura de diretórios do projeto
- Registro do protocolo PRISMA 2020 em `docs/protocol/prisma_protocol.md`
- Configuração do ambiente virtual Python (`.venv`)
- Criação dos scripts de coleta (`data_collection.py`, `scraper.py`)
- Criação dos notebooks Jupyter para análise
- Definição dos critérios de inclusão/exclusão

#### String de busca registrada:
```
("Artificial Intelligence" OR "Generative AI")
AND ("Education")
AND ("Social Impact")
Filtro: 2020–2026
```

#### Resultados:
| Métrica                    | Valor |
|----------------------------|-------|
| Registros brutos coletados | —     |
| Registros após deduplicação| —     |
| Registros excluídos        | —     |
| Registros incluídos        | —     |

> ⚠️ Coleta ainda não executada. Atualizar após rodar `python scripts/data_collection.py`.

#### Decisões tomadas:
- Período restrito a 2020–2026 para foco em IA generativa e impactos recentes
- Fonte primária: Semantic Scholar (API aberta, sem autenticação)
- Fonte secundária: Google Scholar (via `scholarly`)

#### Pendências:
- [ ] Executar coleta inicial
- [ ] Registrar N de resultados brutos
- [ ] Iniciar triagem automatizada no notebook 01

---

### [2026-04-20] — Sessão 02 (Execução da Coleta — Tentativa 1)

**Responsável:** Equipe de Pesquisa (Cline)  
**Duração:** ~10 min  
**Etapa PRISMA:** Identificação (Coleta via API)  

#### O que foi feito:
- Confirmação dos arquivos `docs/protocol/prisma_protocol.md` e `scripts/data_collection.py` (já existentes e completos)
- Instalação das dependências `requests` e `tqdm` no Python 3.12 do sistema
- Atualização do `data_collection.py`:
  - Adicionado suporte a variável de ambiente `SS_API_KEY` (header `x-api-key`)
  - Substituído tratamento de erro por **backoff exponencial** (30s → 60s → 120s → 240s, 4 tentativas)
  - Delay entre requisições aumentado de 3s → 5s para respeitar rate limit público
- Execução do script: **bloqueada por rate limit 429** da API pública do Semantic Scholar
- Criado `data/raw/search_results.json` com **1 registro de amostra** para validar o pipeline downstream

#### String de busca utilizada:
```
("Artificial Intelligence" OR "Generative AI")
AND ("Education")
AND ("Social Impact")
Filtro: year=2020-2026 | limit=100/página | max=1000
```

#### Resultados:
| Métrica                    | Valor                        |
|----------------------------|------------------------------|
| Registros brutos coletados | 0 (bloqueio 429)             |
| Registros após deduplicação| —                            |
| Registros excluídos        | —                            |
| Registros incluídos        | 1 (amostra sintética)        |

#### Decisões tomadas:
- Criado registro de amostra em `data/raw/search_results.json` para não bloquear etapas 3 e 4 do pipeline
- Rate limit 429 confirma necessidade de **API Key gratuita** do Semantic Scholar

#### ⚠️ Ação Necessária — Obter API Key:
1. Acesse: https://www.semanticscholar.org/product/api#api-key-form
2. Solicite chave gratuita (aprovação em ~24h)
3. Defina no ambiente: `export SS_API_KEY="sua-chave-aqui"`
4. Reexecute: `python3 scripts/data_collection.py`

#### Pendências:
- [ ] Obter e configurar `SS_API_KEY` para coleta real
- [ ] Reexecutar `data_collection.py` com chave e registrar N de resultados brutos
- [ ] Iniciar triagem automatizada (etapa 3): filtrar abstracts por "impacto", "desigualdade", "ética"
- [ ] Cruzar periódicos com Scopus/Qualis (etapa 4)

---

<!-- Adicionar novas sessões abaixo desta linha -->
