#!/usr/bin/env python3
"""
使用 Longbridge SDK 获取真实股票数据
自动使用 OpenClaw 已授权的 Token
"""
import os
import json
from datetime import datetime
from longbridge.openapi import Config, QuoteContext

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TODAY = datetime.now().strftime('%Y-%m-%d')

def fetch_stock_data():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching real stock data...")

    # 使用已有的 OAuth token (OpenClaw 已授权)
    # SDK 会自动从 ~/.longbridge/openapi/tokens/ 读取
    try:
        # 尝试不传入任何参数，让 SDK 自动从缓存读取
        # 读取 token 文件中的 client_id
        import glob
        token_files = glob.glob(os.path.expanduser("~/.longbridge/openapi/tokens/*"))
        if not token_files:
            raise Exception("No token file found")

        with open(token_files[0], 'r') as f:
            token_data = json.load(f)
            client_id = token_data.get('client_id')
            access_token = token_data.get('access_token')

        # 使用 API Key + Access Token 创建配置
        config = Config.from_apikey(client_id, '', access_token)
        ctx = QuoteContext(config)

        # 股票列表
        symbols = [
            'IXIC.US', 'HSI.HK', '000001.SH',  # 指数
            'NVDA.US', 'MSFT.US', 'AAPL.US', 'GOOGL.US', 'AMZN.US', 'META.US', 'TSLA.US',  # M7
            '00700.HK', '09988.HK', '03690.HK', '01810.HK',  # 港股
        ]

        print(f"Querying {len(symbols)} stocks...")
        quotes = ctx.quote(symbols)

        # 构建数据
        quote_map = {q.symbol: q for q in quotes}

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

        # 处理指数
        for s, name, m, f in [('IXIC.US', '纳斯达克', '美股', '🇺🇸'),
                               ('HSI.HK', '恒生指数', '港股', '🇭🇰'),
                               ('000001.SH', '上证指数', 'A股', '🇨🇳')]:
            q = quote_map.get(s)
            if q:
                data['indices'].append({
                    'symbol': s, 'name': name, 'market': m, 'flag': f,
                    'price': float(q.last_done) if q.last_done else 0,
                    'change': float(q.change) if q.change else 0,
                    'changePercent': round(float(q.change_rate) * 100, 2) if q.change_rate else 0,
                    'volume': str(int(q.volume)) if q.volume else '-',
                    '_source': 'real'
                })

        # 处理 M7
        for s, name in [('NVDA.US', '英伟达'), ('MSFT.US', '微软'), ('AAPL.US', '苹果'),
                        ('GOOGL.US', '谷歌'), ('AMZN.US', '亚马逊'), ('META.US', 'Meta'), ('TSLA.US', '特斯拉')]:
            q = quote_map.get(s)
            if q:
                data['m7'].append({
                    'symbol': s, 'name': name, 'flag': '🇺🇸',
                    'price': float(q.last_done) if q.last_done else 0,
                    'change': float(q.change) if q.change else 0,
                    'changePercent': round(float(q.change_rate) * 100, 2) if q.change_rate else 0,
                    'marketCap': '-',
                    '_source': 'real'
                })

        # 处理港股
        for s, name in [('00700.HK', '腾讯'), ('09988.HK', '阿里'),
                        ('03690.HK', '美团'), ('01810.HK', '小米')]:
            q = quote_map.get(s)
            if q:
                data['hkStocks'].append({
                    'symbol': s, 'name': name, 'flag': '🇭🇰',
                    'price': float(q.last_done) if q.last_done else 0,
                    'change': float(q.change) if q.change else 0,
                    'changePercent': round(float(q.change_rate) * 100, 2) if q.change_rate else 0,
                    'marketCap': '-',
                    '_source': 'real'
                })

        ctx.close()

        # 保存
        os.makedirs(DATA_DIR, exist_ok=True)
        filepath = os.path.join(DATA_DIR, f'stocks-{TODAY}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ Saved {len(quote_map)} real quotes to {filepath}")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    fetch_stock_data()
