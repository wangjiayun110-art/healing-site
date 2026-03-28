#!/usr/bin/env python3
import requests, json, os

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.790221.xyz/v1"

def fetch_raw(en):
    try:
        res = requests.get(f"https://api.vvhan.com/api/horoscope?type={en}&time=today", timeout=15).json()
        return res['data'] if res.get('success') else None
    except: return None

def deep_ai(cn, raw):
    if not DEEPSEEK_API_KEY: return None
    prompt = f"为【{cn}】撰写深度解析。原始：{json.dumps(raw, ensure_ascii=False)}\n直接返回JSON: {{\"theme\":\"4字\",\"today\":\"100字\",\"personality\":\"50字性格\",\"weakness\":\"50字缺点\",\"item\":\"开运物\"}}"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
    try:
        res = requests.post(f"{DEEPSEEK_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=60).json()
        return json.loads(res['choices'][0]['message']['content'])
    except: return None

def main():
    signs = [("aries","白羊座"), ("taurus","金牛座"), ("gemini","双子座"), ("cancer","巨蟹座"), ("leo","狮子座"), ("virgo","处女座"), ("libra","天秤座"), ("scorpio","天蝎座"), ("sagittarius","射手座"), ("capricorn","摩羯座"), ("aquarius","水瓶座"), ("pisces","双鱼座")]
    results = []
    for en, cn in signs:
        raw = fetch_raw(en); ai = deep_ai(cn, raw)
        if ai:
            results.append({
                "sign": cn, "icon": get_icon(en), "theme": ai['theme'], "today_analysis": ai['today'],
                "personality": ai['personality'], "weakness": ai['weakness'],
                "lucky": {"color": raw['luck']['color'], "number": raw['luck']['number'], "match": raw['luck']['constellation'], "item": ai['item']}
            })
    if results:
        with open("index.html", "r", encoding="utf-8") as f: html = f.read()
        start_tag = "// DATA_START"; end_tag = "// DATA_END"
        start_idx = html.find(start_tag) + len(start_tag)
        end_idx = html.find(end_tag)
        new_html = html[:start_idx] + f"\nconst db = {json.dumps(results, ensure_ascii=False)};\n" + html[end_idx:]
        with open("index.html", "w", encoding="utf-8") as f: f.write(new_html)
        print("✅ 同步完成")

def get_icon(en):
    return {"aries":"♈️","taurus":"♉️","gemini":"♊️","cancer":"♋️","leo":"♌️","virgo":"♍️","libra":"♎️","scorpio":"♏️","sagittarius":"♐️","capricorn":"♑️","aquarius":"♒️","pisces":"♓️"}.get(en, "✨")

if __name__ == "__main__": main()
