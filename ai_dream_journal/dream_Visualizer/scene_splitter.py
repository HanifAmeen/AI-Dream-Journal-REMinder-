def split_into_scenes(
    dream_text: str,
    chunk_size: int = 50,
    max_scenes: int = 8
):
    words = dream_text.split()
    total_words = len(words)

    scenes = []

    # Reserve 1 slot for the final "conclusion" image
    max_main_scenes = max_scenes - 1

    for i in range(max_main_scenes):
        start = i * chunk_size
        end = start + chunk_size

        if start >= total_words:
            break

        scene_words = words[start:end]
        scenes.append(" ".join(scene_words))

    # Final scene = remaining text
    remaining_start = len(scenes) * chunk_size
    if remaining_start < total_words:
        remaining_words = words[remaining_start:]
        scenes.append(" ".join(remaining_words))

    return scenes
