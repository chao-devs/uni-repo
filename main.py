from fastapi import FastAPI
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel
from openai import OpenAI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os,json


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

HUMANITIES_RULE = """
文系レポートとして、以下の流れで見出し構成を作成せよ。
1. 研究背景・問題提起
2. 用語や概念の整理
3. 主要な議論・論点
4. 批判的考察・課題
5. 結論・示唆
"""

SCIENCE_RULE = """
理系レポートとして、以下の流れで見出し構成を作成せよ。
1. 研究対象の定義
2. 理論・仕組みの説明
3. 方法・手法・アプローチ
4. 結果・考察
5. 限界と今後の展望
"""

MIXED_RULE = """
文理融合系レポートとして、以下の流れで見出し構成を作成せよ。
1. 技術・テーマの概要
2. 技術的仕組みや特徴
3. 社会への応用・影響
4. 課題・リスク・倫理的観点
5. 将来展望
"""

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
        rule = HUMANITIES_RULE
    elif data.faculty=="science":
        rule = SCIENCE_RULE
    else:
        rule = MIXED_RULE
    

    messages = [
        {
            "role": "system",
            "content": (
            "あなたは大学レポートの構成を3つの案で生成するAIです。"
            "必ず3つそれぞれ**独立した構成**を生成し、"
            "出力はこの順番で行ってください：\n\n"
            "【案1】\n【案2】\n【案3】\n\n"
            "各案ごとにレポート構成を最初から作り直してください。"
            "（案3だけにまとめて書くのは禁止です）\n\n"
            "フォーマットは必ず守ってください：\n"
            "# タイトル\n"
            "## H1：見出し\n"
            "- 書く内容\n"
            "## H2：見出し\n"
            "- 書く内容\n"
            "### H3：見出し\n"
            "- 書く内容\n\n"
            "それでは開始してください。\n\n"
            + rule
            + "\n\n"
            + rule_text
            )
        },
        {
            "role": "user",
            "content": (
                f"課題文:{data.text}\n"
                f"{rule_text}"
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

@app.get("/")
def home():
    return FileResponse("static/index.html")
