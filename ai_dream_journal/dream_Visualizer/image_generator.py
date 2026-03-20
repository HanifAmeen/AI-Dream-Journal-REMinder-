import os
from pathlib import Path
import torch

# ============================================================
# 🔥 IMAGE GENERATION TOGGLE
# ============================================================
# HOW TO USE:
#
# 👉 LOCAL (enable images):
# Windows:
#   set ENABLE_IMAGE_GEN=true
#   python -m ai_dream_journal.app
#
# 👉 RENDER (keep OFF):
#   Do NOT set it OR set:
#   ENABLE_IMAGE_GEN=false
#
# ⚠️ IMPORTANT:
# Turning this ON in Render will likely crash the app (no GPU)
# ============================================================

ENABLE_IMAGE_GEN = os.environ.get("ENABLE_IMAGE_GEN", "false") == "true"

# Only import heavy libraries IF enabled
if ENABLE_IMAGE_GEN:
    from diffusers import StableDiffusionPipeline
    from ai_dream_journal.dream_visualizer.prompt_builder import get_negative_prompt

# ------------------------------------
# CPU THREAD OPTIMIZATION
# ------------------------------------
torch.set_num_threads(8)
torch.set_num_interop_threads(8)

# ------------------------------------
# OUTPUT DIRECTORY
# ------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "dream_output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ------------------------------------
# LOAD MODEL (ONLY IF ENABLED)
# ------------------------------------
pipe = None

if ENABLE_IMAGE_GEN:
    print("[INIT] Image generation ENABLED")
    print("[INIT] Loading Stable Diffusion model...")

    pipe = StableDiffusionPipeline.from_pretrained(
        "stabilityai/sd-turbo",
        torch_dtype=torch.float32,
        safety_checker=None
    )

    pipe = pipe.to("cpu")
    pipe.enable_attention_slicing()

    print("[INIT] Model loaded successfully")
else:
    print("[INIT] Image generation DISABLED (safe mode)")

# ------------------------------------
# IMAGE GENERATION FUNCTION
# ------------------------------------
def generate_image(prompt, index):

    # If disabled → skip safely
    if not ENABLE_IMAGE_GEN:
        print("[IMAGE GEN] Skipped (disabled)")
        return None

    filename = OUTPUT_DIR / f"scene_{index}.png"

    print(f"[IMAGE GEN] Saving to: {filename}")
    print(f"[IMAGE GEN] Prompt: {prompt[:80]}")

    with torch.inference_mode():
        image = pipe(
            prompt,
            negative_prompt=get_negative_prompt(),
            width=512,
            height=512,
            num_inference_steps=6,
            guidance_scale=0.0
        ).images[0]

    image.save(filename)

    return filename