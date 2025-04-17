from transformers import AutoModelForCausalLM
from peft import PeftModel, PeftConfig
from safetensors.torch import load_file

import torch

# パス設定
base_model_path = "/Users/neo-aichan/models/Llama-3.3-Swallow-70B-v0.4"
adapter_path = "/Users/neo-aichan/models/llama3.3-swallow-70b-mlx-adapter"
output_path = "/Users/neo-aichan/models/merged-llama3.3-swallow-70b"

# ベースモデルロード
model = AutoModelForCausalLM.from_pretrained(base_model_path, device_map="auto", torch_dtype="auto")

# LoRA設定を読み込み
peft_config = PeftConfig.from_pretrained(adapter_path)
peft_config.base_model_name_or_path = base_model_path
model = PeftModel(model, peft_config)

# safetensorsファイルを読み込み
state_dict = load_file(f"{adapter_path}/adapters.safetensors")  # ← ここが修正点

# モデルに重みをロード
model.load_state_dict(state_dict, strict=False)

# LoRAをマージ
model = model.merge_and_unload()

# 保存
model.save_pretrained(output_path)
