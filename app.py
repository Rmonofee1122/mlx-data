from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles  # ← これも必要！
from mlx_lm import load, generate
import subprocess
import time
import os

app = FastAPI()

# 🔧 モデル読み込み
print("🔄 モデルとLoRAアダプタをロード中...")
t0 = time.time()
model, tokenizer = load(
    "/Users/neo-aichan/models/Llama-3.3-Swallow-70B-v0.4",
    adapter_path="/Users/neo-aichan/models/llama3.3-swallow-70b-mlx-adapter"
)
print(f"✅ モデル読み込み完了: {time.time() - t0:.2f}秒")

# ✅ mount は app 定義のあとに書く！
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ /chat ルート
@app.get("/chat", response_class=HTMLResponse)
async def serve_chat():
    with open("chat.html", encoding="utf-8") as f:
        return f.read()

# ✅ /generate ルート
class PromptRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 1.4
    top_p: float = 0.9

@app.post("/generate")
async def generate_text(req: PromptRequest):

    wrapped_prompt = f"<s>[INST] {req.prompt} [/INST]"

    cmd = [
        "mlx_lm.generate",
        "--model", "/Users/neo-aichan/models/Llama-3.3-Swallow-70B-v0.4",
        "--adapter-path", "/Users/neo-aichan/models/llama3.3-swallow-70b-mlx-adapter",
        "--prompt", wrapped_prompt,
        "--max-tokens", str(req.max_tokens),
        "--temp", str(req.temperature),
        "--top-p", str(req.top_p),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return {"response": result.stdout.strip()}
