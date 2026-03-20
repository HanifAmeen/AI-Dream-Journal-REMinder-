import os
from pathlib import Path

# ============================================================
# 🔥 LLM TOGGLE
# ============================================================
# LOCAL:
#   set ENABLE_LLM=true
#
# RENDER:
#   leave it OFF
# ============================================================

ENABLE_LLM = os.environ.get("ENABLE_LLM", "false") == "true"

# ---------------------------------------------------
# MODEL PATH
# ---------------------------------------------------

MODEL_PATH = Path(__file__).parent / "models" / "phi-3-mini-instruct.Q4_K_M.gguf"

# ---------------------------------------------------
# LOAD MODEL ONLY IF ENABLED
# ---------------------------------------------------

llm = None

if ENABLE_LLM:
    from llama_cpp import Llama

    print("[LLM] Loading local model...")

    llm = Llama(
        model_path=str(MODEL_PATH),
        n_ctx=2048,
        n_threads=7,
        n_batch=512,
        n_gpu_layers=20,
        verbose=False
    )

    print("[LLM] Model loaded")
else:
    print("[LLM] Disabled (safe mode)")


# ---------------------------------------------------
# GENERATE RESPONSE
# ---------------------------------------------------

def generate_reply(system_prompt, user_prompt):

    # 🔴 If disabled → safe fallback
    if not ENABLE_LLM or llm is None:
        return "Chatbot is unavailable in this environment."

    prompt = f"""
<|system|>
{system_prompt}

<|user|>
{user_prompt}

<|assistant|>
"""

    output = llm(
        prompt,
        max_tokens=240,
        temperature=0.35,
        top_p=0.9,
        stop=["</s>", "<|end|>", "<|assistant|>", "<|user|>", "User:", "Title:", "Abstract:"]
    )

    text = output["choices"][0]["text"].strip()

    # cleanup
    text = text.split("User:")[0]
    text = text.split("<|assistant|>")[0]
    text = text.replace("<|end|>", "").strip()

    return text