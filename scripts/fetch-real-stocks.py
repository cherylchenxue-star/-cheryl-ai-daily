#!/usr/bin/env python3
"""
使用 Longbridge Python SDK 获取真实股票数据
"""
import os
import sys
import json
from datetime import datetime

# 添加项目目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from longbridge.openapi import Config, HttpClient, QuoteContext

# API 凭证
APP_KEY = "a4ee5cca06ea39ff2ea48cb12c7d1d43"
APP_SECRET = "b03dff25d2ea0fd7bbc2201a820d09a85f546e06a4634043bacd62068d149fb5"

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TODAY = datetime.now().strftime('%Y-%m-%d')

# 股票配置
STOCK_CONFIG = {
    'indices': [
        {'symbol': 'IXIC.US', 'name': '纳斯达克', 'market': '美股', 'flag': '🇺🇸'},
        {'symbol': 'HSI.HK', 'name': '恒生指数', 'market': '港股', 'flag': '🇭🇰'},
        {'symbol': '000001.SH', 'name': '上证指数', 'market': 'A股', 'flag': '🇨🇳'},
    ],
    'm7': [
        {'symbol': 'NVDA.US', 'name': '英伟达', 'flag': '🇺🇸'},
        {'symbol': 'MSFT.US', 'name': '微软', 'flag': '🇺🇸'},
        {'symbol': 'AAPL.US', 'name': '苹果', 'flag': '🇺🇸'},
        {'symbol': 'GOOGL.US', 'name': '谷歌', 'flag': '🇺🇸'},
        {'symbol': 'AMZN.US', 'name': '亚马逊', 'flag': '🇺🇸'},
        {'symbol': 'META.US', 'name': 'Meta', 'flag': '🇺🇸'},
        {'symbol': 'TSLA.US', 'name': '特斯拉', 'flag': '🇺🇸'},
    ],
    'hkStocks': [
        {'symbol': '00700.HK', 'name': '腾讯', 'flag': '🇭🇰'},
        {'symbol': '09988.HK', 'name': '阿里', 'flag': '🇭🇰'},
        {'symbol': '03690.HK', 'name': '美团', 'flag': '🇭🇰'},
        {'symbol': '01810.HK', 'name': '小米', 'flag': '🇭🇰'},
    ],
}


def format_number(value, decimals=2):
    """格式化数字"""
    if value is None:
        return 0
    return round(float(value), decimals)


def fetch_quotes_direct():
    """使用 HTTP API 直接获取行情"""
    import urllib.request
    import urllib.parse
    import hashlib
    import hmac
    import base64
    import time

    base_url = "https://openapi.longbridge.cn"
    timestamp = str(int(time.time()))

    # 生成签名
    message = f"POST|/v1/quote/get|{timestamp}"
    signature = hmac.new(
        APP_SECRET.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    signature_b64 = base64.b64encode(signature).decode('utf-8')

    headers = {
        "X-Api-Key": APP_KEY,
        "X-Api-Signature": signature_b64,
        "X-Api-Timestamp": timestamp,
        "Content-Type": "application/json"
    }

    # 获取所有股票
    all_symbols = []
    for category in STOCK_CONFIG.values():
        all_symbols.extend([s['symbol'] for s in category])

    data = json.dumps({"symbol": all_symbols}).encode('utf-8')

    try:
        req = urllib.request.Request(
            f"{base_url}/v1/quote/get",
            data=data,
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        print(f"API 请求失败: {e}")
        return None


def fetch_stock_data():
    """抓取股票数据"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始获取股票数据...")

    # 尝试获取真实数据
    result = fetch_quotes_direct()

    stock_data = {
        'date': TODAY,
        'lastUpdate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'indices': [],
        'm7': [],
        'hkStocks': [],
        'aStocks': [],
        'usPeers': [],
        'marketCommentary': {
            'us': '美股科技股分化，AI板块持续强势',
            'cn': 'A股震荡整理，等待政策面明朗',
            'hk': '港股回调，南向资金持续净流入'
        }
    }

    # 处理真实数据
    if result and result.get('code') == 0 and result.get('data'):
        quotes = {q['symbol']: q for q in result['data']}
        print(f"✅ 成功获取 {len(quotes)} 条行情数据")

        # 处理各类股票
        for category, stocks in STOCK_CONFIG.items():
            for stock in stocks:
                symbol = stock['symbol']
                quote = quotes.get(symbol, {})

                if quote:
                    stock_data[category].append({
                        **stock,
                        'price': format_number(quote.get('last_done') or quote.get('price')),
                        'change': format_number(quote.get('change')),
                        'changePercent': format_number(quote.get('change_rate', 0) * 100),
                        'volume': str(int(quote.get('volume', 0))) if quote.get('volume') else '-',
                        'open': format_number(quote.get('open')),
                        'high': format_number(quote.get('high')),
                        'low': format_number(quote.get('low')),
                        'prevClose': format_number(quote.get('prev_close')),
                        '_source': 'real'
                    })
                else:
                    print(f"⚠️ 未获取到 {symbol} 的数据，使用模拟值")
                    stock_data[category].append(get_mock_data(stock))
    else:
        print("⚠️ API 调用失败，使用模拟数据")
        # 使用模拟数据
        for category, stocks in STOCK_CONFIG.items():
            for stock in stocks:
                stock_data[category].append(get_mock_data(stock))

    # 保存数据
    os.makedirs(DATA_DIR, exist_ok=True)
    output_file = os.path.join(DATA_DIR, f'stocks-{TODAY}.json')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stock_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 数据已保存: {output_file}")
    return stock_data


def get_mock_data(stock):
    """获取模拟数据"""
    mock_values = {
        'IXIC.US': {'price': 17850.22, 'change': 250.18, 'changePercent': 1.42},
        'HSI.HK': {'price': 23150.32, 'change': -104.58, 'changePercent': -0.45},
        '000001.SH': {'price': 3345.86, 'change': -7.72, 'changePercent': -0.23},
        'NVDA.US': {'price': 142.35, 'change': 4.35, 'changePercent': 3.15},
        'MSFT.US': {'price': 432.18, 'change': 5.35, 'changePercent': 1.25},
        'AAPL.US': {'price': 238.52, 'change': 1.62, 'changePercent': 0.68},
        'GOOGL.US': {'price': 186.45, 'change': 3.39, 'changePercent': 1.85},
        'AMZN.US': {'price': 198.72, 'change': 1.81, 'changePercent': 0.92},
        'META.US': {'price': 625.18, 'change': 14.38, 'changePercent': 2.35},
        'TSLA.US': {'price': 268.45, 'change': -3.40, 'changePercent': -1.25},
        '00700.HK': {'price': 520.50, 'change': -4.45, 'changePercent': -0.85},
        '09988.HK': {'price': 128.30, 'change': -1.45, 'changePercent': -1.12},
        '03690.HK': {'price': 142.80, 'change': 2.85, 'changePercent': 2.04},
        '01810.HK': {'price': 18.52, 'change': 0.35, 'changePercent': 1.93},
    }

    symbol = stock['symbol']
    mock = mock_values.get(symbol, {'price': 100, 'change': 0, 'changePercent': 0})

    return {
        **stock,
        **mock,
        'volume': '-',
        '_source': 'mock'
    }


if __name__ == '__main__':
    fetch_stock_data()
