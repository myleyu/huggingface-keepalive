import os
import sys
import time
from datetime import datetime

def wake_with_browser_simulation():
    """模拟真实浏览器访问"""
    
    space_url = os.getenv('SPACE_URL')
    
    if not space_url:
        print("❌ 未设置 SPACE_URL")
        return False
    
    print("=" * 70)
    print(f"🌐 模拟浏览器访问 Space")
    print(f"🔗 URL: {space_url}")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        import requests
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry
        
        # 创建一个持久会话，模拟浏览器
        session = requests.Session()
        
        # 设置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 完整的浏览器请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        print("\n📡 第 1 步: 访问主页（模拟浏览器首次访问）")
        response = session.get(space_url, headers=headers, timeout=60)
        print(f"   ✅ 状态码: {response.status_code}")
        print(f"   📦 响应大小: {len(response.content)} bytes")
        
        if response.status_code != 200:
            print("   ⚠️ 首页访问失败")
            return False
        
        # 等待一下，模拟真实用户
        time.sleep(2)
        
        # 尝试获取 Gradio 配置
        print("\n📡 第 2 步: 获取 Gradio 配置")
        config_url = f"{space_url}/config"
        try:
            config_response = session.get(config_url, headers=headers, timeout=30)
            if config_response.status_code == 200:
                print(f"   ✅ 成功获取配置")
                # 解析配置
                try:
                    config = config_response.json()
                    if 'components' in config:
                        print(f"   ✅ 检测到 {len(config.get('components', []))} 个组件")
                except:
                    pass
        except Exception as e:
            print(f"   ⚠️ 配置获取失败: {str(e)[:50]}")
        
        time.sleep(1)
        
        # 尝试建立队列连接（Gradio 的关键机制）
        print("\n📡 第 3 步: 尝试加入队列")
        queue_url = f"{space_url}/queue/join"
        try:
            queue_data = {
                "fn_index": 0,
                "session_hash": f"github_actions_{int(time.time())}"
            }
            queue_response = session.post(
                queue_url, 
                json=queue_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            print(f"   ✅ 队列响应: {queue_response.status_code}")
            
            if queue_response.status_code in [200, 201]:
                print("   🎉 成功触发 Gradio 队列系统!")
                return True
                
        except Exception as e:
            print(f"   ⚠️ 队列加入失败: {str(e)[:50]}")
        
        # 最后尝试：访问 API info
        print("\n📡 第 4 步: 获取 API 信息")
        info_url = f"{space_url}/info"
        try:
            info_response = session.get(info_url, timeout=30)
            if info_response.status_code == 200:
                print(f"   ✅ 成功获取 API 信息")
                return True
        except Exception as e:
            print(f"   ⚠️ API 信息获取失败: {str(e)[:50]}")
        
        print("\n✅ 已完成多次请求，Space 应该被唤醒了")
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    success = wake_with_browser_simulation()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ Space 保活完成")
    else:
        print("⚠️ 保活尝试完成")
    print("=" * 70)
    
    sys.exit(0)
