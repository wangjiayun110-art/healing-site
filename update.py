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
        res = requests.get(url, timeout=15)
        data = res.json()
        if data.get('success'):
            return data['data']
    except Exception as e:
        print(f"Fetch {sign_en} failed: {e}")
    return None

def deep_heal_ify(sign_cn, raw):
    """调用 AI 进行深度长文本创作"""
    if not DEEPSEEK_API_KEY:
        return None

    prompt = f"""
    你是一位极具洞察力、文笔优美、温暖人心的深度占星师。请根据以下原始运势数据，为【{sign_cn}】撰写今日的深度百科解析。
    
    原始数据：{json.dumps(raw, ensure_ascii=False)}
    
    请严格按照以下 JSON 格式输出，内容要极其详尽、文艺、富有治愈力（总字数约 500 字）：
    {{
        "theme": "4字治愈主题",
        "today_analysis": "150字左右的今日星象详述，语气要温柔，像在耳边呢喃。",
        "yearly_analysis": "200字左右的 2026 年度宏观能量展望，关注长期的重塑与成长。",
        "details": {{
            "love": "50字左右的今日情感磁场深度流向分析。",
            "career": "50字左右的今日事业进阶与行动建议。",
            "wealth": "50字左右的今日财富吸附与消费提醒。"
        }},
        "lucky": {{
            "color": "{raw['luck']['color']}",
            "number": "{raw['luck']['number']}",
            "match": "{raw['luck']['constellation']}",
            "item": "由你建议的一个极具美感的开运小物"
        }}
    }}
    """
    
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat", 
        "messages": [{"role": "user", "content": prompt}], 
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(f"{DEEPSEEK_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=60)
        return json.loads(response.json()['choices'][0]['message']['content'])
    except Exception as e:
        print(f"AI Deep Creation for {sign_cn} failed: {e}")
        return None

def update_index_html(horo_json):
    """将数据精准注入 HTML 模板"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()
        
        # 查找数据区域
        start_marker = "const db ="
        end_marker = "];"
        start_idx = html.find(start_marker)
        if start_idx != -1:
            end_idx = html.find(end_marker, start_idx) + 1
            new_data_str = f"const db = {json.dumps(horo_json, ensure_ascii=False)};"
            new_html = html[:start_idx] + new_data_str + html[end_idx:]
            
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(new_html)
            return True
    except Exception as e:
        print(f"Update HTML failed: {e}")
    return False

def main():
    signs = [("aries","白羊座"), ("taurus","金牛座"), ("gemini","双子座"), ("cancer","巨蟹座"), ("leo","狮子座"), ("virgo","处女座"), ("libra","天秤座"), ("scorpio","天蝎座"), ("sagittarius","射手座"), ("capricorn","摩羯座"), ("aquarius","水瓶座"), ("pisces","双鱼座")]
    
    all_deep_horos = []
    print(f"🚀 启动深度内容工厂: {datetime.now()}")
    
    for en, cn in signs:
        print(f"🔮 正在为 {cn} 进行深度创作...")
        raw = fetch_raw_horoscope(en)
        if raw:
            ai = deep_heal_ify(cn, raw)
            if ai:
                all_deep_horos.append({
                    "sign": cn, 
                    "icon": get_icon(en), 
                    "theme": ai['theme'],
                    "today_analysis": ai['today_analysis'],
                    "yearly_analysis": ai['yearly_analysis'],
                    "details": ai['details'],
                    "lucky": ai['lucky']
                })
        
    if all_deep_horos:
        if update_index_html(all_deep_horos):
            print(f"✅ 全站深度内容已更新。总计 {len(all_deep_horos)} 个星座已就绪。")
        else:
            print("❌ 写入 HTML 失败。")
    else:
        print("❌ 未能生成任何深度内容。")

def get_icon(en):
    icons = {"aries":"♈️","taurus":"♉️","gemini":"♊️","cancer":"♋️","leo":"♌️","virgo":"♍️","libra":"♎️","scorpio":"♏️","sagittarius":"♐️","capricorn":"♑️","aquarius":"♒️","pisces":"♓️"}
    return icons.get(en, "✨")

if __name__ == "__main__":
    main()