import os
import tempfile
import json
import unittest
from pathlib import Path
import sys

# Adiciona a raiz do projeto ao sys.path para importar o pacote src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils import save_json, load_json, load_csv

class TestUtils(unittest.TestCase):

    def test_json_io(self):
        data = {"key": "value", "lista": [1, 2, 3]}
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            save_json(data, path)
            self.assertTrue(path.exists())
            loaded = load_json(path)
            self.assertEqual(loaded, data)

    def test_csv_io(self):
        import csv
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.csv"
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["coluna_1", "coluna_2"])
                writer.writeheader()
                writer.writerow({"coluna_1": "valor_1", "coluna_2": "valor_2"})
            
            loaded = load_csv(path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["coluna_1"], "valor_1")
            self.assertEqual(loaded[0]["coluna_2"], "valor_2")

if __name__ == '__main__':
    unittest.main()
