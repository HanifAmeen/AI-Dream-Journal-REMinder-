import json
import os

BASE_DIR = os.path.dirname(__file__)
WEIGHT_PATH = os.path.join(BASE_DIR, "symbol_weights.json")

def load_symbol_weights() -> dict:
    if not os.path.exists(WEIGHT_PATH):
        return {}
    with open(WEIGHT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
