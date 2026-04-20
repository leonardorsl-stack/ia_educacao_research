"""
upload_to_zotero.py
--------------------
Lê data/processed/meta_analysis_matrix.csv e envia cada artigo como
@journalArticle para a biblioteca pessoal do Zotero via API REST.

Endpoint: https://api.zotero.org/users/{userID}/items
Limite:   50 itens por request (respeitado automaticamente)
"""

import csv
import json
import urllib.request
import urllib.error
from pathlib import Path

# ── Credenciais ────────────────────────────────────────────────────────────────
ZOTERO_USER_ID = "16904895"
ZOTERO_API_KEY = "kNdML8CC5efmAApY3zk33xvQ"
API_BASE       = f"https://api.zotero.org/users/{ZOTERO_USER_ID}/items"

# ── Caminhos ───────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "processed" / "meta_analysis_matrix.csv"


# ── Helpers ────────────────────────────────────────────────────────────────────
def load_matrix(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def record_to_zotero_item(r: dict) -> dict:
    """Converte uma linha do CSV para o formato JSON da API Zotero."""
    paper_id  = r["paper_id"].strip()
    title     = r["title"].strip()
    year      = r["year"].strip()
    venue     = r["venue"].strip()
    abstract  = r["abstract"].strip()
    cluster   = r["cluster_label"].strip()
    method    = r["methodology_type"].strip() or "Not Specified"
    ai_type   = r["ai_type"].strip() or "Not Specified"
    direction = r["main_finding_direction"].strip()
    inequity  = r["inequity"].strip().lower() in ("true", "1")
    ethics    = r["ethics"].strip().lower() in ("true", "1")

    # Monta lista de tags
    tags = [
        {"tag": cluster},
        {"tag": "IA na Educação"},
        {"tag": "Meta-Análise"},
        {"tag": f"Finding: {direction}"},
        {"tag": f"AI: {ai_type}"},
        {"tag": f"Method: {method}"},
    ]
    if inequity:
        tags.append({"tag": "Equidade"})
    if ethics:
        tags.append({"tag": "Ética em IA"})

    # Monta nota extra
    extra_lines = [
        f"Paper ID: {paper_id}",
        f"Methodology: {method}",
        f"AI Type: {ai_type}",
        f"Finding Direction: {direction}",
        f"Inequity Flagged: {inequity}",
        f"Ethics Flagged: {ethics}",
    ]

    return {
        "itemType":        "journalArticle",
        "title":           title,
        "creators":        [{"creatorType": "author", "name": "Author(s) to be verified"}],
        "abstractNote":    abstract,
        "publicationTitle": venue,
        "date":            year,
        "tags":            tags,
        "extra":           "\n".join(extra_lines),
        "language":        "en",
    }


def chunked(lst: list, size: int):
    """Divide uma lista em lotes de tamanho `size`."""
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def post_items(items: list[dict]) -> dict:
    """Envia um lote de itens para a API Zotero e retorna a resposta."""
    payload = json.dumps(items).encode("utf-8")
    req = urllib.request.Request(
        API_BASE,
        data=payload,
        headers={
            "Zotero-API-Key":     ZOTERO_API_KEY,
            "Zotero-API-Version": "3",
            "Content-Type":       "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code}: {body}") from e


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {CSV_PATH}")

    records = load_matrix(CSV_PATH)
    print(f"[✓] {len(records)} artigos carregados de {CSV_PATH.name}")

    items = [record_to_zotero_item(r) for r in records]
    print(f"[✓] {len(items)} itens convertidos para formato Zotero JSON")

    total_ok    = 0
    total_fail  = 0
    total_unchanged = 0

    for batch_num, batch in enumerate(chunked(items, 50), start=1):
        print(f"\n[→] Enviando lote {batch_num} ({len(batch)} itens)…")
        result = post_items(batch)

        ok        = result.get("success",   {})
        failed    = result.get("failed",    {})
        unchanged = result.get("unchanged", {})

        total_ok       += len(ok)
        total_fail     += len(failed)
        total_unchanged += len(unchanged)

        print(f"    ✔ Sucesso:     {len(ok)}")
        print(f"    ✘ Falhas:      {len(failed)}")
        print(f"    ~ Sem mudança: {len(unchanged)}")

        if failed:
            for idx, err in failed.items():
                print(f"      [ERRO item {idx}] {err}")

    print(f"\n── Resumo final ─────────────────────────────────────────────────")
    print(f"   Total enviado com sucesso : {total_ok}")
    print(f"   Total com falha           : {total_fail}")
    print(f"   Total sem mudança         : {total_unchanged}")
    print(f"   Acesse: https://www.zotero.org/leonardorsl/library")


if __name__ == "__main__":
    main()
