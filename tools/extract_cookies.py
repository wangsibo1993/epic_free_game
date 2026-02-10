import browser_cookie3
import json
import os
import sys

def extract_cookies():
    print("正在尝试从本地浏览器提取 Epic Games 的 Cookie...")
    cookies = []
    
    # 定义目标域名
    domain = 'epicgames.com'
    
    browsers = [
        ('Chrome', browser_cookie3.chrome),
        ('Edge', browser_cookie3.edge),
        ('Firefox', browser_cookie3.firefox),
        ('Safari', browser_cookie3.safari),
        ('Chromium', browser_cookie3.chromium),
        ('Brave', browser_cookie3.brave),
        ('Opera', browser_cookie3.opera),
    ]

    found_cookies = []

    for browser_name, loader in browsers:
        try:
            print(f"正在检查 {browser_name}...")
            # 尝试加载 Cookie
            cj = loader(domain_name=domain)
            count = 0
            for c in cj:
                cookie_dict = {
                    'name': c.name,
                    'value': c.value,
                    'domain': c.domain,
                    'path': c.path,
                    'secure': c.secure,
                    'httpOnly': 'HttpOnly' in c._rest,
                    'sameSite': 'Lax' # Default fallback
                }
                if c.expires:
                    cookie_dict['expires'] = c.expires
                
                found_cookies.append(cookie_dict)
                count += 1
            
            if count > 0:
                print(f"✅ 从 {browser_name} 提取到了 {count} 个 Cookie")
            
        except Exception as e:
            # 忽略未安装的浏览器或提取错误
            # print(f"  - {browser_name} 提取失败: {e}")
            pass

    if not found_cookies:
        print("❌ 未能在任何浏览器中找到 Epic Games 的 Cookie。")
        print("请确保您已在 Chrome/Edge/Firefox 等浏览器中登录了 https://store.epicgames.com")
        sys.exit(1)

    # 去重：如果多个浏览器都有，或者同一个浏览器有重复记录
    # 简单的去重策略：以 name + domain 为键
    unique_cookies = {}
    for c in found_cookies:
        key = f"{c['domain']}_{c['name']}"
        unique_cookies[key] = c
    
    final_cookies = list(unique_cookies.values())
    
    # 保存到 cookies.json
    output_path = 'cookies.json'
    try:
        with open(output_path, 'w') as f:
            json.dump(final_cookies, f, indent=2)
        print(f"\n✅ 成功保存 {len(final_cookies)} 个 Cookie 到 {output_path}")
        print("现在您可以直接运行 ./run_auto.sh 了")
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    extract_cookies()
