from diffusers import StableDiffusionPipeline
import torch
from pathlib import Path
from prompt_builder import get_negative_prompt

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
# LOAD MODEL (CPU SAFE CONFIG)
# ------------------------------------
pipe = StableDiffusionPipeline.from_pretrained(
    "stabilityai/sd-turbo",
    torch_dtype=torch.float32,
    safety_checker=None
)

pipe = pipe.to("cpu")

# Memory optimizations
pipe.enable_attention_slicing()

# ------------------------------------
# IMAGE GENERATION
# ------------------------------------
def generate_image(prompt, index):

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