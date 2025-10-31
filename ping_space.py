import requests
import time
import os
from datetime import datetime

def ping_space(url, max_retries=3):
    """
    Ping HuggingFace Space to keep it awake
    """
    print(f"🚀 开始 Ping Space: {url}")
    print(f"⏰ 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n📡 尝试 {attempt}/{max_retries}...")
            
            # 发送 GET 请求
            response = requests.get(
                url,
                timeout=30,
                headers={
                    'User-Agent': 'Mozilla/5.0 (GitHub Actions Space Pinger)'
                }
            )
            
            print(f"✅ HTTP 状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("🎉 Space 正在运行！")
                return True
            else:
                print(f"⚠️ 意外状态码: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏱️ 请求超时 (尝试 {attempt}/{max_retries})")
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {str(e)}")
        
        if attempt < max_retries:
            wait_time = 10 * attempt
            print(f"⏳ 等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
    
    print("❌ 所有尝试均失败")
    return False

def main():
    # 从环境变量读取 Space URL
    space_url = os.getenv('SPACE_URL')
    
    if not space_url:
        print("❌ 错误: 未设置 SPACE_URL 环境变量")
        print("请在 GitHub Secrets 中添加 SPACE_URL")
        exit(1)
    
    # 确保 URL 格式正确
    if not space_url.startswith('http'):
        space_url = f"https://{space_url}"
    
    # 执行 Ping
    success = ping_space(space_url)
    
    if success:
        print("\n✅ Ping 成功完成")
        exit(0)
    else:
        print("\n⚠️ Ping 失败，但不影响工作流")
        exit(0)  # 不让工作流失败

if __name__ == "__main__":
    main()
