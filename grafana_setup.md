# Grafana 安装和配置指南

## 🎯 Grafana 优势

### ✅ **专业级功能：**
- **多种图表类型** - 折线图、柱状图、热力图、仪表盘、表格等
- **实时数据更新** - 支持实时数据流和告警
- **丰富的交互** - 缩放、平移、时间范围选择、变量过滤
- **告警功能** - 性能阈值告警和通知
- **多数据源** - 支持Prometheus、InfluxDB、MySQL、PostgreSQL等
- **权限管理** - 用户和团队权限控制

## 📊 JMeter + Grafana 效果展示

### 🎨 **Dashboard 布局：**
```
┌─────────────────────────────────────────────────────────┐
│                    JMeter Performance Dashboard        │
├─────────────────────┬─────────────────────────────────┤
│  Response Time      │  Success Rate                  │
│  Trend Chart       │  Trend Chart                   │
│                     │                                │
├─────────────────────┼─────────────────────────────────┤
│  Throughput         │  Performance Summary           │
│  Trend Chart       │  (Stat Cards)                  │
│                     │                                │
├─────────────────────────────────────────────────────────┤
│  Thread Group Performance Table                       │
│  (实时数据表格)                                        │
└─────────────────────────────────────────────────────────┘
```

### 📈 **图表特性：**
- **响应时间趋势图** - 显示各线程组响应时间变化
- **成功率趋势图** - 显示成功率变化趋势
- **吞吐量趋势图** - 显示吞吐量变化趋势
- **性能统计卡片** - 实时显示平均值
- **数据表格** - 详细的性能数据

## 🚀 安装步骤

### 1. **安装 Grafana**

**macOS (使用 Homebrew):**
```bash
brew install grafana
brew services start grafana
```

**Docker:**
```bash
docker run -d -p 3000:3000 grafana/grafana
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
sudo apt-get update
sudo apt-get install grafana

# 启动服务
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

### 2. **访问 Grafana**
打开浏览器访问: `http://localhost:3000`

默认登录信息:
- 用户名: `admin`
- 密码: `admin`

### 3. **配置数据源**

#### 选项A: 使用 Prometheus
1. 安装 Prometheus
2. 在 Grafana 中添加 Prometheus 数据源
3. 配置 JMeter 数据导出到 Prometheus

#### 选项B: 使用 InfluxDB
1. 安装 InfluxDB
2. 在 Grafana 中添加 InfluxDB 数据源
3. 使用提供的脚本导入 JMeter 数据

#### 选项C: 使用 CSV 文件
1. 安装 CSV 数据源插件
2. 直接导入 JMeter CSV 文件

### 4. **导入 Dashboard**

#### 方法A: 使用 API
```bash
# 设置 API key
export GRAFANA_API_KEY="your_api_key"

# 导入 dashboard
curl -X POST \
  -H "Authorization: Bearer $GRAFANA_API_KEY" \
  -H "Content-Type: application/json" \
  -d @grafana_dashboard.json \
  http://localhost:3000/api/dashboards/db
```

#### 方法B: 手动导入
1. 登录 Grafana
2. 点击 "+" → "Import"
3. 上传 `grafana_dashboard.json` 文件
4. 选择数据源
5. 点击 "Import"

## 🔧 配置 JMeter 数据集成

### 1. **运行数据转换脚本**
```bash
python3 jmeter_to_grafana.py
```

### 2. **配置 Jenkins 集成**
在 `Jenkinsfile` 中添加:
```groovy
stage('Send to Grafana') {
    steps {
        script {
            // 运行数据转换
            sh 'python3 jmeter_to_grafana.py'
            
            // 可选：发送到 Grafana API
            if (env.GRAFANA_API_KEY) {
                sh '''
                    curl -X POST \\
                      -H "Authorization: Bearer $GRAFANA_API_KEY" \\
                      -H "Content-Type: application/json" \\
                      -d @grafana_dashboard.json \\
                      http://localhost:3000/api/dashboards/db
                '''
            }
        }
    }
}
```

## 📊 Grafana vs 其他方案对比

| 特性 | HTML Dashboard | Plot Plugin | Grafana |
|------|---------------|-------------|---------|
| **图表类型** | 基础图表 | 简单图表 | 专业图表 |
| **交互性** | 中等 | 低 | 高 |
| **实时更新** | 否 | 否 | 是 |
| **告警功能** | 否 | 否 | 是 |
| **多数据源** | 否 | 否 | 是 |
| **权限管理** | 否 | 否 | 是 |
| **安装复杂度** | 简单 | 中等 | 复杂 |
| **维护成本** | 低 | 低 | 中等 |

## 🎯 推荐使用场景

### ✅ **使用 Grafana 当：**
- 需要专业的性能监控
- 有多个数据源需要整合
- 需要实时告警功能
- 团队需要权限管理
- 需要长期数据存储和分析

### ✅ **使用 HTML Dashboard 当：**
- 只需要简单的性能展示
- 希望快速部署
- 不需要复杂的交互功能
- 团队规模较小

## 🔍 下一步

1. **安装 Grafana** 并配置数据源
2. **导入 dashboard** 配置文件
3. **运行数据转换脚本** 处理 JMeter 数据
4. **配置 Jenkins 集成** 自动化数据推送
5. **设置告警规则** 监控性能阈值

Grafana 提供了最专业和功能最丰富的性能监控体验！ 