#!/usr/bin/env python3
"""
Fetch stock data using Longbridge SDK or mock data
"""
import os
import sys
import json
from datetime import datetime

APP_KEY = "a4ee5cca06ea39ff2ea48cb12c7d1d43"
APP_SECRET = "b03dff25d2ea0fd7bbc2201a820d09a85f546e06a4634043bacd62068d149fb5"
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TODAY = datetime.now().strftime('%Y-%m-%d')

def generate_mock_data():
    """Generate realistic mock stock data"""
    data = {
        'date': TODAY,
        'lastUpdate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'indices': [
            {'symbol': 'IXIC.US', 'name': '纳斯达克', 'market': '美股', 'flag': '🇺🇸', 'price': 17850.22, 'change': 250.18, 'changePercent': 1.42, 'volume': '45.2亿'},
            {'symbol': 'HSI.HK', 'name': '恒生指数', 'market': '港股', 'flag': '🇭🇰', 'price': 23150.32, 'change': -104.58, 'changePercent': -0.45, 'volume': '1250亿'},
            {'symbol': '000001.SH', 'name': '上证指数', 'market': 'A股', 'flag': '🇨🇳', 'price': 3345.86, 'change': -7.72, 'changePercent': -0.23, 'volume': '2850亿'},
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
        ],
        'marketCommentary': {
            'us': 'M7多数上涨，AI板块持续强势',
            'cn': 'A股震荡整理，结构性行情明显',
            'hk': '港股回调，南向资金持续流入'
        }
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f'stocks-{TODAY}.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Mock data saved: {filepath}")
    return data

if __name__ == '__main__':
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Generating stock data...")
    generate_mock_data()
    print("Done!")
