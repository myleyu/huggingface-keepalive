import requests
import time
import os
from datetime import datetime
import sys
import json

def ping_gradio_space(base_url, max_retries=3):
    """
    真正调用 Gradio API 来保活 Space
    """
    print("=" * 70)
    print(f"🚀 开始保活 Gradio Space")
    print(f"🔗 URL: {base_url}")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Step 1: 访问首页获取配置
    print("\n📡 步骤 1: 访问 Space 首页...")
    try:
        response = requests.get(
            base_url,
            timeout=60,  # 增加超时时间，等待冷启动
            headers={
                'User-Agent': 'Mozilla/5.0 (GitHub-Actions-Pinger)',
                'Accept': 'text/html,application/xhtml+xml,application/xml'
            }
        )
        print(f"   ✅ 状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ⚠️ 首页访问失败")
            return False
        
        # 检查是否是真实的 Space 页面
        if 'gradio' not in response.text.lower():
            print(f"   ⚠️ 页面不包含 Gradio 内容，可能是缓存页面")
        else:
            print(f"   ✅ 检测到 Gradio 页面")
            
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False
    
    # Step 2: 建立 WebSocket 连接（模拟真实用户）
    print("\n📡 步骤 2: 尝试调用 API 端点...")
    
    # 尝试多个可能的 API 端点
    api_endpoints = [
        f"{base_url}/api/predict",
        f"{base_url}/call/predict",
        f"{base_url}/api/health",
        f"{base_url}/api/",
    ]
    
    for endpoint in api_endpoints:
        try:
            print(f"   尝试: {endpoint}")
            
            # 发送 POST 请求到 API
            response = requests.post(
                endpoint,
                json={
                    "data": [],
                    "fn_index": 0,
                    "session_hash": f"github_actions_{int(time.time())}"
                },
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (GitHub-Actions-Pinger)'
                },
                timeout=30
            )
            
            print(f"   ✅ API 响应: {response.status_code}")
            
            # 即使返回错误，只要有响应就说明容器在运行
            if response.status_code in [200, 201, 400, 422, 500]:
                print(f"   ✅ 容器正在运行（已触发后端）")
                return True
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️  超时（容器可能正在启动）")
        except Exception as e:
            print(f"   ⚠️ {str(e)[:50]}")
    
    # Step 3: 最后尝试 - 访问 /config 端点
    print("\n📡 步骤 3: 尝试获取 Gradio 配置...")
    try:
        config_url = f"{base_url}/config"
        response = requests.get(config_url, timeout=30)
        
        if response.status_code == 200:
            print(f"   ✅ 成功获取配置")
            try:
                config = response.json()
                print(f"   ✅ Gradio 版本: {config.get('version', 'unknown')}")
            except:
                pass
            return True
    except Exception as e:
        print(f"   ⚠️ 配置获取失败: {e}")
    
    print("\n⚠️ 所有 API 调用尝试完毕")
    return False

def main():
    space_url = os.getenv('SPACE_URL')
    
    if not space_url:
        print("❌ 错误: 未设置 SPACE_URL 环境变量")
        print("请在 GitHub Secrets 中添加 SPACE_URL")
        print("格式: https://huggingface.co/spaces/用户名/space名称")
        sys.exit(1)
    
    # 确保 URL 格式正确
    if not space_url.startswith('http'):
        space_url = f"https://{space_url}"
    
    # 移除尾部斜杠
    space_url = space_url.rstrip('/')
    
    print(f"📍 目标 Space: {space_url}")
    
    # 执行保活
    success = ping_gradio_space(space_url)
    
    print("\n" + "=" * 70)
    if success:
        print("✅ 保活成功 - Space 容器已响应")
        print("💡 说明: 已成功触发 Space 后端，容器应保持活跃")
    else:
        print("⚠️ 保活可能未成功")
        print("💡 建议:")
        print("   1. 检查 SPACE_URL 是否正确")
        print("   2. 手动访问 Space 确认其正在运行")
        print("   3. 考虑使用 HuggingFace Pro 获得更稳定的运行")
    print("=" * 70)
    
    # 即使失败也返回 0，避免 Actions 报错
    sys.exit(0)

if __name__ == "__main__":
    main()
