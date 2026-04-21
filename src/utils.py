import json
import csv
from pathlib import Path

def load_json(path: Path | str) -> list | dict:
    """Carrega dados de um arquivo JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data: list | dict, path: Path | str) -> None:
    """Salva dados em um arquivo JSON, criando os diretórios se necessário."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_csv(path: Path | str) -> list[dict]:
    """Carrega dados de um arquivo CSV retornando uma lista de dicionários."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
