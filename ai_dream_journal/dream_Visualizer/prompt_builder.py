def truncate_prompt(prompt, max_words=60):
    words = prompt.split()
    return " ".join(words[:max_words])


def build_prompt(scene, is_final=False):
    if is_final:
        style = (
            "symbolic dream conclusion, emotional resolution, "
            "soft glowing light, surreal abstraction, painterly, cinematic, "
            "atmospheric fantasy art"
        )
        full_prompt = f"{scene}. Represent the emotional meaning of the dream. {style}"
        return truncate_prompt(full_prompt)

    style = (
        "surreal dreamlike atmosphere, glowing light, "
        "detailed fantasy art, soft focus, pastel colors"
    )

    full_prompt = f"{scene}, {style}"
    return truncate_prompt(full_prompt)
