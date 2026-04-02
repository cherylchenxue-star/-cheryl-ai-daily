#!/usr/bin/env python3
"""
获取 Longbridge OAuth Token
运行后会输出授权链接，你需要在浏览器中打开并授权
"""

from longbridge.openapi import OAuthBuilder, Config
import webbrowser
import os

APP_KEY = "a4ee5cca06ea39ff2ea48cb12c7d1d43"

def main():
    print("=" * 60)
    print("Longbridge OAuth 授权")
    print("=" * 60)

    def open_browser(url):
        print(f"\n请在浏览器中打开以下链接:\n{url}\n")
        print("授权完成后，程序会自动获取 token")
        print("=" * 60)

        # 尝试自动打开浏览器
        try:
            webbrowser.open(url)
            print("\n✅ 已尝试自动打开浏览器...")
        except Exception as e:
            print(f"\n⚠️ 自动打开浏览器失败: {e}")
            print("请手动复制上面的链接到浏览器打开")

    try:
        # 创建 OAuth 并授权
        print("\n正在初始化 OAuth...")
        oauth = OAuthBuilder(client_id=APP_KEY).build(open_browser)

        print("\n✅ 授权成功!")

        # 测试获取行情
        config = Config.from_oauth(oauth)
        print(f"\n✅ Config 创建成功")
        print(f"测试获取行情...")

        from longbridge.openapi import QuoteContext
        ctx = QuoteContext(config)

        # 测试获取一个行情
        quotes = ctx.quote(["AAPL.US"])
        if quotes:
            print(f"\n✅ API 测试成功! AAPL 当前价格: ${quotes[0].last_done}")

        ctx.close()

        # 保存配置信息
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        print(f"\n✅ Token 已自动缓存到: ~/.longbridge/openapi/tokens/")
        print(f"下次运行 fetch-all.js 时会自动使用缓存的 token")
        print(f"\n现在可以运行: npm run fetch")

    except Exception as e:
        print(f"\n❌ 授权失败: {e}")
        import traceback
        traceback.print_exc()
        print("\n可能的原因:")
        print("1. 网络连接问题")
        print("2. 用户取消了授权")
        print("3. API Key 不正确")

if __name__ == "__main__":
    main()
