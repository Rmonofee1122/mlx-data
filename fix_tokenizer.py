import json
import os

# 保存先
output_file = "/Users/neo-aichan/models/Llama-3.3-Swallow-70B-v0.4/tokenizer.json"

# もし壊れたファイルがあったらバックアップ
if os.path.exists(output_file):
    os.rename(output_file, output_file + ".bak")
    print(f"✅ 壊れた tokenizer.json をバックアップしました: {output_file}.bak")

# 修正した tokenizer.json 内容
tokenizer_data = {
    "version": "1.0",
    "truncation": None,
    "padding": None,
    "chat_template": "<s>[INST] {{ prompt }} [/INST]{{ completion }}</s>",
    "added_tokens": [
        {"id": 128000, "content": "<|begin_of_text|>", "single_word": False, "lstrip": False, "rstrip": False, "normalized": False, "special": True},
        {"id": 128001, "content": "<|end_of_text|>", "single_word": False, "lstrip": False, "rstrip": False, "normalized": False, "special": True},
    ],
    "normalizer": {
        "type": "Sequence",
        "normalizers": [{"type": "NFKC"}]
    },
    "pre_tokenizer": {"type": "Whitespace"},
    "post_processor": {
        "type": "TemplateProcessing",
        "single": "<|begin_of_text|> $A <|end_of_text|>",
        "pair": "<|begin_of_text|> $A $B:1 <|end_of_text|>",
        "special_tokens": [
            ["<|begin_of_text|>", 128000],
            ["<|end_of_text|>", 128001]
        ]
    },
    "decoder": {"type": "WordPiece", "cleanup": True},
    "model": {
        "type": "WordPiece",
        "unk_token": "<|unk|>",
        "vocab": {"<|unk|>": 0, "<|begin_of_text|>": 128000, "<|end_of_text|>": 128001},
        "continuing_subword_prefix": "##"
    }
}

# 保存
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(tokenizer_data, f, ensure_ascii=False, indent=2)

print(f"✅ tokenizer.json を修復しました: {output_file}")