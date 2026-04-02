#!/usr/bin/env python3
"""
使用 Longbridge SDK HttpClient 获取真实股票数据
"""
import os
import json
from datetime import datetime
from longbridge.openapi import HttpClient

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TODAY = datetime.now().strftime('%Y-%m-%d')
TOKEN_FILE = os.path.expanduser("~/.longbridge/openapi/tokens/5b47f58b-526e-4208-a72d-a1fbab4b7bde")

def read_tokens():
    with open(TOKEN_FILE, 'r') as f:
        return json.load(f)

def fetch_with_sdk_http():
    tokens = read_tokens()
    client_id = tokens['client_id']
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']

    # 创建 HttpClient
    http = HttpClient.from_apikey(client_id, '', access_token)

    symbols = [
        'IXIC.US', 'HSI.HK', '000001.SH',
        'NVDA.US', 'MSFT.US', 'AAPL.US', 'GOOGL.US', 'AMZN.US', 'META.US', 'TSLA.US',
        '00700.HK', '09988.HK', '03690.HK', '01810.HK',
    ]

    try:
        # 使用 SDK 的请求方法
        # Try different API paths
        for path in ["/v1/quote/get", "/quote/get", "/v1/quote", "/quote"]:
            try:
                print(f"Trying {path}...")
                result = http.request("post", path, body={"symbol": symbols})
                print(f"Success with {path}")
                return result
            except Exception as e:
                print(f"  Failed: {e}")
                continue
        return None
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

def save_data(result):
    if not result or result.get('code') != 0:
        print(f"API Error: {result}")
        return False

    quotes = {q['symbol']: q for q in result.get('data', [])}
    print(f"Got {len(quotes)} real quotes")

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

    # Print sample data
    print("\nSample data:")
    for idx in data['indices']:
        print(f"  {idx['name']}: {idx['price']} ({idx['changePercent']:+.2f}%)")

    return True

if __name__ == '__main__':
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching real stock data...")
    result = fetch_with_sdk_http()
    if result:
        save_data(result)
    else:
        print("Failed")
