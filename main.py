from fastapi import FastAPI
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel
from openai import OpenAI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os,json,random


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://uni-repo.onrender.com"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

class Input(BaseModel):
    text : str
    length : int
    faculty : str

class StructureResponse(BaseModel):
    plan1 : str
    plan2 : str
    plan3 : str

client = OpenAI(api_key=api_key)

HUMANITIES_RULE = ["""
文系レポートとして、以下の流れで見出し構成を作成せよ。
1. 研究背景・問題提起
2. 用語や概念の整理
3. 主要な議論・論点
4. 批判的考察・課題
5. 結論・示唆
""","""
文系レポートとして、以下の流れで見出し構成を作成せよ。
1. 社会的事例から見る問題の導入
2. 重要概念の定義と比較整理
3. 議論の対立軸と主要な論点の抽出
4. 影響評価と未解決課題の検討
5. 結論と実社会への示唆
""","""
文系レポートとして、以下の流れで見出し構成を作成せよ。
1. 調査結果・統計データから見る課題の提示
2. 背景理論・関連研究の要点整理
3. 論点の構造化と重要な主張の分類
4. 批判的検討と方法論的な課題の指摘
5. 総括と今後の研究・社会的示唆
"""]

humanities_selected = random.choice(HUMANITIES_RULE)

SCIENCE_RULE = ["""
理系レポートとして、以下の流れで見出し構成を作成せよ。
1. 研究対象の定義
2. 理論・仕組みの説明
3. 方法・手法・アプローチ
4. 結果・考察
5. 限界と今後の展望
""","""
理系レポートとして、以下の流れで見出し構成を作成せよ。
1. 研究課題の特定と仮説の設定
2. 関連理論モデルの比較と採用根拠
3. 検証設計・実験条件・評価指標
4. 想定される結果とデータ解釈の方針
5. 検証の信頼性・誤差要因・今後の改善
""","""
理系レポートとして、以下の流れで見出し構成を作成せよ。
1. 研究対象の条件と既存研究の前提整理
2. 再現に用いる理論・数式・シミュレーション枠組み
3. 再現手順・比較手法・計測/解析アルゴリズム
4. 比較結果の評価観点と考察の論理構造
5. 再現性の限界・計算/計測の制約・次の研究課題
"""]

science_selected = random.choice(SCIENCE_RULE)

MIXED_RULE = ["""
文理融合系レポートとして、以下の流れで見出し構成を作成せよ。
1. 技術・テーマの概要
2. 技術的仕組みや特徴
3. 社会への応用・影響
4. 課題・リスク・倫理的観点
5. 将来展望
""","""
文理融合系レポートとして、以下の流れで見出し構成を作成せよ。
1. 技術・テーマの概要と社会課題の接続点
2. 技術の動作原理・比較軸・評価観点
3. 産業/教育/生活領域への応用可能性と波及効果
4. 法制度・リスク・倫理面のトレードオフ分析
5. 技術発展シナリオと持続可能な導入の展望
""","""
文理融合系レポートとして、以下の流れで見出し構成を作成せよ。
1. 技術・テーマの全体像と関連技術の階層整理
2. コア機能の特徴と実装アプローチの分類
3. 社会的インパクトの定量/定性評価の方針
4. ガバナンス・リスク管理・倫理指針の設計課題
5. 技術と社会の共進化を前提とした将来の研究方向
"""]

mixed_selected = random.choice(MIXED_RULE)

@app.post("/structure", response_model=StructureResponse)
def structure(data:Input):
    if data.length == 500:
        h2_count = 2
        h3_count = 0
        rule_text = f"H2は{h2_count}個作り、H3は絶対に使用しないでください。簡潔な構成にしてください。"
    elif data.length == 1000:
        h2_count = 3
        h3_count = 2
        rule_text = f"H2は{h2_count}個作り、各H2にH3を{h3_count}個ずつ含めてください。"
    elif data.length == 2000:
        h2_count = 4
        h3_count = 2
        rule_text = f"H2は{h2_count}個作り、各H2にH3を{h3_count}個ずつ含めてください。"

    if data.faculty=="humanities":
        rule = humanities_selected
    elif data.faculty=="science":
        rule = science_selected
    else:
        rule = mixed_selected
    

    messages = [
                {
            "role": "system",
            "content": (
            "あなたは大学レポート構成を3案で生成するAIです。\n"
            "必ず3つそれぞれ独立した構成を内部フォーマットで生成してください。\n\n"

            "⚠最優先ルール（ここを厳守）：\n"
            "・構成の階層は必ずスペース2個を使ってインデントで表現してください\n"
            "・インデントは 2 / 4 / 6 のいずれかの深さでのみ使うこと（半端なスペースは禁止）\n"
            "・見出しラベル（H1/H2/H3/#）は**内部生成では使ってOK、ユーザー向け出力では全削除**\n"
            "・箇条書きは `- ` ではなく `・` で内部生成の段階から統一\n\n"

            "階層構造の例（この形で必ず下書きを作る）：\n"
            "【案1】\n"
            "研究背景・問題提起\n"
            "  SNSの普及の現状\n"
            "  若者のSNS利用率の増加\n"
            "    承認欲求の変化\n"
            "    コミュニケーションのオンライン化\n"
            "  影響の総括\n\n"

            "【案2】\n"
            "研究背景・問題提起\n"
            "  SNSと若者文化の関係\n"
            "    消費行動の変化\n"
            "    トレンド形成の高速化\n"
            "  課題の整理\n\n"

            "【案3】\n"
            "研究背景・問題提起\n"
            "  SNSの社会的浸透\n"
            "    心理的影響\n"
            "    リアル/ネットの関係変化\n"
            "  結論\n\n"

            "このように、スペース2個単位のインデントだけで階層を示した下書きを生成してください。\n\n"
            "それでは生成を開始してください。"
            )
        },
        {
            "role": "user",
            "content": (
                f"課題文:{data.text}\n"
                f"文字数ルール:{rule_text}\n"
                f"学部系ルール:{rule}"
            )
        }
    ]

    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages
    )
    structuring = response.choices[0].message.content
    
    parts= structuring.split("【案")
    plans= StructureResponse(
        plan1="【案" + parts[1] if len(parts) > 1 else "生成失敗",
        plan2="【案" + parts[2] if len(parts) > 2 else "生成失敗",
        plan3="【案" + parts[3] if len(parts) > 3 else "生成失敗",
    )

    path = Path("structures.json")
    if path.exists():
        with open(path,"r",encoding="utf-8") as f:
            structures = json.load(f)
    else:
        structures = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_structure = {
    "time": timestamp,
    "text": data.text,
    "plans": [plans.plan1, plans.plan2, plans.plan3]
    }
    structures.append(new_structure)
    with open(path,"w",encoding="utf-8") as f:
        json.dump(structures,f,ensure_ascii=False,indent=2)
        
    return plans

def converted_structure(text: str) -> str:
    plan1_lines = []
    plan2_lines = []
    plan3_lines = []
    lines = text.splitlines()

    current_plan = 0
    prev_indent = 0
    for line in lines:

        current_indent = len(line) - len(line.lstrip(" "))

        if line.strip().startswith("【案1】"):
            plan1_lines.append("【案1】")
            plan1_lines.append("──────")
            current_plan = 1
            prev_indent = 0
            continue

        elif line.strip().startswith("【案2】"):
            plan2_lines.append("【案2】")
            plan2_lines.append("──────")
            current_plan = 2
            prev_indent = 0
            continue

        elif line.strip().startswith("【案3】"):
            plan3_lines.append("【案3】")
            plan3_lines.append("──────")
            current_plan = 3
            prev_indent = 0
            continue

        clean = line.lstrip()
        clean = clean.replace("#","")
        clean = clean.replace("-","・")

        if clean.startswith(("研究背景・問題提起","用語や概念の整理","主要な議論・論点","批判的考察・課題","結論・示唆")):
            continue

        # 分岐（階層）の開始/継続/終了を検出して縦線をつける
        # prev_indent < current_indent → 右に進んだ = 子の開始
        # prev_indent > 0 and current_indent == 0 → 左に戻った = 子の終了
        if prev_indent >= 2 and current_indent == 0:
            # 子ブロックが終わったので横線を1回だけ追加（どの案モードかで箱を選ぶ）
            if current_plan == 1:
                plan1_lines.append("────")
            elif current_plan == 2:
                plan2_lines.append("────")
            elif current_plan == 3:
                plan3_lines.append("────")

        
        # 追加👇「案モードに応じて保存」
        branch_line = ("│ " * current_indent) + clean if current_indent > 0 else clean
        if current_plan == 1 :
            plan1_lines.append(branch_line)
            continue
        elif current_plan == 2:
            plan2_lines.append(branch_line)
            continue
        elif current_plan == 3 :
            plan3_lines.append(branch_line)
            continue

        prev_indent = current_indent

    plan1_text = "\n".join(plan1_lines)
    plan2_text = "\n".join(plan2_lines)
    plan3_text = "\n".join(plan3_lines)

    return plan1_text+"\n"+plan2_text+"\n"+plan3_text

generated_text = """
【案1】  
研究背景・問題提起  
社会におけるSNSの急速な普及  
若者における価値観の変化の必要性  

用語や概念の整理  
SNSの定義と種類  
価値観と人間関係の関連性  

主要な議論・論点  
SNSがもたらすコミュニケーションの変化  
オンラインとオフラインの人間関係の比較  

批判的考察・課題  
SNS利用による孤独感の増加  
情報の信憑性やプライバシーの問題  

結論・示唆  
SNSの影響を正しく理解する重要性  
今後のSNS利用における注意点  

【案2】  
研究背景・問題提起  
SNSが若者に与える影響の広がり  
重要な研究対象としてのSNSと若者の関係  

用語や概念の整理  
SNSとは何か、具体的な説明  
価値観の変化とそのメカニズム  

主要な議論・論点  
SNSによる新たな社会的つながり  
自己表現と他者評価のダイナミクス  

批判的考察・課題  
SNSの中毒性とその影響  
ネット上の人間関係と実生活の乖離  

結論・示唆  
SNSの影響を踏まえた社会的提言  
若者への教育の必要性  

【案3】  
研究背景・問題提起  
SNSの浸透がもたらした社会変化  
若者の心理的影響についての重要性  

用語や概念の整理  
SNS関連の基本用語  
価値観や人間関係の基礎知識  

主要な議論・論点  
SNS時代における新しい価値観の形成  
仮想空間での人間関係の特徴  

批判的考察・課題  
SNSが引き起こす負の側面  
若者のメンタルヘルスとSNSの関連  

結論・示唆  
SNSの利用についての総合的理解  
今後の課題と対応策の検討  """

print(converted_structure(generated_text))


@app.get("/")
def home():
    return FileResponse("static/index.html")