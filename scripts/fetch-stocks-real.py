#!/usr/bin/env python3
"""
股票数据抓取脚本 - 使用 Longbridge Python SDK
获取真实行情数据
"""

import os
import sys
import json
from datetime import datetime, timedelta
from longbridge.openapi import Config, QuoteContext, Market, SubType

# 配置
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TODAY = datetime.now().strftime('%Y-%m-%d')

# API 配置 (从环境变量或直接使用)
APP_KEY = os.getenv('LONGBRIDGE_APP_KEY', 'a4ee5cca06ea39ff2ea48cb12c7d1d43')
APP_SECRET = os.getenv('LONGBRIDGE_APP_SECRET', 'b03dff25d2ea0fd7bbc2201a820d09a85f546e06a4634043bacd62068d149fb5')

# 股票代码配置
STOCK_CONFIG = {
    # 宏观指数
    'indices': [
        {'symbol': 'SPX.US', 'name': '标普500', 'market': '美股', 'flag': '🇺🇸'},
        {'symbol': 'IXIC.US', 'name': '纳斯达克综合', 'market': '美股', 'flag': '🇺🇸'},
        {'symbol': 'DJI.US', 'name': '道琼斯', 'market': '美股', 'flag': '🇺🇸'},
        {'symbol': 'HSI.HK', 'name': '恒生指数', 'market': '港股', 'flag': '🇭🇰'},
        {'symbol': 'HSTECH.HK', 'name': '恒生科技指数', 'market': '港股', 'flag': '🇭🇰'},
        {'symbol': '000001.SH', 'name': '上证指数', 'market': 'A股', 'flag': '🇨🇳'},
        {'symbol': '399001.SZ', 'name': '深证成指', 'market': 'A股', 'flag': '🇨🇳'},
        {'symbol': '000688.SH', 'name': '科创50', 'market': 'A股', 'flag': '🇨🇳'},
    ],
    # 美股M7
    'm7': [
        {'symbol': 'NVDA.US', 'name': '英伟达', 'flag': '🇺🇸', 'desc': 'AI芯片龙头'},
        {'symbol': 'MSFT.US', 'name': '微软', 'flag': '🇺🇸', 'desc': '云计算与AI'},
        {'symbol': 'AAPL.US', 'name': '苹果', 'flag': '🇺🇸', 'desc': '消费电子'},
        {'symbol': 'GOOGL.US', 'name': '谷歌', 'flag': '🇺🇸', 'desc': '搜索与AI'},
        {'symbol': 'AMZN.US', 'name': '亚马逊', 'flag': '🇺🇸', 'desc': '电商与云'},
        {'symbol': 'META.US', 'name': 'Meta', 'flag': '🇺🇸', 'desc': '社交与元宇宙'},
        {'symbol': 'TSLA.US', 'name': '特斯拉', 'flag': '🇺🇸', 'desc': '电动车'},
    ],
    # 港股业务相关标的
    'hkStocks': [
        {'symbol': '00700.HK', 'name': '腾讯控股', 'flag': '🇭🇰', 'desc': '游戏+云+AI'},
        {'symbol': '09988.HK', 'name': '阿里巴巴-W', 'flag': '🇭🇰', 'desc': '电商+云+AI'},
        {'symbol': '03690.HK', 'name': '美团-W', 'flag': '🇭🇰', 'desc': '本地生活'},
        {'symbol': '01810.HK', 'name': '小米集团-W', 'flag': '🇭🇰', 'desc': '手机+AIoT'},
        {'symbol': '02015.HK', 'name': '理想汽车-W', 'flag': '🇭🇰', 'desc': '新能源车'},
        {'symbol': '09888.HK', 'name': '百度集团-SW', 'flag': '🇭🇰', 'desc': '搜索+AI'},
        {'symbol': '01024.HK', 'name': '快手-W', 'flag': '🇭🇰', 'desc': '短视频'},
        {'symbol': '00285.HK', 'name': '比亚迪电子', 'flag': '🇭🇰', 'desc': '电子制造'},
    ],
    # A股相关
    'aStocks': [
        {'symbol': '603171.SH', 'name': '税友股份', 'flag': '🇨🇳', 'desc': '财税SaaS'},
        {'symbol': '300033.SZ', 'name': '同花顺', 'flag': '🇨🇳', 'desc': '金融科技'},
    ],
    # 美股对标
    'usPeers': [
        {'symbol': 'INTU.US', 'name': '财捷(Intuit)', 'flag': '🇺🇸', 'desc': '财税SaaS龙头'},
    ]
}


def format_market_cap(cap):
    """格式化市值"""
    if cap is None or cap == 0:
        return '-'
    if cap >= 1e12:  # 万亿
        return f'{cap/1e12:.2f}万亿'
    if cap >= 1e8:  # 亿
        return f'{cap/1e8:.0f}亿'
    return str(cap)


def fetch_stock_data():
    """抓取股票数据"""
    print('开始抓取股票数据...')

    # 初始化配置
    config = Config.from_apikey(
        app_key=APP_KEY,
        app_secret=APP_SECRET
    )

    # 创建行情上下文
    ctx = QuoteContext(config)

    result = {
        'date': TODAY,
        'lastUpdate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'indices': [],
        'm7': [],
        'hkStocks': [],
        'aStocks': [],
        'usPeers': [],
        'marketCommentary': {
            'us': '',
            'cn': '',
            'hk': ''
        }
    }

    try:
        # 获取各类股票数据
        print('获取宏观指数...')
        result['indices'] = fetch_quotes(ctx, STOCK_CONFIG['indices'])

        print('获取美股M7...')
        result['m7'] = fetch_quotes(ctx, STOCK_CONFIG['m7'])

        print('获取港股标的...')
        result['hkStocks'] = fetch_quotes(ctx, STOCK_CONFIG['hkStocks'])

        print('获取A股标的...')
        result['aStocks'] = fetch_quotes(ctx, STOCK_CONFIG['aStocks'])

        print('获取美股对标...')
        result['usPeers'] = fetch_quotes(ctx, STOCK_CONFIG['usPeers'])

        # 生成市场解读
        result['marketCommentary'] = generate_market_commentary(result)

        # 保存数据
        output_file = os.path.join(DATA_DIR, f'stocks-{TODAY}.json')
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f'股票数据已保存: stocks-{TODAY}.json')
        return result

    except Exception as e:
        print(f'抓取股票数据失败: {e}')
        import traceback
        traceback.print_exc()
        raise
    finally:
        ctx.close()


def fetch_quotes(ctx, stocks):
    """批量获取行情"""
    results = []
    symbols = [s['symbol'] for s in stocks]

    try:
        # 获取实时报价
        quotes = ctx.quote(symbols)

        for stock, quote in zip(stocks, quotes):
            try:
                # 计算涨跌幅
                change = quote.change
                change_percent = quote.change_rate * 100 if quote.change_rate else 0

                # 获取市场数据
                market_cap = None
                try:
                    # 尝试获取静态信息
                    static = ctx.static_info([stock['symbol']])
                    if static and len(static) > 0:
                        market_cap = static[0].total_shares * quote.last_done if static[0].total_shares else None
                except:
                    pass

                results.append({
                    **stock,
                    'price': float(quote.last_done) if quote.last_done else 0,
                    'change': float(change) if change else 0,
                    'changePercent': round(change_percent, 2),
                    'volume': str(int(quote.volume)) if quote.volume else '-',
                    'marketCap': format_market_cap(market_cap),
                    'open': float(quote.open) if quote.open else 0,
                    'high': float(quote.high) if quote.high else 0,
                    'low': float(quote.low) if quote.low else 0,
                    'prevClose': float(quote.prev_close) if quote.prev_close else 0,
                })

            except Exception as e:
                print(f'  获取 {stock["symbol"]} 失败: {e}')
                # 使用备用数据
                results.append({
                    **stock,
                    'price': 0,
                    'change': 0,
                    'changePercent': 0,
                    '_error': str(e)
                })

    except Exception as e:
        print(f'批量获取行情失败: {e}')
        # 返回备用数据
        for stock in stocks:
            results.append(get_mock_data(stock))

    return results


def get_mock_data(stock):
    """获取模拟数据作为备用"""
    mock_data = {
        'SPX.US': {'price': 5650.38, 'change': 47.52, 'changePercent': 0.85},
        'IXIC.US': {'price': 17850.22, 'change': 250.18, 'changePercent': 1.42},
        'DJI.US': {'price': 42150.35, 'change': 320.15, 'changePercent': 0.76},
        'HSI.HK': {'price': 23150.32, 'change': -104.58, 'changePercent': -0.45},
        'HSTECH.HK': {'price': 5250.18, 'change': -85.42, 'changePercent': -1.60},
        '000001.SH': {'price': 3345.86, 'change': -7.72, 'changePercent': -0.23},
        'NVDA.US': {'price': 142.35, 'change': 4.35, 'changePercent': 3.15},
        'MSFT.US': {'price': 432.18, 'change': 5.35, 'changePercent': 1.25},
        'AAPL.US': {'price': 238.52, 'change': 1.62, 'changePercent': 0.68},
        '00700.HK': {'price': 520.50, 'change': -4.45, 'changePercent': -0.85},
        '09988.HK': {'price': 128.30, 'change': -1.45, 'changePercent': -1.12},
    }

    symbol = stock['symbol']
    mock = mock_data.get(symbol, {'price': 0, 'change': 0, 'changePercent': 0})

    return {
        **stock,
        'price': mock['price'],
        'change': mock['change'],
        'changePercent': mock['changePercent'],
        'volume': '-',
        'marketCap': '-',
        '_note': '模拟数据'
    }


def generate_market_commentary(data):
    """生成市场解读"""
    commentary = {
        'us': '美股科技股走势分化，关注财报季指引',
        'cn': 'A股震荡整理，结构性行情明显',
        'hk': '港股受南向资金影响，科技股波动加大'
    }

    # 根据M7涨跌情况调整
    if data.get('m7'):
        up_count = sum(1 for s in data['m7'] if s.get('changePercent', 0) > 0)
        down_count = sum(1 for s in data['m7'] if s.get('changePercent', 0) < 0)

        if up_count > down_count:
            commentary['us'] = f'美股科技股情绪积极，M7中{up_count}家上涨，AI概念股领涨'
        elif down_count > up_count:
            commentary['us'] = f'美股科技股承压，M7中{down_count}家下跌，关注宏观数据影响'
        else:
            commentary['us'] = '美股科技股震荡分化，板块轮动特征明显'

    # 根据港股涨跌调整
    if data.get('hkStocks'):
        up_count = sum(1 for s in data['hkStocks'] if s.get('changePercent', 0) > 0)
        down_count = sum(1 for s in data['hkStocks'] if s.get('changePercent', 0) < 0)

        if up_count > down_count:
            commentary['hk'] = f'港股情绪回暖，科技股{up_count}家上涨，南向资金净流入'
        elif down_count > up_count:
            commentary['hk'] = f'港股回调，科技股{down_count}家下跌，关注外围市场影响'

    return commentary


if __name__ == '__main__':
    fetch_stock_data()
