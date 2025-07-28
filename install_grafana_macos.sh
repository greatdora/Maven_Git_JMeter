#!/bin/bash

# macOS Grafana 安装脚本
# 适用于 macOS 系统

echo "🚀 开始安装 Grafana on macOS..."

# 检查是否已安装 Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew 未安装，正在安装..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew 已安装"
fi

# 更新 Homebrew
echo "📦 更新 Homebrew..."
brew update

# 安装 Grafana
echo "📦 安装 Grafana..."
brew install grafana

# 检查安装是否成功
if command -v grafana-server &> /dev/null; then
    echo "✅ Grafana 安装成功"
else
    echo "❌ Grafana 安装失败"
    exit 1
fi

# 创建配置文件目录（如果不存在）
echo "📁 创建配置文件目录..."
sudo mkdir -p /usr/local/etc/grafana
sudo mkdir -p /usr/local/var/lib/grafana
sudo mkdir -p /usr/local/var/log/grafana

# 设置权限
echo "🔐 设置权限..."
sudo chown -R $(whoami) /usr/local/var/lib/grafana
sudo chown -R $(whoami) /usr/local/var/log/grafana

# 启动 Grafana 服务
echo "🚀 启动 Grafana 服务..."
brew services start grafana

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
if brew services list | grep grafana | grep started &> /dev/null; then
    echo "✅ Grafana 服务启动成功"
    echo "🌐 访问地址: http://localhost:3000"
    echo "👤 默认用户名: admin"
    echo "🔑 默认密码: admin"
else
    echo "❌ Grafana 服务启动失败"
    echo "📋 尝试手动启动:"
    echo "   brew services start grafana"
    echo "   或者:"
    echo "   grafana-server --config=/usr/local/etc/grafana/grafana.ini"
fi

# 显示服务信息
echo ""
echo "📊 服务信息:"
brew services info grafana

echo ""
echo "🎯 下一步:"
echo "1. 打开浏览器访问 http://localhost:3000"
echo "2. 使用默认凭据登录 (admin/admin)"
echo "3. 配置数据源 (Prometheus/InfluxDB/CSV)"
echo "4. 导入 dashboard 配置文件"
echo ""
echo "📁 配置文件位置:"
echo "   - 配置: /usr/local/etc/grafana/grafana.ini"
echo "   - 数据: /usr/local/var/lib/grafana"
echo "   - 日志: /usr/local/var/log/grafana"
echo ""
echo "🔧 常用命令:"
echo "   - 启动: brew services start grafana"
echo "   - 停止: brew services stop grafana"
echo "   - 重启: brew services restart grafana"
echo "   - 状态: brew services list | grep grafana" 