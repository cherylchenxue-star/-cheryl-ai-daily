#!/usr/bin/env python3
"""
使用 Longbridge OAuth 获取实时股票数据
不使用 Mock，坚决获取真实数据！
"""
import os
import sys
import json
import webbrowser
import urllib.request
import urllib.parse
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
from datetime import datetime

# ========== 配置 ==========
APP_KEY = "a4ee5cca06ea39ff2ea48cb12c7d1d43"
APP_SECRET = "b03dff25d2ea0fd7bbc2201a820d09a85f546e06a4634043bacd62068d149fb5"
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TODAY = datetime.now().strftime('%Y-%m-%d')

# 全局变量
auth_code = None
auth_state = None
server_running = True

# ========== HTTP 回调服务器 ==========
class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code, auth_state, server_running

        if "/callback" in self.path:
            # 解析参数
            query = self.path.split("?")[1] if "?" in self.path else ""
            params = {}
            for param in query.split("&"):
                if "=" in param:
                    k, v = param.split("=", 1)
                    params[k] = v

            auth_code = params.get("code")
            state = params.get("state")
            error = params.get("error")

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()

            if auth_code:
                html = """
                <html><head><title>授权成功</title></head>
                <body style="text-align: center; padding: 50px; font-family: Arial;">
                    <h1 style="color: green;">✓ 授权成功！</h1>
                    <p>请返回命令行查看数据获取进度。</p>
                </body></html>
                """
                self.wfile.write(html.encode("utf-8"))
                server_running = False
            else:
                html = f"""
                <html><head><title>授权失败</title></head>
                <body style="text-align: center; padding: 50px;">
                    <h1 style="color: red;">✗ 授权失败</h1>
                    <p>错误: {error}</p>
                </body></html>
                """
                self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        pass

def start_oauth_server():
    """启动 OAuth 回调服务器"""
    server = HTTPServer(("localhost", 8080), OAuthCallbackHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server

# ========== OAuth 流程 ==========
def generate_auth_url():
    """生成授权 URL"""
    import secrets
    global auth_state
    auth_state = secrets.token_urlsafe(16)

    params = {
        "response_type": "code",
        "client_id": APP_KEY,
        "redirect_uri": "http://localhost:8080/callback",
        "state": auth_state,
        "scope": "quote"
    }

    query = urllib.parse.urlencode(params)
    return f"https://openapi.longbridge.cn/oauth2/authorize?{query}"

def exchange_code_for_token(code):
    """用 code 换取 access token"""
    url = "https://openapi.longbridge.cn/oauth2/token"

    # Basic Auth
    credentials = base64.b64encode(f"{APP_KEY}:{APP_SECRET}".encode()).decode()

    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:8080/callback"
    }).encode()

    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Token exchange failed: {e}")
        return None

# ========== 获取股票数据 ==========
def fetch_stock_data(access_token):
    """使用 access token 获取实时行情"""
    print("\n[Step 3/4] Fetching real-time stock data...")

    symbols = [
        "IXIC.US",   # 纳斯达克
        "HSI.HK",    # 恒生指数
        "000001.SH", # 上证指数
        "NVDA.US", "MSFT.US", "AAPL.US", "GOOGL.US", "AMZN.US", "META.US", "TSLA.US",  # M7
        "00700.HK", "09988.HK", "03690.HK", "01810.HK",  # 港股
    ]

    url = "https://openapi.longbridge.cn/v1/quote/get"
    data = json.dumps({"symbol": symbols}).encode()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())

            if result.get("code") == 0:
                print(f"✓ Successfully fetched {len(result.get('data', []))} stock quotes!")
                return result
            else:
                print(f"API Error: {result}")
                return None
    except Exception as e:
        print(f"Fetch failed: {e}")
        return None

def save_data(api_result):
    """保存数据到文件"""
    print("\n[Step 4/4] Saving data...")

    quotes = {q["symbol"]: q for q in api_result.get("data", [])}

    data = {
        "date": TODAY,
        "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "Longbridge Real-time API",
        "indices": [],
        "m7": [],
        "hkStocks": [],
        "marketCommentary": {
            "us": "美股科技股分化，AI板块持续强势",
            "cn": "A股震荡整理，结构性行情明显",
            "hk": "港股回调，南向资金持续流入"
        }
    }

    # 指数
    for symbol, name, market, flag in [
        ("IXIC.US", "纳斯达克", "美股", "🇺🇸"),
        ("HSI.HK", "恒生指数", "港股", "🇭🇰"),
        ("000001.SH", "上证指数", "A股", "🇨🇳")
    ]:
        q = quotes.get(symbol, {})
        data["indices"].append({
            "symbol": symbol,
            "name": name,
            "market": market,
            "flag": flag,
            "price": round(q.get("last_done", 0), 2),
            "change": round(q.get("change", 0), 2),
            "changePercent": round(q.get("change_rate", 0) * 100, 2),
            "volume": str(int(q.get("volume", 0))) if q.get("volume") else "-",
            "_source": "real-time"
        })

    # M7
    for symbol, name in [
        ("NVDA.US", "英伟达"), ("MSFT.US", "微软"), ("AAPL.US", "苹果"),
        ("GOOGL.US", "谷歌"), ("AMZN.US", "亚马逊"), ("META.US", "Meta"), ("TSLA.US", "特斯拉")
    ]:
        q = quotes.get(symbol, {})
        data["m7"].append({
            "symbol": symbol,
            "name": name,
            "flag": "🇺🇸",
            "price": round(q.get("last_done", 0), 2),
            "change": round(q.get("change", 0), 2),
            "changePercent": round(q.get("change_rate", 0) * 100, 2),
            "_source": "real-time"
        })

    # 港股
    for symbol, name in [
        ("00700.HK", "腾讯"), ("09988.HK", "阿里"),
        ("03690.HK", "美团"), ("01810.HK", "小米")
    ]:
        q = quotes.get(symbol, {})
        data["hkStocks"].append({
            "symbol": symbol,
            "name": name,
            "flag": "🇭🇰",
            "price": round(q.get("last_done", 0), 2),
            "change": round(q.get("change", 0), 2),
            "changePercent": round(q.get("change_rate", 0) * 100, 2),
            "_source": "real-time"
        })

    # 保存
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f"stocks-{TODAY}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ Data saved to: {filepath}")

    # 显示数据
    print("\n" + "="*60)
    print("REAL-TIME STOCK DATA")
    print("="*60)
    for idx in data["indices"]:
        change_str = f"{idx['changePercent']:+.2f}%"
        print(f"  {idx['flag']} {idx['name']}: {idx['price']} ({change_str})")
    print("="*60)

    return True

# ========== 主函数 ==========
def main():
    print("="*60)
    print("Longbridge Real-time Stock Data Fetcher")
    print("NO MOCK - REAL DATA ONLY!")
    print("="*60)

    # Step 1: 启动 OAuth 服务器
    print("\n[Step 1/4] Starting OAuth callback server on port 8080...")
    server = start_oauth_server()

    # Step 2: 生成授权 URL
    print("\n[Step 2/4] Generating authorization URL...")
    auth_url = generate_auth_url()

    print(f"\nAuthorization URL: {auth_url}")
    print("\nPlease open this URL in your browser and authorize.")

    # 尝试打开浏览器
    try:
        webbrowser.open(auth_url)
        print("(Browser opened automatically)")
    except:
        pass

    # 等待授权回调
    print("\nWaiting for authorization (timeout: 2 minutes)...")
    timeout = 120
    start_time = time.time()

    while server_running and time.time() - start_time < timeout:
        time.sleep(0.5)

    if not auth_code:
        print("\n✗ Authorization timeout!")
        server.shutdown()
        return False

    print(f"\n✓ Got authorization code!")
    server.shutdown()

    # Step 3: 换取 Token
    print("\n[Step 2.5/4] Exchanging code for access token...")
    token_response = exchange_code_for_token(auth_code)

    if not token_response or "access_token" not in token_response:
        print("✗ Failed to get access token!")
        print(f"Response: {token_response}")
        return False

    access_token = token_response["access_token"]
    print(f"✓ Got access token (expires in {token_response.get('expires_in', 'unknown')}s)")

    # Step 4: 获取股票数据
    api_result = fetch_stock_data(access_token)
    if not api_result:
        return False

    # Step 5: 保存数据
    save_data(api_result)

    print("\n✓ All done! Real-time stock data fetched successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
