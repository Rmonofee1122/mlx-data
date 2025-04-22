from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles  # ← これも必要！
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
import subprocess
import time
import os
import json
import asyncio

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
    stream: bool = False  # ストリーミング生成を制御するフラグ

# トークンごとに生成するジェネレータ関数
async def generate_tokens(prompt, max_tokens, sequence_idx=0):
    wrapped_prompt = f"<s>[INST] {prompt} [/INST]"
    print(f"\U0001f4e5 Prompt: {wrapped_prompt}")
    
    # 生成されたテキスト全体
    full_text = ""
    
    # generate関数を使用してテキストを生成
    response = generate(
        model=model,
        tokenizer=tokenizer,
        prompt=wrapped_prompt,
        max_tokens=max_tokens,
        sampler=sampler,
        verbose=False,
    )
    
    # 生成されたテキストを1文字ずつストリーミング
    for i in range(len(response)):
        # 1文字ずつ取得
        delta = response[i]
        full_text += delta
        
        # 新しいテキスト部分を返す
        yield json.dumps({"delta": delta, "sequence_idx": sequence_idx}) + "\n"
        
        # 少し待機してストリーミング効果を強調
        await asyncio.sleep(0.01)
    
    print(f"\U0001f4e4 Response {sequence_idx+1}: {full_text}")

# ✅ 推論API（複数案対応）
@app.post("/generate")
async def generate_text(req: PromptRequest):
    # ストリーミングモードが無効の場合は従来の方法で生成
    if not req.stream:
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
    
    # ストリーミングモードが有効の場合はStreamingResponseを返す
    async def stream_generator():
        for i in range(req.num_return_sequences):
            async for token in generate_tokens(req.prompt, req.max_tokens, i):
                yield token
        
        # 生成完了を示す終了メッセージ
        yield json.dumps({"finish": True}) + "\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="application/x-ndjson"
    )

# ✅ ストリーミング専用エンドポイント
@app.post("/generate_stream")
async def generate_stream(req: PromptRequest):
    async def stream_generator():
        for i in range(req.num_return_sequences):
            async for token in generate_tokens(req.prompt, req.max_tokens, i):
                yield token
        
        # 生成完了を示す終了メッセージ
        yield json.dumps({"finish": True}) + "\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="application/x-ndjson"
    )
