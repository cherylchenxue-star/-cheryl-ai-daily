#!/usr/bin/env python3
"""
使用 API Key + Secret 获取 Access Token
"""
import json
import urllib.request
import urllib.parse
import base64

APP_KEY = "a4ee5cca06ea39ff2ea48cb12c7d1d43"
APP_SECRET = "b03dff25d2ea0fd7bbc2201a820d09a85f546e06a4634043bacd62068d149fb5"

def get_token():
    url = "https://openapi.longbridge.cn/oauth2/token"

    # Basic Auth
    credentials = base64.b64encode(f"{APP_KEY}:{APP_SECRET}".encode()).decode()

    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "scope": "quote"
    }).encode()

    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            print(f"Response: {json.dumps(result, indent=2)}")

            if "access_token" in result:
                print(f"\nAccess Token: {result['access_token'][:50]}...")
                print(f"Expires in: {result.get('expires_in')} seconds")
                return result["access_token"]
            else:
                print(f"Error: {result}")
                return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == '__main__':
    get_token()
