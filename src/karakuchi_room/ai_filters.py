from openai import OpenAI
import os
import re

client = OpenAI(api_key=os.environ["API_KEY"])

# --------------------------
# NGワード（弱攻撃含む）
# --------------------------
NG_PATTERNS = [
    r"むかつく",
    r"ムカつく",
    r"ムカツク",
    r"腹立つ",
    r"ばか", r"バカ", r"馬鹿", r"アホ", r"ボケ",
    r"死ね", r"しね",
    r"殺す", r"ころす",
]

def contains_ng_word(text: str) -> bool:
    """独自NGワードの検出"""
    return any(re.search(p, text) for p in NG_PATTERNS)

def is_offensive(text: str) -> bool:
    """ChatGPT によるカスタム誹謗中傷チェック"""

    if not text or not text.strip():
        return False
    
    # --------------------------
    # ① NGワード辞書チェック（最優先）
    # --------------------------
    if contains_ng_word(text):
        return True
    
    # --------------------------
    # ② Moderation API
    # --------------------------
    moderation = client.moderations.create(
        model="omni-moderation-latest",
        input=text
    )
    if moderation.results[0].flagged:
        return True
    
    # --------------------------
    # ③ ChatGPT による弱攻撃判定
    # --------------------------

    prompt = f"""
あなたは誹謗中傷検知AIです。

次の文章が以下のいずれかに該当する場合、必ず「NG」と判断してください。

【NGとする】
- 他者への侮辱（例：ばか、バカ、馬鹿、アホ、ボケなど全バリエーション）
- 人格否定（例：お前は価値がない、無能など）
- 嘲笑（例：だせぇ）
- 攻撃的・乱暴な表現（例：うざい、きもい、くそが、ざけんな）
- “むかつく” のような否定感情が **相手に向けられている** 場合
- 暴力表現（例：殺す、ころす、殴る）
- 相手を傷つける可能性がある表現（例：あいつ嫌い、こいつ無理）

【OKとする】
- 攻撃性のない批評（例：改善の余地があると思います）

必ず「OK」か「NG」だけを返してください。

文章：
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    result = response.choices[0].message.content.strip()

    return result == "NG"