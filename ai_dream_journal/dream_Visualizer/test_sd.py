import time
from scene_splitter import split_into_scenes
from prompt_builder import build_prompt
from image_generator import generate_image

# ------------------------------------
# TEST DREAM
# ------------------------------------
dream_text = """
Last night, I found myself standing on a wide mountain ledge where white mist drifted slowly below.
A small group of goats moved calmly around me, their hooves making no sound against the stone.
One goat with long curved horns stepped closer and looked at me as if it recognized me.
As it walked past, the ground beneath its feet turned warm and green, sprouting grass instantly.
More goats appeared along the cliffs, balancing effortlessly on narrow edges that should not have held them.
I followed them upward, feeling strangely steady even as the path narrowed.
At the peak, a large goat stood silhouetted against the sky, its eyes glowing softly like lanterns.
When it nodded its head, the mountain seemed to breathe, and I felt a deep sense of calm and belonging.
The wind carried the sound of bells, though none of the goats wore any.
As the mist closed in, the goats faded into the light, and I woke up feeling grounded and peaceful.
"""


# ------------------------------------
# PARAMETERS
# ------------------------------------
CHUNK_SIZE = 50
MAX_SCENES = 8

# ------------------------------------
# SPLIT INTO SCENES
# ------------------------------------
scenes = split_into_scenes(
    dream_text,
    chunk_size=CHUNK_SIZE,
    max_scenes=MAX_SCENES
)

total = len(scenes)

print(f"\nScenes generated: {total}")
for i, s in enumerate(scenes):
    print(f"\n--- Scene {i} ({len(s.split())} words) ---\n{s}")

# ------------------------------------
# IMAGE GENERATION WITH PROGRESS
# ------------------------------------
output_files = []
overall_start = time.time()

print("\nStarting image generation...\n")

for i, scene in enumerate(scenes, start=1):
    is_final = (i == total)
    prompt = build_prompt(scene, is_final=is_final)

    percent = int((i - 1) / total * 100)
    bar = "█" * (percent // 10) + "-" * (10 - percent // 10)

    print(f"[{bar}] {percent}% — Generating image {i}/{total}")
    print(f"Prompt preview: {prompt[:80]}...\n")

    start = time.time()
    filename = generate_image(prompt, i - 1)
    elapsed = time.time() - start

    output_files.append(filename)

    percent_done = int(i / total * 100)
    bar_done = "█" * (percent_done // 10) + "-" * (10 - percent_done // 10)

    print(f"[{bar_done}] {percent_done}% — Done image {i}/{total} "
          f"({elapsed:.1f}s)\n")

# ------------------------------------
# FINAL SUMMARY
# ------------------------------------
total_time = time.time() - overall_start

print("\nGeneration complete.")
print(f"Total time: {total_time/60:.2f} minutes")
print("\nGenerated images:")

for f in output_files:
    print(f)
