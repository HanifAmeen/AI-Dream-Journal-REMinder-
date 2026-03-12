def truncate_prompt(prompt, max_words=120):
    words = prompt.split()
    return " ".join(words[:max_words])


# Core dream style
BASE_STYLE = (
    "dreamlike surreal atmosphere, cinematic lighting, volumetric light, "
    "soft glowing mist, painterly fantasy art, highly detailed, "
    "ethereal mood, symbolic imagery, digital painting, concept art"
)

# Scene composition
SCENE_STYLE = (
    "wide cinematic composition, dynamic perspective, dramatic lighting, "
    "deep atmospheric depth, detailed environment"
)

# Ending scene style
FINAL_STYLE = (
    "symbolic dream ending, emotional resolution, mystical atmosphere, "
    "abstract symbolism, glowing light, surreal environment"
)

# Negative prompt (reduces ugly artifacts)
NEGATIVE_PROMPT = (
    "blurry, low quality, distorted, pixelated, bad anatomy, "
    "extra limbs, watermark, text, cropped, poorly drawn"
)


def build_prompt(scene, is_final=False):

    # Emphasize the subject of the scene
    subject_focus = f"main subject: {scene}"

    if is_final:
        prompt = (
            f"{subject_focus}. surreal symbolic dream ending, "
            f"{FINAL_STYLE}, {SCENE_STYLE}, {BASE_STYLE}"
        )
    else:
        prompt = (
            f"{subject_focus}. cinematic dream scene, "
            f"{SCENE_STYLE}, {BASE_STYLE}"
        )

    return truncate_prompt(prompt)


def get_negative_prompt():
    return NEGATIVE_PROMPT