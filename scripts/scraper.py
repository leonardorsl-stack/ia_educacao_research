# scripts/scraper.py

import requests
from bs4 import BeautifulSoup
import json
import time
from tqdm import tqdm

def scrape_google_scholar(query, num_pages):
    results = []
    for page in range(num_pages):
        url = f"https://scholar.google.com/scholar?q={query}&start={page * 10}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        for result in soup.find_all("div", class_="gs_ri"):
            title = result.find("h3", class_="gs_rt").text
            link = result.find("a")["href"]
            abstract = result.find("div", class_="gs_rs").text
            results.append({"title": title, "link": link, "abstract": abstract})
        time.sleep(2)  # Delay to avoid being blocked
    return results

if __name__ == "__main__":
    QUERY = (
        '("Artificial Intelligence" OR "Generative AI" OR "Large Language Models" OR "LLM") '
        'AND ("Education" OR "Schools" OR "Higher Education" OR "Pedagogy") '
        'AND ("Social Impact" OR "Inequality" OR "Equity" OR "Ethics" OR "Bias" '
        'OR "Empirical" OR "Case Study" OR "Experiment" OR "Survey" OR "Quantitative" OR "Qualitative")'
    )
    scraped_data = scrape_google_scholar(QUERY, 20)  # Scrape 20 pages
    with open("data/raw/google_scholar_results.json", "w") as f:
        json.dump(scraped_data, f, indent=2)
    print(f"Scraped {len(scraped_data)} articles from Google Scholar.")
