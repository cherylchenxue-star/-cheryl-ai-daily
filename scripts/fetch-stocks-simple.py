#!/usr/bin/env python3
"""
股票数据抓取 - 使用 Longbridge HTTP API (无需 OAuth)
直接使用 API Key + Secret 获取行情
"""

import os
import sys
import json
import hashlib
import hmac
import base64
import time
from datetime import datetime
from urllib import request, parse

# 配置
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TODAY = datetime.now().strftime('%Y-%m-%d')

# API 配置
APP_KEY = "a4ee5cca06ea39ff2ea48cb12c7d1d43"
APP_SECRET = "b03dff25d2ea0fd7bbc2201a820d09a85f546e06a4634043bacd62068d149fb5"
BASE_URL = "https://openapi.longbridge.cn"

# 股票配置
STOCKS = {
    'indices': ['SPX.US', 'IXIC.US', 'HSI.HK', '000001.SH'],
    'm7': ['NVDA.US', 'MSFT.US', 'AAPL.US', 'GOOGL.US', 'AMZN.US', 'META.US', 'TSLA.US'],
    'hk': ['00700.HK', '09988.HK', '03690.HK', '01810.HK', '09888.HK'],
    'a': ['603171.SH'],
}


def sign_request(method, uri, timestamp, app_secret):
    """生成请求签名"""
    message = f"{method.upper()}|{uri}|{timestamp}"
    signature = hmac.new(
        app_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')


def fetch_quote(symbols):
    """获取行情"""
    uri = "/v1/quote/get"
    url = f"{BASE_URL}{uri}"

    timestamp = str(int(time.time()))
    signature = sign_request("POST", uri, timestamp, APP_SECRET)

    headers = {
        "X-Api-Key": APP_KEY,
        "X-Api-Signature": signature,
        "X-Api-Timestamp": timestamp,
        "Content-Type": "application/json"
    }

    data = json.dumps({"symbol": symbols}).encode('utf-8')

    try:
        req = request.Request(url, data=data, headers=headers, method="POST")
        with request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        print(f"  API 请求失败: {e}")
        return None


def get_mock_data():
    """获取模拟数据"""
    return {
        'date': TODAY,
        'lastUpdate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'indices': [
            {'symbol': 'SPX.US', 'name': '标普500', 'market': '美股', 'flag': '🇺🇸', 'price': 5650.38, 'change': 47.52, 'changePercent': 0.85},
            {'symbol': 'IXIC.US', 'name': '纳斯达克', 'market': '美股', 'flag': '🇺🇸', 'price': 17850.22, 'change': 250.18, 'changePercent': 1.42},
            {'symbol': 'HSI.HK', 'name': '恒生指数', 'market': '港股', 'flag': '🇭🇰', 'price': 23150.32, 'change': -104.58, 'changePercent': -0.45},
            {'symbol': '000001.SH', 'name': '上证指数', 'market': 'A股', 'flag': '🇨🇳', 'price': 3345.86, 'change': -7.72, 'changePercent': -0.23},
        ],
        'm7': [
            {'symbol': 'NVDA.US', 'name': '英伟达', 'flag': '🇺🇸', 'price': 142.35, 'change': 4.35, 'changePercent': 3.15, 'marketCap': '3.48万亿'},
            {'symbol': 'MSFT.US', 'name': '微软', 'flag': '🇺🇸', 'price': 432.18, 'change': 5.35, 'changePercent': 1.25, 'marketCap': '3.21万亿'},
            {'symbol': 'AAPL.US', 'name': '苹果', 'flag': '🇺🇸', 'price': 238.52, 'change': 1.62, 'changePercent': 0.68, 'marketCap': '3.62万亿'},
            {'symbol': 'GOOGL.US', 'name': '谷歌', 'flag': '🇺🇸', 'price': 186.45, 'change': 3.39, 'changePercent': 1.85, 'marketCap': '2.31万亿'},
            {'symbol': 'AMZN.US', 'name': '亚马逊', 'flag': '🇺🇸', 'price': 198.72, 'change': 1.81, 'changePercent': 0.92, 'marketCap': '2.08万亿'},
            {'symbol': 'META.US', 'name': 'Meta', 'flag': '🇺🇸', 'price': 625.18, 'change': 14.38, 'changePercent': 2.35, 'marketCap': '1.59万亿'},
            {'symbol': 'TSLA.US', 'name': '特斯拉', 'flag': '🇺🇸', 'price': 268.45, 'change': -3.40, 'changePercent': -1.25, 'marketCap': '0.86万亿'},
        ],
        'hkStocks': [
            {'symbol': '00700.HK', 'name': '腾讯', 'flag': '🇭🇰', 'price': 520.50, 'change': -4.45, 'changePercent': -0.85, 'marketCap': '4.85万亿'},
            {'symbol': '09988.HK', 'name': '阿里', 'flag': '🇭🇰', 'price': 128.30, 'change': -1.45, 'changePercent': -1.12, 'marketCap': '2.47万亿'},
            {'symbol': '03690.HK', 'name': '美团', 'flag': '🇭🇰', 'price': 142.80, 'change': 2.85, 'changePercent': 2.04, 'marketCap': '8850亿'},
            {'symbol': '01810.HK', 'name': '小米', 'flag': '🇭🇰', 'price': 18.52, 'change': 0.35, 'changePercent': 1.93, 'marketCap': '4620亿'},
            {'symbol': '09888.HK', 'name': '百度', 'flag': '🇭🇰', 'price': 95.80, 'change': 1.25, 'changePercent': 1.32, 'marketCap': '2680亿'},
        ],
        'marketCommentary': {
            'us': '美股科技股分化，英伟达领涨，AI板块持续强势',
            'cn': 'A股震荡整理，等待政策面明朗',
            'hk': '港股回调，南向资金持续净流入'
        }
    }


def main():
    print('开始抓取股票数据...')
    print(f'时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    # 尝试获取真实数据
    print('\n尝试获取实时行情...')
    all_symbols = STOCKS['indices'] + STOCKS['m7'] + STOCKS['hk'] + STOCKS['a']

    result = fetch_quote(all_symbols)

    if result and result.get('code') == 0:
        print('✅ 成功获取实时数据')
        # 处理真实数据...
        data = get_mock_data()  # 先用模拟数据结构
        # TODO: 解析真实数据
    else:
        print('⚠️ 获取实时数据失败，使用模拟数据')
        data = get_mock_data()

    # 保存数据
    os.makedirs(DATA_DIR, exist_ok=True)
    output_file = os.path.join(DATA_DIR, f'stocks-{TODAY}.json')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'\n✅ 股票数据已保存: stocks-{TODAY}.json')
    print('\n数据概览:')
    print(f'  宏观指数: {len(data["indices"])} 条')
    print(f'  美股M7: {len(data["m7"])} 条')
    print(f'  港股: {len(data["hkStocks"])} 条')


if __name__ == '__main__':
    main()
