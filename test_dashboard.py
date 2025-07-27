#!/usr/bin/env python3
"""
测试dashboard生成和Jenkins集成
"""

import os
import sys

def test_dashboard_files():
    """测试dashboard文件是否存在且正确"""
    compare_results_dir = 'compare_results'
    
    # 检查目录是否存在
    if not os.path.exists(compare_results_dir):
        print(f"❌ 目录 {compare_results_dir} 不存在")
        return False
    
    # 检查必要文件
    required_files = [
        'dashboard.html',
        'performance_dashboard.png'
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(compare_results_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
        else:
            size = os.path.getsize(file_path)
            print(f"✅ {file}: {size} bytes")
    
    if missing_files:
        print(f"❌ 缺少文件: {missing_files}")
        return False
    
    # 检查HTML文件内容
    html_path = os.path.join(compare_results_dir, 'dashboard.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'JMeter Performance Dashboard' in content:
        print("✅ HTML文件内容正确")
    else:
        print("❌ HTML文件内容可能有问题")
        return False
    
    print("\n🎉 Dashboard文件检查完成！")
    print("📋 在Jenkins中查看步骤：")
    print("1. 进入Jenkins项目页面")
    print("2. 点击最新的构建")
    print("3. 在左侧菜单中找到 'Performance Dashboard'")
    print("4. 点击查看完整的性能报告")
    
    return True

def generate_test_dashboard():
    """生成测试dashboard"""
    print("🔄 生成测试dashboard...")
    
    # 确保compare_results目录存在
    os.makedirs('compare_results', exist_ok=True)
    
    # 运行dashboard生成脚本
    try:
        import subprocess
        result = subprocess.run(['python3', 'compare_tg.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dashboard生成成功")
            print(result.stdout)
        else:
            print("❌ Dashboard生成失败")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 运行脚本时出错: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Jenkins Dashboard 测试工具")
    print("=" * 50)
    
    # 检查是否在Jenkins环境中
    jenkins_url = os.environ.get('BUILD_URL')
    if jenkins_url:
        print(f"🔗 检测到Jenkins环境: {jenkins_url}")
    else:
        print("💻 本地环境")
    
    # 生成dashboard
    if generate_test_dashboard():
        # 测试文件
        test_dashboard_files()
    else:
        print("❌ 无法生成dashboard")
        sys.exit(1) 