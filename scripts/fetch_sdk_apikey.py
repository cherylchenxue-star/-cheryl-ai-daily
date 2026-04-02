#!/usr/bin/env python3
"""
使用 SDK + API Key 获取行情
"""
import os
import json
from datetime import datetime
from longbridge.openapi import Config, QuoteContext

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TODAY = datetime.now().strftime('%Y-%m-%d')

APP_KEY = "a4ee5cca06ea39ff2ea48cb12c7d1d43"
APP_SECRET = "b03dff25d2ea0fd7bbc2201a820d09a85f546e06a4634043bacd62068d149fb5"

def fetch():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching with SDK...")

    # 使用 API Key 创建 Config (不传 access_token，让 SDK 自动处理)
    config = Config.from_apikey(
        app_key=APP_KEY,
        app_secret=APP_SECRET,
        access_token="",  # 空字符串
        http_url='https://openapi.longbridge.cn'
    )

    ctx = QuoteContext(config)

    symbols = ['AAPL.US', '00700.HK']
    print(f"Querying {symbols}...")

    try:
        quotes = ctx.quote(symbols)
        print(f"Got {len(quotes)} quotes")
        for q in quotes:
            print(f"  {q.symbol}: {q.last_done}")
    except Exception as e:
        print(f"Error: {e}")

    ctx.close()

if __name__ == '__main__':
    fetch()
