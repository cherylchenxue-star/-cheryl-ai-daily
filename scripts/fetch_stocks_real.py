#!/usr/bin/env python3
"""
使用 Longbridge SDK 获取真实股票数据
"""
import os
import json
from datetime import datetime
from longbridge.openapi import Config, QuoteContext

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TODAY = datetime.now().strftime('%Y-%m-%d')

def fetch():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching real stock data...")

    # 从 token 文件读取
    token_file = os.path.expanduser("~/.longbridge/openapi/tokens/5b47f58b-526e-4208-a72d-a1fbab4b7bde")
    with open(token_file, 'r') as f:
        tokens = json.load(f)

    # 使用 from_apikey 创建 Config (OAuth token 方式)
    config = Config.from_apikey(
        app_key=tokens['client_id'],
        app_secret='',  # OAuth 不需要 secret
        access_token=tokens['access_token'],
        http_url='https://openapi.longbridge.cn'
    )

    ctx = QuoteContext(config)

    # 股票列表
    symbols = [
        'IXIC.US', 'HSI.HK', '000001.SH',
        'NVDA.US', 'MSFT.US', 'AAPL.US', 'GOOGL.US', 'AMZN.US', 'META.US', 'TSLA.US',
        '00700.HK', '09988.HK', '03690.HK', '01810.HK',
    ]

    print(f"Querying {len(symbols)} stocks...")
    quotes = ctx.quote(symbols)

    # 处理数据
    quote_map = {q.symbol: q for q in quotes}
    print(f"Got {len(quote_map)} quotes")

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

    # Fill data
    for s, name, m, f in [('IXIC.US', '纳斯达克', '美股', '🇺🇸'),
                           ('HSI.HK', '恒生指数', '港股', '🇭🇰'),
                           ('000001.SH', '上证指数', 'A股', '🇨🇳')]:
        q = quote_map.get(s)
        if q:
            data['indices'].append({
                'symbol': s, 'name': name, 'market': m, 'flag': f,
                'price': float(q.last_done or 0),
                'change': float(q.change or 0),
                'changePercent': round(float(q.change_rate or 0) * 100, 2),
                '_source': 'real'
            })

    for s, name in [('NVDA.US', '英伟达'), ('MSFT.US', '微软'), ('AAPL.US', '苹果'),
                    ('GOOGL.US', '谷歌'), ('AMZN.US', '亚马逊'), ('META.US', 'Meta'), ('TSLA.US', '特斯拉')]:
        q = quote_map.get(s)
        if q:
            data['m7'].append({
                'symbol': s, 'name': name, 'flag': '🇺🇸',
                'price': float(q.last_done or 0),
                'change': float(q.change or 0),
                'changePercent': round(float(q.change_rate or 0) * 100, 2),
                '_source': 'real'
            })

    for s, name in [('00700.HK', '腾讯'), ('09988.HK', '阿里'),
                    ('03690.HK', '美团'), ('01810.HK', '小米')]:
        q = quote_map.get(s)
        if q:
            data['hkStocks'].append({
                'symbol': s, 'name': name, 'flag': '🇭🇰',
                'price': float(q.last_done or 0),
                'change': float(q.change or 0),
                'changePercent': round(float(q.change_rate or 0) * 100, 2),
                '_source': 'real'
            })

    # Save
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f'stocks-{TODAY}.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved to {filepath}")

    # Show sample
    print("\nStock prices:")
    for idx in data['indices']:
        print(f"  {idx['name']}: {idx['price']} ({idx['changePercent']:+.2f}%)")

    ctx.close()

if __name__ == '__main__':
    fetch()
