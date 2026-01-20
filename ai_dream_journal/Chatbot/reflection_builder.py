def build_reflection(dream_context, followups):
    if not followups:
        return None

    last = followups[-1]
    answer = last["answer"].lower()

    if "exam" in answer or "test" in answer:
        return (
            "Your response suggests this dream may be tied to performance pressure. "
            "The sense of being unprepared in the dream mirrors a real-life concern "
            "about evaluation and expectations."
        )

    if "work" in answer or "job" in answer:
        return (
            "This dream appears to reflect stress related to responsibility or "
            "external expectations rather than the specific events in the dream."
        )

    return (
        "Your answer helps ground the dream in current waking-life concerns, "
        "suggesting the symbols reflect ongoing emotional pressure rather than "
        "random imagery."
    )
