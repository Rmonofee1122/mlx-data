import json

# 読み込むファイルパス
input_path = "/Users/neo-aichan/models/Llama-3.3-Swallow-70B-v0.4/tokenizer.json"
backup_path = "/Users/neo-aichan/models/Llama-3.3-Swallow-70B-v0.4/tokenizer_backup.json"
output_path = input_path  # 上書き

# バックアップを取る
with open(input_path, "r", encoding="utf-8") as f:
    data = f.read()

with open(backup_path, "w", encoding="utf-8") as f:
    f.write(data)

print(f"✅ バックアップ作成済み: {backup_path}")

# 読み込んでパースする（構文エラーがある場合はここでエラーが出る）
try:
    tokenizer_json = json.loads(data)
    print("✅ tokenizer.json の構文チェック OK")
except json.JSONDecodeError as e:
    print(f"❌ JSON 構文エラー: {e}")
    print("👉 手動修正または自動修正ツールを使ってください。")
    exit(1)

# 整形して書き出す
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(tokenizer_json, f, ensure_ascii=False, indent=2)

print(f"✅ 修正済み tokenizer.json を保存しました: {output_path}")