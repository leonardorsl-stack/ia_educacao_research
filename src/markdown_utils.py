from collections import Counter

def md_table(headers: list[str], rows: list[list]) -> str:
    """Gera uma tabela Markdown a partir de cabeçalhos e linhas."""
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    header_row = "| " + " | ".join(str(h) for h in headers) + " |"
    body = "\n".join("| " + " | ".join(str(c) for c in row) + " |" for row in rows)
    return "\n".join([header_row, sep, body])

def freq_table(counter: Counter, col_label: str) -> str:
    """Converte um Counter em tabela Markdown com contagem e percentual."""
    total = sum(counter.values())
    rows = []
    for value, count in sorted(counter.items(), key=lambda x: -x[1]):
        pct = f"{count / total * 100:.1f}%" if total > 0 else "0.0%"
        rows.append([value, count, pct])
    rows.append(["**Total**", total, "100%"])
    return md_table([col_label, "Contagem", "%"], rows)

def crosstab(records: list[dict], row_key: str, col_key: str) -> str:
    """Tabela cruzada Markdown entre duas variáveis categóricas."""
    row_vals = sorted(set(r[row_key] for r in records))
    col_vals = sorted(set(r[col_key] for r in records))

    # Contagem
    cell: dict[tuple, int] = Counter()
    for r in records:
        cell[(r[row_key], r[col_key])] += 1

    headers = [row_key + " \\ " + col_key] + col_vals + ["Total"]
    rows = []
    col_totals = Counter()
    for rv in row_vals:
        row_data = [rv]
        row_sum = 0
        for cv in col_vals:
            n = cell.get((rv, cv), 0)
            row_data.append(n)
            row_sum += n
            col_totals[cv] += n
        row_data.append(row_sum)
        rows.append(row_data)

    # Linha de totais
    total_row = ["**Total**"] + [col_totals[cv] for cv in col_vals]
    total_row.append(sum(col_totals.values()))
    rows.append(total_row)

    return md_table(headers, rows)
