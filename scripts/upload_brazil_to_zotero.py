"""
upload_brazil_to_zotero.py
---------------------------
Le data/raw/brazil_research.json e envia os 30 artigos brasileiros
para a biblioteca pessoal do Zotero via API REST.

Credenciais: user leonardorsl (ID 16904895)
"""

import json
import urllib.request
import urllib.error
from pathlib import Path

# -- Credenciais ---------------------------------------------------------------
ZOTERO_USER_ID = "16904895"
ZOTERO_API_KEY = "kNdML8CC5efmAApY3zk33xvQ"
API_BASE       = f"https://api.zotero.org/users/{ZOTERO_USER_ID}/items"

# -- Caminhos ------------------------------------------------------------------
BASE_DIR  = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "data" / "raw" / "brazil_research.json"


# -- Conversao para Zotero JSON ------------------------------------------------
def record_to_zotero_item(p: dict) -> dict:
    """Converte um artigo do brazil_research.json para o formato da API Zotero."""
    authors = p.get("authors") or []
    creators = [{"creatorType": "author", "name": name} for name in authors[:5]] \
               or [{"creatorType": "author", "name": "Autor(es) a verificar"}]

    # Tags enriquecidas
    tags = [
        {"tag": "Pesquisa Brasileira"},
        {"tag": "IA na Educação"},
        {"tag": p.get("doc_type", "Nao classificado")},
    ]
    for theme in (p.get("themes") or "").split("|"):
        t = theme.strip()
        if t and t != "Nao classificado":
            tags.append({"tag": t})

    pub_types = p.get("publication_types") or []
    item_type = "conferencePaper" if any("Conference" in pt for pt in pub_types) else "journalArticle"

    extra_lines = [
        f"Paper ID (Semantic Scholar): {p.get('paper_id', '')}",
        f"Tipo do Documento: {p.get('doc_type', '')}",
        f"Instituição BR: {p.get('institution_br', 'Não identificada')}",
        f"Open Access: {p.get('open_access', False)}",
        f"Query de Origem: {p.get('source_query', '')}",
    ]

    return {
        "itemType":         item_type,
        "title":            p.get("title", ""),
        "creators":         creators,
        "abstractNote":     p.get("abstract", ""),
        "publicationTitle": p.get("venue", ""),
        "date":             str(p.get("year", "")),
        "language":         "pt-BR",
        "tags":             tags,
        "extra":            "\n".join(extra_lines),
    }


def chunked(lst: list, size: int):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def post_items(items: list[dict]) -> dict:
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


# -- Main ----------------------------------------------------------------------
def main():
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {JSON_PATH}")

    data    = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    papers  = data.get("papers", [])
    meta    = data.get("metadata", {})

    print(f"[OK] {len(papers)} artigos carregados de brazil_research.json")
    print(f"     Empiricos: {meta.get('empiricos')} | Teoricos: {meta.get('teoricos')}\n")

    items = [record_to_zotero_item(p) for p in papers]
    print(f"[OK] {len(items)} itens convertidos para formato Zotero JSON")

    total_ok = total_fail = total_unchanged = 0

    for batch_num, batch in enumerate(chunked(items, 50), start=1):
        print(f"\n[->] Enviando lote {batch_num} ({len(batch)} itens)...")
        result = post_items(batch)

        ok        = result.get("success",   {})
        failed    = result.get("failed",    {})
        unchanged = result.get("unchanged", {})

        total_ok        += len(ok)
        total_fail      += len(failed)
        total_unchanged += len(unchanged)

        print(f"    OK Sucesso:     {len(ok)}")
        print(f"    !! Falhas:      {len(failed)}")
        print(f"    ~~ Sem mudanca: {len(unchanged)}")

        if failed:
            for idx, err in failed.items():
                print(f"      [ERRO item {idx}] {err}")

    print(f"\n-- Resumo final ------------------------------------------------")
    print(f"   Total com sucesso  : {total_ok}")
    print(f"   Total com falha    : {total_fail}")
    print(f"   Total sem mudanca  : {total_unchanged}")
    print(f"   Acesse: https://www.zotero.org/leonardorsl/library")


if __name__ == "__main__":
    main()
