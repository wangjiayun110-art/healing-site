#!/usr/bin/env python3
import requests, json, os, sys
from datetime import datetime

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.790221.xyz/v1"

def fetch_raw(sign_en):
    try:
        res = requests.get(f"https://api.vvhan.com/api/horoscope?type={sign_en}&time=today", timeout=15).json()
        return res['data'] if res.get('success') else None
    except: return None

def deep_ai(sign_cn, raw):
    if not DEEPSEEK_API_KEY: return None
    prompt = f"""
    为【{sign_cn}】撰写深度解析。原始数据：{json.dumps(raw, ensure_ascii=False)}
    直接返回 JSON：
    {{
        "theme": "4字主题",
        "today": "100字今日星象详述",
        "personality": "50字核心性格优点",
        "weakness": "50字核心性格缺点与软肋",
        "item": "开运小物"
    }}
    """
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
    try:
        response = requests.post(f"{DEEPSEEK_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=60)
        return json.loads(response.json()['choices'][0]['message']['content'])
    except: return None

def main():
    signs = [("aries","白羊座"), ("taurus","金牛座"), ("gemini","双子座"), ("cancer","巨蟹座"), ("leo","狮子座"), ("virgo","处女座"), ("libra","天秤座"), ("scorpio","天蝎座"), ("sagittarius","射手座"), ("capricorn","摩羯座"), ("aquarius","水瓶座"), ("pisces","双鱼座")]
    results = []
    print(f"🚀 开始全员同步...")
    for en, cn in signs:
        raw = fetch_raw(en)
        if raw:
            ai = deep_ai(cn, raw)
            if ai:
                results.append({
                    "sign": cn, "icon": get_icon(en), "theme": ai['theme'],
                    "today_analysis": ai['today'], "personality": ai['personality'], "weakness": ai['weakness'],
                    "lucky": {"color": raw['luck']['color'], "number": raw['luck']['number'], "match": raw['luck']['constellation'], "item": ai['item']}
                })
    if results:
        with open("index.html", "r", encoding="utf-8") as f: html = f.read()
        start = html.find("const db ="); end = html.find("];", start) + 1
        new_html = html[:start] + f"const db = {json.dumps(results, ensure_ascii=False)};" + html[end:]
        with open("index.html", "w", encoding="utf-8") as f: f.write(new_html)
        print("✅ 同步完成")

def get_icon(en):
    return {"aries":"♈️","taurus":"♉️","gemini":"♊️","cancer":"♋️","leo":"♌️","virgo":"♍️","libra":"♎️","scorpio":"♏️","sagittarius":"♐️","capricorn":"♑️","aquarius":"♒️","pisces":"♓️"}.get(en, "✨")

if __name__ == "__main__": main()
