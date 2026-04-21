import pandas as pd
import json

def process_scraped_data():
    """
    Reads scraped Google Scholar data, processes it, and saves it as a CSV file.
    """
    # Load the raw scraped data
    with open("data/raw/google_scholar_results.json", "r") as f:
        data = json.load(f)

    # Process the data into a list of dictionaries
    processed_data = []
    for result in data:
        processed_data.append({
            "title": result.get("title"),
            "authors": ", ".join(result.get("authors", [])),
            "year": result.get("year"),
            "abstract": result.get("abstract"),
            "url": result.get("url"),
            "source": "Google Scholar"
        })

    # Create a DataFrame and save it to a CSV file
    df = pd.DataFrame(processed_data)
    df.to_csv("data/processed/scraped_papers.csv", index=False)
    print("Processed data saved to data/processed/scraped_papers.csv")

if __name__ == "__main__":
    process_scraped_data()
