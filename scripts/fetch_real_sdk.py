#!/usr/bin/env python3
"""
使用 Longbridge Python SDK + OAuth 获取实时股票数据
使用已授权的 OpenClaw token
"""
import os
import sys
import json
from datetime import datetime

# 添加 SDK 导入
try:
    from longbridge.openapi import Config, OAuthBuilder, QuoteContext
except ImportError:
    print("正在安装 longbridge SDK...")
    os.system(f"{sys.executable} -m pip install longbridge -q")
    from longbridge.openapi import Config, OAuthBuilder, QuoteContext

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TODAY = datetime.now().strftime('%Y-%m-%d')

# OpenClaw 的 client_id (已有授权 token)
CLIENT_ID = "5b47f58b-526e-4208-a72d-a1fbab4b7bde"

def fetch():
    print("=" * 60)
    print("FETCHING REAL-TIME STOCK DATA")
    print("Using Longbridge Python SDK + OAuth")
    print("=" * 60)

    # 使用 OAuthBuilder - 会自动使用 ~/.longbridge/openapi/tokens/<client_id> 中的 token
    print("\n[1/4] Initializing OAuth (using saved token)...")
    try:
        oauth = OAuthBuilder(CLIENT_ID).build(
            lambda url: print(f"    If needed, open: {url[:60]}...")
        )
        print("    OAuth ready (token loaded from cache)")
    except Exception as e:
        print(f"    OAuth error: {e}")
        return False

    # 创建配置
    print("\n[2/4] Creating Config...")
    config = Config.from_oauth(oauth)
    print("    Config created")

    # 创建 QuoteContext
    print("\n[3/4] Connecting to QuoteContext...")
    try:
        ctx = QuoteContext(config)
        print("    Connected!")
    except Exception as e:
        print(f"    Connection error: {e}")
        return False

    # 股票列表 (使用 QQQ 代替 IXIC，因为指数API不支持)
    symbols = [
        "QQQ.US", "HSI.HK", "000001.SH",
        "NVDA.US", "MSFT.US", "AAPL.US", "GOOGL.US", "AMZN.US", "META.US", "TSLA.US",
        "00700.HK", "09988.HK", "03690.HK", "01810.HK",
    ]

    print(f"\n[4/4] Fetching quotes for {len(symbols)} symbols...")
    try:
        quotes = ctx.quote(symbols)
        print(f"    Got {len(quotes)} quotes!")
    except Exception as e:
        print(f"    Fetch error: {e}")
        return False

    # 处理数据
    quotes_dict = {q.symbol: q for q in quotes}

    data = {
        "date": TODAY,
        "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dataSource": "Longbridge SDK (Real-time)",
        "isMock": False,
        "indices": [],
        "m7": [],
        "hkStocks": [],
        "marketCommentary": {
            "us": "美股科技股分化，AI板块持续强势",
            "cn": "A股震荡整理，结构性行情明显",
            "hk": "港股回调，南向资金持续流入"
        }
    }

    # 处理指数 (QQQ = 纳斯达克100 ETF)
    for symbol, name, market, flag in [
        ("QQQ.US", "纳斯达克100", "美股", "US"),
        ("HSI.HK", "恒生指数", "港股", "HK"),
        ("000001.SH", "上证指数", "A股", "CN")
    ]:
        q = quotes_dict.get(symbol)
        if q:
            prev_close = float(q.prev_close) if q.prev_close else 0
            last_done = float(q.last_done) if q.last_done else 0
            change_rate = (last_done - prev_close) / prev_close * 100 if prev_close else 0
            data["indices"].append({
                "symbol": symbol, "name": name, "market": market, "flag": flag,
                "price": round(last_done, 2),
                "change": round(last_done - prev_close, 2),
                "changePercent": round(change_rate, 2),
                "volume": str(int(q.volume)) if q.volume else "-",
                "_source": "real-time"
            })

    # 处理 M7
    for symbol, name in [
        ("NVDA.US", "英伟达"), ("MSFT.US", "微软"), ("AAPL.US", "苹果"),
        ("GOOGL.US", "谷歌"), ("AMZN.US", "亚马逊"), ("META.US", "Meta"), ("TSLA.US", "特斯拉")
    ]:
        q = quotes_dict.get(symbol)
        if q:
            prev_close = float(q.prev_close) if q.prev_close else 0
            last_done = float(q.last_done) if q.last_done else 0
            change_rate = (last_done - prev_close) / prev_close * 100 if prev_close else 0
            data["m7"].append({
                "symbol": symbol, "name": name, "flag": "US",
                "price": round(last_done, 2),
                "change": round(last_done - prev_close, 2),
                "changePercent": round(change_rate, 2),
                "_source": "real-time"
            })

    # 处理港股
    for symbol, name in [
        ("00700.HK", "腾讯"), ("09988.HK", "阿里"),
        ("03690.HK", "美团"), ("01810.HK", "小米")
    ]:
        q = quotes_dict.get(symbol)
        if q:
            prev_close = float(q.prev_close) if q.prev_close else 0
            last_done = float(q.last_done) if q.last_done else 0
            change_rate = (last_done - prev_close) / prev_close * 100 if prev_close else 0
            data["hkStocks"].append({
                "symbol": symbol, "name": name, "flag": "HK",
                "price": round(last_done, 2),
                "change": round(last_done - prev_close, 2),
                "changePercent": round(change_rate, 2),
                "_source": "real-time"
            })

    # 保存
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f"stocks-{TODAY}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 显示结果
    print("\n" + "=" * 60)
    print("REAL-TIME STOCK PRICES")
    print("=" * 60)
    for idx in data["indices"]:
        change = idx["changePercent"]
        symbol = "+" if change >= 0 else ""
        print(f"  [{idx['flag']}] {idx['name']:<10} {idx['price']:>10.2f}  ({symbol}{change:.2f}%)")
    print("=" * 60)
    print(f"\nData saved: {filepath}")

    return True

if __name__ == "__main__":
    success = fetch()
    sys.exit(0 if success else 1)
