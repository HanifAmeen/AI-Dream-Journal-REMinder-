from diffusers import StableDiffusionPipeline
import torch
from pathlib import Path

# ------------------------------------
# 🔧 ABSOLUTE OUTPUT DIRECTORY (CRITICAL FIX)
# ------------------------------------
# This ensures Flask and the generator use THE SAME folder
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "dream_output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ------------------------------------
# LOAD SD TURBO (FAST)
# ------------------------------------
pipe = StableDiffusionPipeline.from_pretrained(
    "stabilityai/sd-turbo",
    torch_dtype=torch.float32
).to("cpu")

pipe.enable_attention_slicing()

# ------------------------------------
# IMAGE GENERATION
# ------------------------------------
def generate_image(prompt, index):
    filename = OUTPUT_DIR / f"scene_{index}.png"

    print(f"[IMAGE GEN] Saving to: {filename}")
    print(f"[IMAGE GEN] Prompt: {prompt[:80]}")

    image = pipe(
        prompt,
        width=384,
        height=384,
        num_inference_steps=4,   # Turbo sweet spot
        guidance_scale=0.0       # REQUIRED for Turbo
    ).images[0]

    image.save(filename)
    return filename
