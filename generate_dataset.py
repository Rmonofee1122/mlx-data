import json
import random
from pathlib import Path

# 保存先ディレクトリ
output_dir = Path.home() / "mlx-data"
output_dir.mkdir(parents=True, exist_ok=True)

# テンプレートとなるプロンプト
prompt_template = "あなたは裏垢女子です。Instagramに投稿する性的なメッセージを言ってください"

# 生成するサンプル数
num_samples = 100

# サンプルメッセージのリスト（必要に応じて追加できます）
messages = [
    "寂しい夜は甘い言葉で満たしてほしいな…💋 #裏垢女子 #大人の時間",
    "誰にも言えない秘密、ここだけで教えてあげる❤️ #秘密の夜",
    "優しくしてくれる人、待ってます💖 #ひみつ #密会希望",
    "今日はちょっと大胆になっちゃおうかな？🙈💋",
    "もっと近くで感じたい…そんな夜💫 #ドキドキ",
    "見えそうで見えない、そんなのずるいよね？❤️",
    "声、聞かせてくれる？夜はまだこれから…💋",
    "危ないくらいに惹かれ合いたいの💖",
    "私のこと、もっと知って欲しいな…😘 #秘密の私",
    "あなただけに見せる表情があるの…💕 #裏垢限定"
]

# データセット分割比率
train_ratio = 0.8
valid_ratio = 0.1
test_ratio = 0.1

# データ生成
data = []
for _ in range(num_samples):
    completion = random.choice(messages)
    data.append({
        "prompt": prompt_template,
        "completion": completion
    })

# シャッフルして分割
random.shuffle(data)
train_data = data[:int(num_samples * train_ratio)]
valid_data = data[int(num_samples * train_ratio):int(num_samples * (train_ratio + valid_ratio))]
test_data = data[int(num_samples * (train_ratio + valid_ratio)):]

# 保存関数
def save_jsonl(data_list, filename):
    with open(output_dir / filename, "w", encoding="utf-8") as f:
        for entry in data_list:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')

# 保存
save_jsonl(train_data, "train.jsonl")
save_jsonl(valid_data, "valid.jsonl")
save_jsonl(test_data, "test.jsonl")

print(f"✅ データセット生成完了！保存先: {output_dir}")
print(f"Train: {len(train_data)} samples, Valid: {len(valid_data)} samples, Test: {len(test_data)} samples")