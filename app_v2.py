from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles  # ← これも必要！
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
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

# temperatureを設定したsamplerを作成
sampler = make_sampler(
    temp=1.4,
    top_p=0.9,
    )        

# ✅ /generate API
class PromptRequest(BaseModel):
    prompt: str
    max_tokens: int = 300
    num_return_sequences: int = 3  # デフォルトで3案生成

# ✅ 推論API（複数案対応）
@app.post("/generate")
async def generate_text(req: PromptRequest):
    wrapped_prompt = f"<s>[INST] {req.prompt} [/INST]"
    print(f"\U0001f4e5 Prompt: {wrapped_prompt}")

    results = []
    for i in range(req.num_return_sequences):
        response = generate(
            model=model,
            tokenizer=tokenizer,
            prompt=wrapped_prompt,
            max_tokens=req.max_tokens,
            sampler=sampler,
            verbose=False,
        )
        print(f"\U0001f4e4 Response {i+1}: {response}")
        results.append(response)

    return {"responses": results}
