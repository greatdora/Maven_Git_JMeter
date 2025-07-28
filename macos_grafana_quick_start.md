# macOS Grafana 快速启动指南

## 🚀 一键安装 (推荐)

### 方法1: 使用安装脚本
```bash
# 下载并运行安装脚本
curl -fsSL https://raw.githubusercontent.com/your-repo/install_grafana_macos.sh | bash

# 或者运行本地脚本
./install_grafana_macos.sh
```

### 方法2: 手动安装
```bash
# 1. 安装 Grafana
brew install grafana

# 2. 启动服务
brew services start grafana

# 3. 检查状态
brew services list | grep grafana
```

### 方法3: 使用 Docker (最简单)
```bash
# 拉取并运行 Grafana
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana

# 检查容器状态
docker ps | grep grafana
```

## 🌐 访问 Grafana

安装完成后，打开浏览器访问：
```
http://localhost:3000
```

**默认登录信息：**
- 用户名: `admin`
- 密码: `admin`

## 🔧 常用命令

### 服务管理
```bash
# 启动服务
brew services start grafana

# 停止服务
brew services stop grafana

# 重启服务
brew services restart grafana

# 查看状态
brew services list | grep grafana

# 查看日志
brew services info grafana
```

### 手动启动 (如果服务启动失败)
```bash
# 直接启动
grafana-server

# 后台运行
nohup grafana-server > /dev/null 2>&1 &

# 指定配置文件
grafana-server --config=/usr/local/etc/grafana/grafana.ini
```

## 📊 导入 JMeter Dashboard

### 1. 登录 Grafana
访问 `http://localhost:3000` 并使用默认凭据登录

### 2. 导入 Dashboard
1. 点击左侧菜单的 "+" 号
2. 选择 "Import"
3. 上传 `grafana_dashboard.json` 文件
4. 选择数据源
5. 点击 "Import"

### 3. 配置数据源
推荐使用以下数据源之一：

#### 选项A: CSV 文件 (最简单)
1. 安装 CSV 数据源插件
2. 添加 CSV 数据源
3. 上传 JMeter CSV 文件

#### 选项B: Prometheus
1. 安装 Prometheus
2. 添加 Prometheus 数据源
3. 配置 JMeter 数据导出

#### 选项C: InfluxDB
1. 安装 InfluxDB
2. 添加 InfluxDB 数据源
3. 使用数据转换脚本

## 🐛 常见问题

### 问题1: 端口被占用
```bash
# 检查端口占用
lsof -i :3000

# 杀死占用进程
kill -9 <PID>
```

### 问题2: 权限问题
```bash
# 修复权限
sudo chown -R $(whoami) /usr/local/var/lib/grafana
sudo chown -R $(whoami) /usr/local/var/log/grafana
```

### 问题3: 服务启动失败
```bash
# 查看详细日志
grafana-server --config=/usr/local/etc/grafana/grafana.ini

# 或者使用 Docker
docker run -d -p 3000:3000 grafana/grafana
```

## 📁 文件位置

- **配置文件**: `/usr/local/etc/grafana/grafana.ini`
- **数据目录**: `/usr/local/var/lib/grafana`
- **日志目录**: `/usr/local/var/log/grafana`

## 🎯 下一步

1. ✅ 安装并启动 Grafana
2. ✅ 登录 Grafana 界面
3. 🔄 配置数据源
4. 🔄 导入 JMeter Dashboard
5. 🔄 运行数据转换脚本
6. 🔄 配置告警规则

## 💡 提示

- **Docker 方式最简单**，推荐新手使用
- **Homebrew 方式**适合需要自定义配置的用户
- **CSV 数据源**是最快的开始方式
- **Prometheus** 适合生产环境

现在你可以开始使用 Grafana 来监控 JMeter 性能数据了！🎉 