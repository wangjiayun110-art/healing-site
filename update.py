#!/usr/bin/env python3
import requests
import json
import os
import sys
from datetime import datetime

# 配置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.790221.xyz/v1"

def fetch_raw_horoscope(sign_en):
    """获取真实星座原始数据"""
    try:
        url = f"https://api.vvhan.com/api/horoscope?type={sign_en}&time=today"
        res = requests.get(url, timeout=10)
        data = res.json()
        if data.get('success'):
            return data['data']
    except Exception as e:
        print(f"Fetch {sign_en} failed: {e}")
    return None

def heal_ify_content(sign_cn, raw):
    """AI 治愈化重写"""
    prompt = f"""
    将以下星座运势数据重写为【极具温情、文艺、疗愈】的深度解析。
    星座：{sign_cn} | 原始：{json.dumps(raw, ensure_ascii=False)}
    
    直接返回以下 JSON 格式：
    {{
        "theme": "4字治愈主题",
        "short_text": "30字内文艺金句",
        "long_analysis": "150字左右温情疏导文案",
        "guide": "今日疗愈指南建议",
        "forbidden": "今日禁忌建议"
    }}
    """
    
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
    
    try:
        response = requests.post(f"{DEEPSEEK_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=30)
        return json.loads(response.json()['choices'][0]['message']['content'])
    except Exception as e:
        print(f"AI heal-ify {sign_cn} failed: {e}")
        return None

def update_index_html(horo_json):
    """更新 HTML 首页内容"""
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    # 查找脚本中的数据定义并替换 (更稳健的方式)
    start_marker = "const horoData ="
    end_marker = "];"
    start_idx = html.find(start_marker)
    if start_idx != -1:
        end_idx = html.find(end_marker, start_idx) + 1
        new_html = html[:start_idx] + f"const horoData = {json.dumps(horo_json, ensure_ascii=False)};" + html[end_idx:]
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(new_html)

def main():
    signs = [("aries","白羊座"), ("taurus","金牛座"), ("gemini","双子座"), ("cancer","巨蟹座"), ("leo","狮子座"), ("virgo","处女座"), ("libra","天秤座"), ("scorpio","天蝎座"), ("sagittarius","射手座"), ("capricorn","摩羯座"), ("aquarius","水瓶座"), ("pisces","双鱼座")]
    
    all_horos = []
    print(f"🚀 开始全自动生成: {datetime.now()}")
    
    for en, cn in signs:
        print(f"正在处理 {cn}...")
        raw = fetch_raw_horoscope(en)
        if raw:
            ai = heal_ify_content(cn, raw)
            if ai:
                all_horos.append({
                    "sign": cn, "icon": get_icon(en), "theme": ai['theme'], "text": ai['short_text'], 
                    "detail": ai['long_analysis'], "career": int(raw['index']['work'].replace('%','')), 
                    "wealth": int(raw['index']['money'].replace('%','')), "health": int(raw['index']['health'].replace('%','')), 
                    "love": int(raw['index']['love'].replace('%','')), 
                    "lucky": {"color": raw['luck']['color'], "number": raw['luck']['number'], "match": raw['luck']['constellation'], "direction": "东南", "item": ai['guide']},
                    "guide": ai['guide'], "forbidden": ai['forbidden']
                })
    
    if all_horos:
        update_index_html(all_horos)
        print("✅ 网站首页已更新今日真实数据")

def get_icon(en):
    icons = {"aries":"♈️","taurus":"♉️","gemini":"♊️","cancer":"♋️","leo":"♌️","virgo":"♍️","libra":"♎️","scorpio":"♏️","sagittarius":"♐️","capricorn":"♑️","aquarius":"♒️","pisces":"♓️"}
    return icons.get(en, "✨")

if __name__ == "__main__":
    main()