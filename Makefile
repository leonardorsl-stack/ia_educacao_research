# Makefile para o Projeto de Pesquisa IA na Educação
# Automatiza as principais etapas do pipeline de análise de dados.

# ==============================================================================
# Variáveis e Configurações
# ==============================================================================

# Define o interpretador Python a ser usado. Busca por um ambiente virtual.
PYTHON = $(shell test -d .venv && echo ".venv/bin/python" || echo "python")
# Define o gerenciador de pacotes
PIP = $(shell test -d .venv && echo ".venv/bin/pip" || echo "pip")

# Define o diretório dos scripts
SCRIPT_DIR = scripts

# ==============================================================================
# Metas Principais (Targets)
# ==============================================================================

# Meta padrão: exibe a ajuda
.DEFAULT_GOAL := help

# Instala as dependências do projeto
install:
	@echo "--- 📦 Instalando dependências do requirements.txt..."
	$(PIP) install -r requirements.txt
	@echo "--- ✅ Dependências instaladas com sucesso."

# Roda o pipeline completo de análise de dados
run_pipeline:
	@echo "--- 🚀 Iniciando o pipeline de análise completo..."
	$(PYTHON) $(SCRIPT_DIR)/generate_summary.py
	$(PYTHON) $(SCRIPT_DIR)/generate_synthesis_docs.py
	$(PYTHON) $(SCRIPT_DIR)/generate_tables.py
	$(PYTHON) $(SCRIPT_DIR)/export_to_zotero.py
	@echo "--- ✅ Pipeline concluído. Verifique os resultados nos diretórios 'docs/' e 'results/'."

# Roda a coleta de dados (se aplicável, para futuras execuções)
collect_data:
	@echo "--- 🌐 Coletando dados (artigos teóricos e brasileiros)..."
	$(PYTHON) $(SCRIPT_DIR)/search_theoretical_papers.py
	$(PYTHON) $(SCRIPT_DIR)/search_brazil_papers.py
	@echo "--- ✅ Coleta de dados finalizada. Arquivos salvos em 'data/raw/'."

# Limpa o projeto, removendo arquivos de cache e gerados
clean:
	@echo "--- 🧹 Limpando o projeto..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f .coverage
	@echo "--- ✅ Projeto limpo."

# ==============================================================================
# Ajuda
# ==============================================================================

.PHONY: help install run_pipeline collect_data clean

help:
	@echo "=============================================================="
	@echo "Makefile do Projeto de Pesquisa: IA na Educação"
	@echo "=============================================================="
	@echo "Comandos disponíveis:"
	@echo "  make install         - Instala as dependências Python do projeto."
	@echo "  make run_pipeline    - Roda a sequência principal de scripts de análise e geração de documentos."
	@echo "  make collect_data    - Executa os scripts de busca e coleta de novos dados."
	@echo "  make clean           - Remove arquivos de cache e temporários do Python."
	@echo "=============================================================="

