from pathlib import Path
from llama_cpp import Llama

MODEL_PATH = Path(__file__).parent / "models" / "phi-3-mini-instruct.Q4_K_M.gguf"

# 🔴 LOAD ONCE, GLOBALLY
llm = Llama(
    model_path=str(MODEL_PATH),
    n_ctx=1024,
    n_threads=8,      # adjust to your CPU (usually cores)
    verbose=False
)

def generate_reply(system_prompt, user_prompt):
    output = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=60,        # 🔴 LOWER
        temperature=0.6,
        top_p=0.9,
        stop=["<|end|>", "<|endoftext|>"]
    )

    return output["choices"][0]["message"]["content"].strip()
