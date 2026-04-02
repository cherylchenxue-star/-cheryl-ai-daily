#!/usr/bin/env python3
"""
手动获取 Longbridge Token
步骤：
1. 访问 https://open.longbridgeapp.com/account
2. 登录后点击左侧菜单"令牌管理"
3. 点击"新建令牌"，选择需要的权限（至少要有行情权限）
4. 复制生成的 Access Token
5. 粘贴到下方 TOKEN 变量中运行此脚本
"""

import os

# ========== 请在这里粘贴你的 Access Token ==========
TOKEN = ""
# =================================================

def save_token():
    if not TOKEN or TOKEN == "":
        print("请先获取 Access Token 并粘贴到 TOKEN 变量中")
        print("\n获取步骤：")
        print("1. 访问 https://open.longbridgeapp.com/account")
        print("2. 登录后点击左侧菜单'令牌管理'")
        print("3. 点击'新建令牌'，选择行情权限")
        print("4. 复制 Access Token 粘贴到本文件的 TOKEN 变量")
        return False

    # 保存到 .env 文件
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")

    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 替换或添加 token
    if "LONGBRIDGE_ACCESS_TOKEN=" in content:
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            if line.startswith("LONGBRIDGE_ACCESS_TOKEN="):
                new_lines.append(f"LONGBRIDGE_ACCESS_TOKEN={TOKEN}")
            else:
                new_lines.append(line)
        content = "\n".join(new_lines)
    else:
        content += f"\nLONGBRIDGE_ACCESS_TOKEN={TOKEN}\n"

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Token 已保存到 {env_path}")

    # 测试 API
    print("\n正在测试 API...")
    try:
        from longbridge.openapi import Config, QuoteContext

        config = Config.from_apikey_env()
        ctx = QuoteContext(config)
        quotes = ctx.quote(["AAPL.US"])

        if quotes:
            print(f"✅ API 测试成功! AAPL 当前价格: ${quotes[0].last_done}")
            print("\n现在可以运行: npm run fetch")
        else:
            print("⚠️ 获取行情失败")

        ctx.close()

    except Exception as e:
        print(f"❌ API 测试失败: {e}")
        print("\n可能的原因：")
        print("1. Token 格式不正确")
        print("2. Token 已过期")
        print("3. 网络连接问题")

    return True

if __name__ == "__main__":
    save_token()
