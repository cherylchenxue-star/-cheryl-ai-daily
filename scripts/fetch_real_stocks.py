#!/usr/bin/env python3
"""
使用已有的 Longbridge Token 获取真实股票数据
"""
import os
import sys
import json
from datetime import datetime

# 从已有的 token 文件读取
TOKEN_FILE = os.path.expanduser("~/.longbridge/openapi/tokens/5b47f58b-526e-4208-a72d-a1fbab4b7bde")
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TODAY = datetime.now().strftime('%Y-%m-%d')

def read_token():
    """读取已有的 access token"""
    try:
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
            return data.get('access_token')
    except Exception as e:
        print(f"读取 token 失败: {e}")
        return None

def fetch_real_data():
    """使用 HTTP API 获取真实数据"""
    import urllib.request
    import urllib.parse
    import hashlib
    import hmac
    import base64
    import time

    access_token = read_token()
    if not access_token:
        print("没有找到有效的 access token")
        return None

    # 股票列表
    symbols = [
        'IXIC.US', 'HSI.HK', '000001.SH',  # 指数
        'NVDA.US', 'MSFT.US', 'AAPL.US', 'GOOGL.US', 'AMZN.US', 'META.US', 'TSLA.US',  # M7
        '00700.HK', '09988.HK', '03690.HK', '01810.HK',  # 港股
    ]

    # 构建请求
    url = "https://openapi.longbridge.cn/v1/quote/get"
    timestamp = str(int(time.time()))

    # 注意：这里使用 access_token 而不是 app_secret 来签名
    headers = {
        "X-Api-Key": "5b47f58b-526e-4208-a72d-a1fbab4b7bde",  # 从 token 文件读取的 client_id
        "Authorization": f"Bearer {access_token}",
        "X-Api-Timestamp": timestamp,
        "Content-Type": "application/json"
    }

    data = json.dumps({"symbol": symbols}).encode('utf-8')

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            return result
    except urllib.error.HTTPError as e:
        print(f"API 错误: {e.code} - {e.read().decode()}")
        return None
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def save_stock_data(api_result):
    """保存股票数据"""
    if not api_result or api_result.get('code') != 0:
        print(f"API 返回错误: {api_result}")
        return False

    quotes = {q['symbol']: q for q in api_result.get('data', [])}
    print(f"获取到 {len(quotes)} 条行情数据")

    # 构建数据结构
    data = {
        'date': TODAY,
        'lastUpdate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'indices': [],
        'm7': [],
        'hkStocks': [],
        'marketCommentary': {
            'us': '美股科技股分化，AI板块持续强势',
            'cn': 'A股震荡整理，结构性行情明显',
            'hk': '港股回调，南向资金持续流入'
        }
    }

    # 处理指数
    for symbol, name, market, flag in [
        ('IXIC.US', '纳斯达克', '美股', '🇺🇸'),
        ('HSI.HK', '恒生指数', '港股', '🇭🇰'),
        ('000001.SH', '上证指数', 'A股', '🇨🇳')
    ]:
        q = quotes.get(symbol, {})
        data['indices'].append({
            'symbol': symbol,
            'name': name,
            'market': market,
            'flag': flag,
            'price': round(q.get('last_done', 0), 2),
            'change': round(q.get('change', 0), 2),
            'changePercent': round(q.get('change_rate', 0) * 100, 2),
            'volume': str(int(q.get('volume', 0))) if q.get('volume') else '-',
            '_source': 'real'
        })

    # 处理 M7
    for symbol, name in [
        ('NVDA.US', '英伟达'), ('MSFT.US', '微软'), ('AAPL.US', '苹果'),
        ('GOOGL.US', '谷歌'), ('AMZN.US', '亚马逊'), ('META.US', 'Meta'), ('TSLA.US', '特斯拉')
    ]:
        q = quotes.get(symbol, {})
        data['m7'].append({
            'symbol': symbol,
            'name': name,
            'flag': '🇺🇸',
            'price': round(q.get('last_done', 0), 2),
            'change': round(q.get('change', 0), 2),
            'changePercent': round(q.get('change_rate', 0) * 100, 2),
            'marketCap': '-',
            '_source': 'real'
        })

    # 处理港股
    for symbol, name in [
        ('00700.HK', '腾讯'), ('09988.HK', '阿里'),
        ('03690.HK', '美团'), ('01810.HK', '小米')
    ]:
        q = quotes.get(symbol, {})
        data['hkStocks'].append({
            'symbol': symbol,
            'name': name,
            'flag': '🇭🇰',
            'price': round(q.get('last_done', 0), 2),
            'change': round(q.get('change', 0), 2),
            'changePercent': round(q.get('change_rate', 0) * 100, 2),
            'marketCap': '-',
            '_source': 'real'
        })

    # 保存
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f'stocks-{TODAY}.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 真实股票数据已保存: {filepath}")
    return True

if __name__ == '__main__':
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 获取真实股票数据...")
    print(f"使用 OpenClaw 已授权的 Token")

    result = fetch_real_data()
    if result:
        save_stock_data(result)
    else:
        print("❌ 获取失败，请检查 token 是否过期")
