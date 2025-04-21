import subprocess
from pathlib import Path
import json
from tqdm import tqdm
import random
import argparse

# 引数処理
parser = argparse.ArgumentParser(description="mlx-lm 生成バッチスクリプト")
parser.add_argument('--samples', type=int, default=1000, help='生成するサンプル数 (default: 1000)')
parser.add_argument('--output', type=str, default='generated.jsonl', help='出力ファイル名 (default: generated.jsonl)')
args = parser.parse_args()

# 保存先
output_file = Path(args.output)

# プロンプトリスト（ランダム化用）
prompts = [
    "裏垢女子としてInstagramに投稿するメッセージを考えて",
    "裏垢女子らしい魅力的な投稿を作ってください",
    "エロかわいい裏垢女子のInstagram投稿文を考えて",
    "裏垢女子として誘惑たっぷりのメッセージを考えてください",
    "裏垢女子としてフォロワーが興奮するような投稿を考えて",
    "裏垢女子っぽくてドキドキする投稿メッセージを考えて",
    "裏垢女子としてフォロワーの妄想を掻き立てるような投稿文を考えて",
    "セクシーで小悪魔的な裏垢女子の投稿文を作って",
    "裏垢女子として見た人が思わず二度見しちゃうような誘惑の言葉を考えて",
    "裏垢女子の魅力が溢れる投稿キャプションを考えて",
    "裏垢女子としてついフォローしたくなるエロかわいい投稿を作って",
    "裏垢女子として大人の色気たっぷりなInstagram投稿文を考えて",
    "裏垢女子としてフォロワーの欲望を刺激するような投稿メッセージを考えて",
    "裏垢っぽさ全開で挑発的な投稿文を考えて",
    "裏垢女子として甘くて危険な雰囲気のInstagram投稿文を考えて"
]

# 保存先ファイル初期化
with open(output_file, 'w', encoding='utf-8') as f:
    pass  # 空にしておく

# tqdm プログレスバー付きループ
for _ in tqdm(range(args.samples), desc="Generating samples"):
    prompt = random.choice(prompts)

    # mlx_lm.generate 実行
    result = subprocess.run(
        [
            "mlx_lm.generate",
            "--model", "/Users/neo-aichan/models/Llama-3.3-Swallow-70B-v0.4",
            "--adapter-path", "/Users/neo-aichan/models/llama3.3-swallow-70b-mlx-adapter",
            "--prompt", prompt,
            "--ignore-chat-template",
            "--temp", "1.2",
            "--top-p", "0.95",
            "--max-tokens", "100"
        ],
        capture_output=True,
        text=True
    )

    # 出力クリーンアップ
    output = result.stdout
    try:
        clean_text = output.split('==========')[1].strip()
        # 末尾 </s> や余計な文字も消す
        clean_text = clean_text.replace("<s>", "").strip()
        clean_text = clean_text.replace("</s>", "").strip()
        clean_text = clean_text.replace("<>", "").strip()
        clean_text = clean_text.replace("<", "").strip()
        clean_text = clean_text.replace(">", "").strip()
        clean_text = clean_text.replace("</>", "").strip()
        clean_text = clean_text.replace("</", "").strip()
        clean_text = clean_text.replace("/>", "").strip()
        clean_text = clean_text.replace("<l>", "").strip()
        clean_text = clean_text.replace("</l>", "").strip()
        clean_text = clean_text.replace("<black>", "").strip()
        clean_text = clean_text.replace("</black>", "").strip()
        clean_text = clean_text.replace("<black", "").strip()
        clean_text = clean_text.replace("/black>", "").strip()
        clean_text = clean_text.replace("<strong>", "").strip()
        clean_text = clean_text.replace("</strong>", "").strip()
        clean_text = clean_text.replace("/strong>", "").strip()
        clean_text = clean_text.replace("<strong", "").strip()

        clean_text = clean_text.replace("[INST]", "").strip()
        clean_text = clean_text.replace("INST", "").strip()
        clean_text = clean_text.replace("/", "").strip()
        clean_text = clean_text.replace("\n", "").strip()
        clean_text = clean_text.replace("SPAN", "").strip()
        clean_text = clean_text.replace("span", "").strip()
        clean_text = clean_text.replace("[/INST]", "").strip()
        clean_text = clean_text.replace("strong", "").strip()




        # ここで特定のキーワードを含む場合はスキップ
        forbidden_keywords = ["政治", "選挙", "宗教", "神", "仏教", "キリスト", "イスラム", 
                              "宗教的", "信仰", "信者", "教義", "教え", "教会", "寺院", "神社", 
                              "聖地", "聖典", "教祖", "教団", "信仰心", "信仰対象", "宗教法人",
                              "靖国", "天皇", "皇室", "自民党", "民主党", "共産党", "公明党",
                              "支那", "移民", "難民","外人", "右翼", "左翼", "ナショナリズム","資産",
                              "黒人", "白人", "アジア人", "人種差別", "差別", "ヘイト", "ヘイトスピーチ",]
        if any(keyword in clean_text for keyword in forbidden_keywords):
            clean_text = ""
            continue
    except IndexError:
        clean_text = ""

    if clean_text:
        with open(output_file, 'a', encoding='utf-8') as f:
            json.dump({"prompt": prompt, "completion": clean_text}, f, ensure_ascii=False)
            f.write('\n')
            f.write('\n')