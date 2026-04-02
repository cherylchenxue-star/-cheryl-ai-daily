#!/usr/bin/env python3
"""
使用 HTTP API 获取真实股票数据
"""
import os
import json
import urllib.request
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TODAY = datetime.now().strftime('%Y-%m-%d')
TOKEN_FILE = os.path.expanduser("~/.longbridge/openapi/tokens/5b47f58b-526e-4208-a72d-a1fbab4b7bde")

def read_token():
    with open(TOKEN_FILE, 'r') as f:
        data = json.load(f)
        return data.get('access_token')

def fetch_quotes():
    access_token = read_token()
    if not access_token:
        print("No token found")
        return None

    symbols = [
        'IXIC.US', 'HSI.HK', '000001.SH',
        'NVDA.US', 'MSFT.US', 'AAPL.US', 'GOOGL.US', 'AMZN.US', 'META.US', 'TSLA.US',
        '00700.HK', '09988.HK', '03690.HK', '01810.HK',
    ]

    url = "https://openapi.longbridge.cn/quote/get"
    data = json.dumps({"symbol": symbols}).encode('utf-8')

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode()}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def save_data(result):
    if not result or result.get('code') != 0:
        print(f"API Error: {result}")
        return False

    quotes = {q['symbol']: q for q in result.get('data', [])}
    print(f"Got {len(quotes)} quotes")

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

    # Indices
    for s, name, m, f in [('IXIC.US', '纳斯达克', '美股', '🇺🇸'),
                           ('HSI.HK', '恒生指数', '港股', '🇭🇰'),
                           ('000001.SH', '上证指数', 'A股', '🇨🇳')]:
        q = quotes.get(s, {})
        data['indices'].append({
            'symbol': s, 'name': name, 'market': m, 'flag': f,
            'price': round(q.get('last_done', 0), 2),
            'change': round(q.get('change', 0), 2),
            'changePercent': round(q.get('change_rate', 0) * 100, 2),
            'volume': str(int(q.get('volume', 0))) if q.get('volume') else '-',
            '_source': 'real'
        })

    # M7
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

    # HK
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
    return True

if __name__ == '__main__':
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching real stock data...")
    result = fetch_quotes()
    if result:
        save_data(result)
    else:
        print("Failed to fetch data")
