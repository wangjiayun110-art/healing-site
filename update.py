#!/usr/bin/env python3
import requests, json, os

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.790221.xyz/v1"

def fetch_raw(en):
    try:
        res = requests.get(f"https://api.vvhan.com/api/horoscope?type={en}&time=today", timeout=15).json()
        return res['data'] if res.get('success') else None
    except: return None

def deep_ai_encyclopedia(cn, raw):
    if not DEEPSEEK_API_KEY: return None
    prompt = f"""
    为【{cn}】撰写深度百科。原始运势：{json.dumps(raw, ensure_ascii=False)}
    请严格按照以下 JSON 格式输出，内容要详尽、专业、全面（总字数约 600 字）：
    {{
        "intro": "一句话全面介绍该星座的独特魅力。",
        "base": {{
            "date": "该星座的日期范围",
            "attr": "四象属性/守护星/守护神",
            "symbol": "符号及其含义",
            "palace": "三方宫及所掌管的宫位"
        }},
        "traits": {{
            "pros": "详细的核心优点（50字以上）",
            "cons": "详细的短板与缺点（50字以上）"
        }},
        "relations": ["感情/社交中的表现点1", "最佳配对分析", "友谊观分析"],
        "career": "100字左右的事业适合方向与职场建议。",
        "mythology": "150字左右的该星座神话溯源故事。",
        "today_brief": "今日运势简述"
    }}
    """
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
    try:
        res = requests.post(f"{DEEPSEEK_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=90).json()
        return json.loads(res['choices'][0]['message']['content'])
    except: return None

def main():
    signs = [("aries","白羊座"), ("taurus","金牛座"), ("gemini","双子座"), ("cancer","巨蟹座"), ("leo","狮子座"), ("virgo","处女座"), ("libra","天秤座"), ("scorpio","天蝎座"), ("sagittarius","射手座"), ("capricorn","摩羯座"), ("aquarius","水瓶座"), ("pisces","双鱼座")]
    results = []
    for en, cn in signs:
        print(f"正在为 {cn} 编撰百科...")
        raw = fetch_raw(en); ai = deep_ai_encyclopedia(cn, raw)
        if ai:
            results.append({
                "sign": cn, "icon": get_icon(en), "intro": ai['intro'], "today_brief": ai['today_brief'],
                "base_info": ai['base'], "traits": ai['traits'], "relationships": ai['relations'],
                "career": ai['career'], "mythology": ai['mythology']
            })
    if results:
        with open("index.html", "r", encoding="utf-8") as f: html = f.read()
        start = html.find("// DATA_START") + 13; end = html.find("// DATA_END")
        new_html = html[:start] + f"\nconst db = {json.dumps(results, ensure_ascii=False)};\n" + html[end:]
        with open("index.html", "w", encoding="utf-8") as f: f.write(new_html)
        print("✅ 百科全书同步完成")

def get_icon(en):
    return {"aries":"♈️","taurus":"♉️","gemini":"♊️","cancer":"♋️","leo":"♌️","virgo":"♍️","libra":"♎️","scorpio":"♏️","sagittarius":"♐️","capricorn":"♑️","aquarius":"♒️","pisces":"♓️"}.get(en, "✨")

if __name__ == "__main__": main()
