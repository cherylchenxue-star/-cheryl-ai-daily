#!/usr/bin/env python3
"""
使用 API Key 方式获取 Longbridge 行情
"""
import os
import json
import urllib.request
import hashlib
import hmac
import base64
import time
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TODAY = datetime.now().strftime('%Y-%m-%d')

# 你的 API Key 和 Secret
APP_KEY = "a4ee5cca06ea39ff2ea48cb12c7d1d43"
APP_SECRET = "b03dff25d2ea0fd7bbc2201a820d09a85f546e06a4634043bacd62068d149fb5"

def sign(method, uri, timestamp, secret):
    """生成签名"""
    message = f"{method.upper()}|{uri}|{timestamp}"
    sig = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
    return base64.b64encode(sig).decode()

def fetch():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching with API Key...")

    symbols = [
        'IXIC.US', 'HSI.HK', '000001.SH',
        'NVDA.US', 'MSFT.US', 'AAPL.US', 'GOOGL.US', 'AMZN.US', 'META.US', 'TSLA.US',
        '00700.HK', '09988.HK', '03690.HK', '01810.HK',
    ]

    # 使用行情查询接口
    uri = "/v1/quote/get"
    url = f"https://openapi.longbridge.cn{uri}"
    timestamp = str(int(time.time()))

    headers = {
        "X-Api-Key": APP_KEY,
        "X-Api-Signature": sign("POST", uri, timestamp, APP_SECRET),
        "X-Api-Timestamp": timestamp,
        "Content-Type": "application/json"
    }

    data = json.dumps({"symbol": symbols}).encode()

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())

            if result.get('code') == 0:
                print(f"Success! Got {len(result.get('data', []))} quotes")
                save_data(result)
                return True
            else:
                print(f"API Error: {result}")
                return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def save_data(result):
    quotes = {q['symbol']: q for q in result.get('data', [])}

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

    for s, name, m, f in [('IXIC.US', '纳斯达克', '美股', '🇺🇸'),
                           ('HSI.HK', '恒生指数', '港股', '🇭🇰'),
                           ('000001.SH', '上证指数', 'A股', '🇨🇳')]:
        q = quotes.get(s, {})
        data['indices'].append({
            'symbol': s, 'name': name, 'market': m, 'flag': f,
            'price': round(q.get('last_done', 0), 2),
            'change': round(q.get('change', 0), 2),
            'changePercent': round(q.get('change_rate', 0) * 100, 2),
            '_source': 'real'
        })

    for s, name in [('NVDA.US', '英伟达'), ('MSFT.US', '微软'), ('AAPL.US', '苹果'),
                    ('GOOGL.US', '谷歌'), ('AMZN.US', '亚马逊'), ('META.US', 'Meta'), ('TSLA.US', '特斯拉')]:
        q = quotes.get(s, {})
        data['m7'].append({
            'symbol': s, 'name': name, 'flag': '🇺🇸',
            'price': round(q.get('last_done', 0), 2),
            'change': round(q.get('change', 0), 2),
            'changePercent': round(q.get('change_rate', 0) * 100, 2),
            '_source': 'real'
        })

    for s, name in [('00700.HK', '腾讯'), ('09988.HK', '阿里'),
                    ('03690.HK', '美团'), ('01810.HK', '小米')]:
        q = quotes.get(s, {})
        data['hkStocks'].append({
            'symbol': s, 'name': name, 'flag': '🇭🇰',
            'price': round(q.get('last_done', 0), 2),
            'change': round(q.get('change', 0), 2),
            'changePercent': round(q.get('change_rate', 0) * 100, 2),
            '_source': 'real'
        })

    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f'stocks-{TODAY}.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved to {filepath}")

    # Show prices
    print("\nPrices:")
    for idx in data['indices']:
        print(f"  {idx['name']}: {idx['price']} ({idx['changePercent']:+.2f}%)")

if __name__ == '__main__':
    fetch()
