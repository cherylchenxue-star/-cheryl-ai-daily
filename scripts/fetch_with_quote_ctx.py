#!/usr/bin/env python3
"""
直接使用 QuoteContext 获取行情
"""
import os
import json
from datetime import datetime

# 设置环境变量让 SDK 自动读取 token
os.environ['LONGBRIDGE_CLIENT_ID'] = '5b47f58b-526e-4208-a72d-a1fbab4b7bde'

from longbridge.openapi import QuoteContext

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TODAY = datetime.now().strftime('%Y-%m-%d')

def fetch():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching...")

    try:
        # 尝试直接创建 QuoteContext（从环境/token缓存）
        ctx = QuoteContext()

        symbols = ['AAPL.US', '00700.HK']
        print(f"Querying {symbols}...")
        quotes = ctx.quote(symbols)

        print(f"Got {len(quotes)} quotes")
        for q in quotes:
            print(f"  {q.symbol}: {q.last_done}")

        ctx.close()
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    fetch()
