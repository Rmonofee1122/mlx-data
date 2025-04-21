from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, LoraConfig
import torch
import os

base_model_path = "/Users/neo-aichan/models/Llama-3.3-Swallow-70B-v0.4"
lora_adapter_path = "/Users/neo-aichan/models/llama3.3-swallow-70b-mlx-adapter"
save_path = "/Users/neo-aichan/models/llama3.3-swallow-70b-mlx-merged"

# baseモデル読み込み
model = AutoModelForCausalLM.from_pretrained(
    base_model_path,
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
    trust_remote_code=True
)

# まず仮のLoraConfigを使ってPEFTモデル化
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # 必要に応じて調整
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
model = PeftModel(model, lora_config)

# safetensors を一括読み込み
from safetensors.torch import load_file

# 複数shardがある場合、すべてマージして読み込み
weights = {}
for fname in sorted(os.listdir(lora_adapter_path)):
    if fname.endswith(".safetensors"):
        w = load_file(os.path.join(lora_adapter_path, fname))
        weights.update(w)

model.load_state_dict(weights, strict=False)

# LoRA統合 & 保存
model = model.merge_and_unload()
model.save_pretrained(save_path)

# tokenizerも保存
tokenizer = AutoTokenizer.from_pretrained(base_model_path)
tokenizer.save_pretrained(save_path)