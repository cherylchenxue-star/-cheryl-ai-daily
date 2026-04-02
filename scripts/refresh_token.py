#!/usr/bin/env python3
"""
刷新 Longbridge Access Token
"""
import os
import json
import urllib.request
import urllib.parse
import base64

TOKEN_FILE = os.path.expanduser("~/.longbridge/openapi/tokens/5b47f58b-526e-4208-a72d-a1fbab4b7bde")

def refresh_access_token():
    # 读取 token 数据
    with open(TOKEN_FILE, 'r') as f:
        token_data = json.load(f)

    client_id = token_data.get('client_id')
    refresh_token = token_data.get('refresh_token')

    print(f"Client ID: {client_id}")
    print(f"Refreshing token...")

    # 调用刷新接口
    url = "https://openapi.longbridge.cn/oauth2/token"

    # 注意：OAuth 刷新通常需要 client_secret，但我们没有
    # 尝试不带 client_secret 的请求
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id
    }).encode()

    try:
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            print(f"Response: {json.dumps(result, indent=2)}")

            if "access_token" in result:
                # 更新 token 文件
                token_data["access_token"] = result["access_token"]
                token_data["refresh_token"] = result.get("refresh_token", refresh_token)
                token_data["expires_at"] = result.get("expires_at", 0)

                with open(TOKEN_FILE, 'w') as f:
                    json.dump(token_data, f, indent=2)

                print("\n✅ Token refreshed successfully!")
                return result["access_token"]
            else:
                print(f"\n❌ Refresh failed: {result}")
                return None

    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(f"Response: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == '__main__':
    refresh_access_token()
