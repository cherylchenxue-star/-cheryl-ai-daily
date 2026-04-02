#!/usr/bin/env python3
"""
Longbridge OAuth 授权脚本
会自动打开浏览器进行授权
"""

import os
import sys
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# API Key
APP_KEY = "a4ee5cca06ea39ff2ea48cb12c7d1d43"
APP_SECRET = "b03dff25d2ea0fd7bbc2201a820d09a85f546e06a4634043bacd62068d149fb5"

# 全局变量存储 token
auth_code = None
server_running = True

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code, server_running

        # 解析 URL 参数
        if "?" in self.path:
            query = self.path.split("?")[1]
            params = {}
            for param in query.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key] = value

            auth_code = params.get("code")
            state = params.get("state")

            # 发送成功响应
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            if auth_code:
                html = """
                <html>
                <head><title>授权成功</title></head>
                <body style="text-align: center; padding: 50px; font-family: Arial;">
                    <h1 style="color: green;">✓ 授权成功</h1>
                    <p>请关闭此窗口，返回命令行查看 token。</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode("utf-8"))
                server_running = False
            else:
                error = params.get("error", "未知错误")
                html = f"""
                <html>
                <head><title>授权失败</title></head>
                <body style="text-align: center; padding: 50px; font-family: Arial;">
                    <h1 style="color: red;">✗ 授权失败</h1>
                    <p>错误: {error}</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        # 静默日志
        pass

def generate_auth_url():
    """生成授权 URL"""
    import urllib.parse
    import secrets

    state = secrets.token_urlsafe(16)
    redirect_uri = "http://localhost:8080/callback"

    params = {
        "response_type": "code",
        "client_id": APP_KEY,
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": "quote trade"
    }

    query = urllib.parse.urlencode(params)
    return f"https://openapi.longbridge.cn/oauth2/authorize?{query}", state, redirect_uri

def exchange_code_for_token(code, redirect_uri):
    """用 code 换取 token"""
    import urllib.request
    import urllib.parse
    import json
    import base64

    url = "https://openapi.longbridge.cn/oauth2/token"

    # 生成 Basic Auth
    credentials = base64.b64encode(f"{APP_KEY}:{APP_SECRET}".encode()).decode()

    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }).encode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {credentials}"
    }

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            return result
    except Exception as e:
        print(f"Token 请求失败: {e}")
        return None

def main():
    print("=" * 60)
    print("Longbridge OAuth 授权")
    print("=" * 60)

    # 生成授权 URL
    auth_url, state, redirect_uri = generate_auth_url()

    print(f"\n授权 URL: {auth_url}\n")

    # 启动本地回调服务器
    server = HTTPServer(("localhost", 8080), CallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    print("[1] 正在等待授权回调...")
    print("[2] 尝试打开浏览器...")

    # 尝试打开浏览器
    try:
        webbrowser.open(auth_url)
        print("    浏览器已打开，请在浏览器中完成授权")
    except:
        print(f"    请手动复制以下链接到浏览器打开:\n    {auth_url}")

    print("\n[3] 等待授权完成...")

    # 等待回调
    timeout = 120  # 2分钟超时
    start_time = time.time()

    while server_running and time.time() - start_time < timeout:
        time.sleep(0.5)

    if auth_code:
        print(f"\n[4] 获取到授权码，正在换取 Token...")

        # 用 code 换取 token
        token_response = exchange_code_for_token(auth_code, redirect_uri)

        if token_response and "access_token" in token_response:
            access_token = token_response["access_token"]
            refresh_token = token_response.get("refresh_token", "")
            expires_in = token_response.get("expires_in", 0)

            print(f"\n✓ 授权成功!")
            print(f"  Access Token: {access_token[:30]}...")
            print(f"  有效期: {expires_in} 秒")

            # 保存到 .env 文件
            env_path = os.path.join(os.path.dirname(__file__), "..", ".env")

            with open(env_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 更新 token
            if "LONGBRIDGE_ACCESS_TOKEN=" in content:
                lines = content.split("\n")
                new_lines = []
                for line in lines:
                    if line.startswith("LONGBRIDGE_ACCESS_TOKEN="):
                        new_lines.append(f"LONGBRIDGE_ACCESS_TOKEN={access_token}")
                    else:
                        new_lines.append(line)
                content = "\n".join(new_lines)
            else:
                content += f"\nLONGBRIDGE_ACCESS_TOKEN={access_token}\n"

            with open(env_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"\n✓ Token 已保存到 {env_path}")
            print("\n现在可以运行: npm run fetch")

        else:
            print("\n✗ 换取 Token 失败")
            print(f"响应: {token_response}")
    else:
        print("\n✗ 授权超时或未完成")

    # 关闭服务器
    server.shutdown()
    print("\n按回车键退出...")
    input()

if __name__ == "__main__":
    main()
