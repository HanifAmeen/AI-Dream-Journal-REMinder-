import csv
from pathlib import Path

from Dream_text_preprocessing import process_dreambank_csv_row

# ---- PATH SETUP ----
BASE_DIR = Path(__file__).resolve().parent.parent  # ai_dream_journal/
DREAMBANK_CSV = BASE_DIR / "datasets" / "dreambank.csv"
OUTPUT_CSV = BASE_DIR / "datasets" / "dreambank_processed_full.csv"


# ---- COLUMN CONFIG ----
TEXT_COLUMN = "report"
KEEP_COLUMNS = ["number", "character", "emotion"]
SAMPLE_SIZE = None  # process entire file


# ---- LOAD + PROCESS ----
rows_out = []

with open(DREAMBANK_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)

    for i, row in enumerate(reader):
        if SAMPLE_SIZE is not None and i >= SAMPLE_SIZE:
            break

        raw_text = row.get(TEXT_COLUMN, "")
        if not raw_text:
            continue

        processed = process_dreambank_csv_row(raw_text)

        out_row = {
            "number": row.get("number", ""),
            "character": row.get("character", ""),
            "emotion": row.get("emotion", ""),
            "raw_text": raw_text,
            "narrative_text": processed["narrative_text"],
            "semantic_text": processed["semantic_text"],
        }

        rows_out.append(out_row)

# ---- SAVE RESULT ----
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "number",
            "character",
            "emotion",
            "raw_text",
            "narrative_text",
            "semantic_text",
        ]
    )
    writer.writeheader()
    writer.writerows(rows_out)

print(f"Processed {len(rows_out)} dreams → {OUTPUT_CSV}")
