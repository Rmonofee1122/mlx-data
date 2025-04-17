import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# ==== 設定 ====
MODEL_PATH = "/Users/neo-aichan/models/Llama-3.3-Swallow-70B-v0.4"
ADAPTER_PATH = Path("/Users/neo-aichan/models/llama3.3-swallow-70b-mlx-adapter")
DATA_PATH = Path.home() / "mlx-data"
ADAPTER_FILE = ADAPTER_PATH / "adapter.safetensors"

# ==== バックアップ処理 ====
if ADAPTER_FILE.exists():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = ADAPTER_PATH.parent / f"{ADAPTER_PATH.name}_backup_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ 既存のアダプタをバックアップ: {backup_dir}")
    shutil.copytree(ADAPTER_PATH, backup_dir, dirs_exist_ok=True)

# ==== 学習開始 ====
print("🚀 LoRA ファインチューニングを開始します...")
cmd = [
    "mlx_lm.lora",
    "--model", str(MODEL_PATH),
    "--train",
    "--data", str(DATA_PATH),
    "--fine-tune-type", "lora",
    "--batch-size", "1",
    "--iters", "3000",
    "--learning-rate", "1e-4",
    "--adapter-path", str(ADAPTER_PATH),
    "--steps-per-report", "500"
]

# 実行
subprocess.run(cmd)