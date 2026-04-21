import os
from datetime import datetime

def consolidate_results():
    """
    Consolidates analysis results from multiple markdown files and figures into a single document.
    """
    input_files = {
        "summary": "docs/analysis_summary.md",
        "brazil": "docs/brazil_analysis.md",
        "evidence": "results/tables/evidence_table.md"
    }
    
    figures_dir = "results/figures/"
    output_file = "docs/consolidated_results.md"
    
    # Read files
    contents = {}
    for key, path in input_files.items():
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                contents[key] = f.read()
        else:
            contents[key] = f"*Warning: {path} not found.*"

    # Get list of figures
    figures = []
    if os.path.exists(figures_dir):
        figures = [f for f in os.listdir(figures_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.svg'))]
        figures.sort()

    # Build consolidated markdown
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    consolidated_md = f"""# Results Consolidation: AI in Education Research

> Generated automatically on {now}

---

## 1. Global Analysis Summary

{contents['summary']}

---

## 2. Visual Results (Figures)

Below are the visual representations of the research findings.

"""
    
    for fig in figures:
        fig_name = fig.replace('_', ' ').replace('.png', '').replace('.jpg', '').replace('.jpeg', '').replace('.svg', '').title()
        consolidated_md += f"### {fig_name}\n"
        consolidated_md += f"![{fig_name}](../{figures_dir}{fig})\n\n"

    consolidated_md += f"""
---

## 3. Brazilian Context Analysis

{contents['brazil']}

---

## 4. Evidence Table

{contents['evidence']}

---

*End of Consolidated Report*
"""

    # Save output
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(consolidated_md)
    
    print(f"Successfully consolidated results into {output_file}")

if __name__ == "__main__":
    consolidate_results()
