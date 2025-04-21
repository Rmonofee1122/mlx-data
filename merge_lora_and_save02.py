from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base_model_path = "/Users/neo-aichan/models/Llama-3.3-Swallow-70B-v0.4"
lora_adapter_path = "/Users/neo-aichan/models/llama3.3-swallow-70b-mlx-adapter"
merged_output_path = "/Users/neo-aichan/models/llama3.3-swallow-70b-mlx-merged-v2"

model = AutoModelForCausalLM.from_pretrained(base_model_path, device_map="auto", trust_remote_code=True)
model = PeftModel.from_pretrained(model, lora_adapter_path, is_trainable=True)  # ★ ここを修正
model = model.merge_and_unload()
model.save_pretrained(merged_output_path)

tokenizer = AutoTokenizer.from_pretrained(base_model_path)
tokenizer.save_pretrained(merged_output_path)
