from concurrent.futures import ThreadPoolExecutor
from scene_splitter import split_into_scenes
from prompt_builder import build_prompt
from image_generator import generate_image

dream_text = """..."""

scenes = split_into_scenes(
    dream_text,
    chunk_size=50,
    max_scenes=8
)

def process_scene(args):
    i, scene, total = args
    is_final = (i == total - 1)
    prompt = build_prompt(scene, is_final=is_final)
    return generate_image(prompt, i)

with ThreadPoolExecutor() as executor:
    output_files = list(
        executor.map(process_scene, [(i, s, len(scenes)) for i, s in enumerate(scenes)])
    )

print("\nGenerated images:")
for f in output_files:
    print(f)