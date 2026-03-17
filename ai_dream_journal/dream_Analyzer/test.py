# test.py

from trauma_signal import trauma_linked_score

# ------------------------------
# Test Dreams
# ------------------------------

dream_tests = [
    {
        "name": "Persistent Threat Dream",
        "dream": "I found myself walking through a long empty hallway in an unfamiliar building. "
                 "The lights above were flickering and the atmosphere felt tense. As I kept walking "
                 "I heard footsteps behind me getting closer. I tried several doors but they were all "
                 "locked. Eventually the hallway ended in a dead end and I realized I was trapped "
                 "with nowhere to escape.",
        "emotion_scores": {"fear": 0.9},
        "dynamics": ["pursuit", "locked", "trapped"],
        "no_resolution": True,
        "repeated_threats": True,
        "emotion_variance": 0.1,
        "recurring_count": 0
    },

    {
        "name": "Conflict with Resolution Dream",
        "dream": "I was walking through a crowded market when a group of people nearby started "
                 "arguing loudly. One person began accusing me of something I had not done. "
                 "The situation became tense and I felt angry and overwhelmed as the crowd grew. "
                 "Just when it seemed like a fight might start, someone stepped in and explained "
                 "the misunderstanding. The crowd slowly dispersed and I left feeling relieved.",
        "emotion_scores": {"anger": 0.5, "fear": 0.2, "calm": 0.3},
        "dynamics": ["pressure", "relief", "resolution"],
        "no_resolution": False,
        "repeated_threats": False,
        "emotion_variance": 0.25,
        "recurring_count": 0
    }
]

# ------------------------------
# Run Tests
# ------------------------------

print("\nRunning Dream Trauma Tests\n")

for test in dream_tests:

    score, level = trauma_linked_score(
        emotion_scores=test["emotion_scores"],
        dynamics=test["dynamics"],
        no_resolution=test["no_resolution"],
        repeated_threats=test["repeated_threats"],
        emotion_variance=test["emotion_variance"],
        recurring_count=test["recurring_count"]
    )

    print(f"Dream: {test['name']}")
    print(f"Text: {test['dream']}")
    print(f"Trauma Score: {score}")
    print(f"Level: {level}")
    print("-" * 50)