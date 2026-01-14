from scene_splitter import split_into_scenes
from prompt_builder import build_prompt
from image_generator import generate_image

dream_text = """..."""

scenes = split_into_scenes(
    dream_text,
    chunk_size=50,
    max_scenes=8
)

output_files = []

for i, scene in enumerate(scenes):
    is_final = (i == len(scenes) - 1)
    prompt = build_prompt(scene, is_final=is_final)
    filename = generate_image(prompt, i)
    output_files.append(filename)

print("\nGenerated images:")
for f in output_files:
    print(f)
