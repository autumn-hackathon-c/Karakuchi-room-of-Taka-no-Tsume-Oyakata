# ai_utils.py
import openai

def is_offensive(text: str) -> bool:
    """OpenAI の Moderation API で誹謗中傷・攻撃性をチェック"""
    if not text:
        return False

    moderation = openai.Moderation.create(input=text)
    return moderation.results[0].flagged