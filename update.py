#!/usr/bin/env python3
import requests, json, os

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.790221.xyz/v1"

AVATARS = {
    "白羊座": "https://images.unsplash.com/photo-1635316499385-d912999e525f",
    "金牛座": "https://images.unsplash.com/photo-1628155930542-3c7a64e2c833",
    "双子座": "https://images.unsplash.com/photo-1635316499299-d4193587b1c1",
    "巨蟹座": "https://images.unsplash.com/photo-1635316500057-0130f14652cc",
    "狮子座": "https://images.unsplash.com/photo-1635316500204-6330456f9175",
    "处女座": "https://images.unsplash.com/photo-1635316500115-46f917564d60",
    "天秤座": "https://images.unsplash.com/photo-1635316500511-739c9f2858b4",
    "天蝎座": "https://images.unsplash.com/photo-1635316499645-ec7be329c362",
    "射手座": "https://images.unsplash.com/photo-1635316499990-2591795c643e",
    "摩羯座": "https://images.unsplash.com/photo-1635316500366-075e81d76395",
    "水瓶座": "https://images.unsplash.com/photo-1635316499105-0912999e525f",
    "双鱼座": "https://images.unsplash.com/photo-1635316500438-e6536ec6f395"
}

def fetch_raw(en):
    try:
        res = requests.get(f"https://api.vvhan.com/api/horoscope?type={en}&time=today", timeout=15).json()
        return res['data'] if res.get('success') else None
    except: return None

def deep_ai_full(cn, raw):
    if not DEEPSEEK_API_KEY: return None
    prompt = f"为【{cn}】撰写百科。原始运势：{json.dumps(raw, ensure_ascii=False)}\n输出JSON格式包含：intro(1句), daily(overall,do,dont,tips), base(date,attr,symbol,palace), traits(pros,cons), relations(数组), career(长文本), mythology(长文本)"
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
        raw = fetch_raw(en); ai = deep_ai_full(cn, raw)
        if ai:
            results.append({
                "sign": cn, "avatar": f"{AVATARS[cn]}?auto=format&fit=crop&w=400&q=80", "intro": ai['intro'],
                "daily_guidance": ai['daily'], "base_info": ai['base'], "traits": ai['traits'],
                "relationships": ai['relations'], "career": ai['career'], "mythology": ai['mythology']
            })
    if results:
        with open("index.html", "r", encoding="utf-8") as f: html = f.read()
        start = html.find("// DATA_START") + 13; end = html.find("// DATA_END")
        new_html = html[:start] + f"\nconst db = {json.dumps(results, ensure_ascii=False)};\n" + html[end:]
        with open("index.html", "w", encoding="utf-8") as f: f.write(new_html)
