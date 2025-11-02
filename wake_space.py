import os
import sys
import time
from datetime import datetime

def wake_with_gradio_client():
    """使用 Gradio Client 真正调用 Space"""
    
    space_url = os.getenv('SPACE_URL')
    
    if not space_url:
        print("❌ 未设置 SPACE_URL")
        return False
    
    # 提取 space 路径
    try:
        if 'huggingface.co/spaces/' in space_url:
            space_id = space_url.split('huggingface.co/spaces/')[-1].rstrip('/')
        else:
            print("❌ URL 格式不正确")
            return False
    except Exception as e:
        print(f"❌ URL 解析失败: {e}")
        return False
    
    print("=" * 70)
    print(f"🚀 使用 Gradio Client 唤醒 Space")
    print(f"📍 Space ID: {space_id}")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        from gradio_client import Client
        
        print("\n📡 正在连接到 Space...")
        print("   （如果 Space 正在休眠，这个过程可能需要 2-5 分钟）")
        
        # 创建客户端（这会自动唤醒休眠的 Space）
        client = Client(space_id)
        
        print("✅ 成功连接到 Space!")
        
        # 获取端点信息
        try:
            api_info = client.view_api(return_info=True)
            print(f"✅ 检测到 {len(api_info)} 个 API 端点")
        except:
            print("✅ Space 已连接（API 信息获取可选）")
        
        # 尝试调用一个简单的查询端点（不会触发复杂操作）
        print("\n🔄 尝试调用状态查询端点...")
        
        try:
            # 方法1: 尝试调用 get_status（fn_index: 5）
            result = client.predict(fn_index=5)
            print(f"✅ 成功调用 get_status 端点")
            print(f"   返回: {str(result)[:100]}...")
            
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️ 端点调用失败: {error_msg[:100]}")
            
            # 方法2: 尝试调用 refresh_all（fn_index: 2）
            try:
                print("\n🔄 尝试备用端点 refresh_all...")
                result = client.predict(fn_index=2)
                print(f"✅ 成功调用 refresh_all 端点")
            except Exception as e2:
                print(f"⚠️ 备用端点也失败: {str(e2)[:50]}")
                # 没关系，连接已经建立就够了
        
        print("\n🎉 Space 已被成功唤醒/保活!")
        print("💡 即使 API 调用失败，连接本身也足以保持 Space 活跃")
        return True
        
    except ImportError:
        print("❌ gradio_client 未安装")
        print("💡 正在安装...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gradio_client"])
        print("✅ 安装完成，请重新运行")
        return False
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ 连接失败: {error_msg[:200]}")
        
        # 检查常见错误
        if "Could not find Space" in error_msg:
            print("\n💡 Space 不存在或无法访问")
            print("   请检查 SPACE_URL 是否正确")
        elif "timeout" in error_msg.lower():
            print("\n💡 连接超时 - Space 可能正在冷启动")
            print("   这实际上意味着 Space 正在被唤醒！")
            return True  # 超时也算成功，因为触发了唤醒
        
        return False

if __name__ == "__main__":
    success = wake_with_gradio_client()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ 保活任务完成")
        print("📊 下次运行: 4 小时后")
        print("🛡️ Space 将保持活跃状态")
    else:
        print("⚠️ 保活可能未完全成功，但已尝试唤醒")
    print("=" * 70)
    
    sys.exit(0)
