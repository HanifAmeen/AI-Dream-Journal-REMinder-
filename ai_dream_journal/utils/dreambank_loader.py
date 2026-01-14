import os
import pandas as pd

def load_dreambank(path=None):
    if path is None:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(BASE_DIR, "datasets", "dreambank.csv")

    df = pd.read_csv(path)
    df = df[["number", "report"]].dropna()
    df.rename(columns={"number": "dream_id", "report": "text"}, inplace=True)
    return df
