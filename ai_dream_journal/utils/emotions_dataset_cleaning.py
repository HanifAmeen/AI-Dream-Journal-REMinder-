import pandas as pd

# ------------------------------------------------
# File paths
# ------------------------------------------------
input_file = r"C:\Users\amjad\Downloads\Research Papers 2025\Dream Journal\AI -Dream Journal APP\ai_dream_journal\datasets\NRC-Emotion-Lexicon.csv"

output_file = r"C:\Users\amjad\Downloads\Research Papers 2025\Dream Journal\AI -Dream Journal APP\ai_dream_journal\datasets\NRC_cleaned_emotions.csv"


# ------------------------------------------------
# Load dataset
# ------------------------------------------------
df = pd.read_csv(input_file)

print("Original columns:")
print(df.columns)


# ------------------------------------------------
# Keep only English + emotion columns
# ------------------------------------------------
columns_to_keep = [
    "English (en)",
    "Anger",
    "Anticipation",
    "Disgust",
    "Fear",
    "Joy",
    "Sadness",
    "Surprise",
    "Trust"
]

df = df[columns_to_keep]


# ------------------------------------------------
# Rename English column to "word"
# ------------------------------------------------
df = df.rename(columns={"English (en)": "word"})


# ------------------------------------------------
# Remove rows where word is missing
# ------------------------------------------------
df = df.dropna(subset=["word"])


# ------------------------------------------------
# Save cleaned dataset
# ------------------------------------------------
df.to_csv(output_file, index=False)

print("\nCleaned dataset saved to:")
print(output_file)

print("\nExample rows:")
print(df.head())