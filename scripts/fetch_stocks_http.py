#!/usr/bin/env python3
"""
直接使用 HTTP 请求获取 Longbridge 行情
使用 Bearer Token 认证 (OAuth)
"""
import os
import json
import urllib.request
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TODAY = datetime.now().strftime('%Y-%m-%d')
TOKEN_FILE = os.path.expanduser("~/.longbridge/openapi/tokens/5b47f58b-526e-4208-a72d-a1fbab4b7bde")

def get_token():
    with open(TOKEN_FILE, 'r') as f:
        return json.load(f)['access_token']

def fetch():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching...")

    token = get_token()
    symbols = [
        'IXIC.US', 'HSI.HK', '000001.SH',
        'NVDA.US', 'MSFT.US', 'AAPL.US', 'GOOGL.US', 'AMZN.US', 'META.US', 'TSLA.US',
        '00700.HK', '09988.HK', '03690.HK', '01810.HK',
    ]

    # 长桥行情订阅/查询接口
    url = "https://openapi-quote.longbridge.com/v2/quote/subscribe"

    req_data = json.dumps({
        "symbol": symbols,
        "sub_type": ["QUOTE"],
        "is_first_push": True
    }).encode()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            print(f"Response: {json.dumps(result, indent=2)[:500]}")
            return result
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == '__main__':
    fetch()
