from pathlib import Path
from llama_cpp import Llama

# ---------------------------------------------------
# MODEL PATHS
# ---------------------------------------------------

# ✅ LLaMA MODEL (Disabled)
# MODEL_PATH = Path(__file__).parent / "models" / "llama-3-instruct.Q4_K_M.gguf"

# 🔴 PHI-3 MODEL (Enabled)
MODEL_PATH = Path(__file__).parent / "models" / "phi-3-mini-instruct.Q4_K_M.gguf"


# ---------------------------------------------------
# LOAD MODEL ONCE (IMPORTANT FOR SPEED)
# ---------------------------------------------------

llm = Llama(
    model_path=str(MODEL_PATH),
    n_ctx=2048,
    n_threads=7,
    n_batch=512,
    n_gpu_layers=20,
    verbose=False
)


# ---------------------------------------------------
# GENERATE RESPONSE
# ---------------------------------------------------

def generate_reply(system_prompt, user_prompt):

    # ---------------------------------------------------
    # LLaMA STYLE PROMPT (ACTIVE)
    # ---------------------------------------------------

    prompt = f"""
<|system|>
{system_prompt}

<|user|>
{user_prompt}

<|assistant|>
"""

    # ---------------------------------------------------
    # PHI-3 PROMPT FORMAT (DISABLED)
    # ---------------------------------------------------

    # prompt = f"""
# <|system|>
# {system_prompt}
# <|end|>
# <|user|>
# {user_prompt}
# <|end|>
# <|assistant|>
# """

    output = llm(
    prompt,
    max_tokens=240,
    temperature=0.35,
    top_p=0.9,
    stop=["</s>", "<|end|>", "<|assistant|>", "<|user|>", "User:", "Title:", "Abstract:"]
)

    text = output["choices"][0]["text"].strip()

    # remove accidental conversation markers
    text = text.split("User:")[0]
    text = text.split("<|assistant|>")[0]
    text = text.replace("<|end|>", "").strip()

    return text