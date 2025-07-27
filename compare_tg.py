import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from jinja2 import Template
import datetime

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# result_dir = '/data/compare_results'  # 注释掉这行
result_dir = 'compare_results'          # 用相对路径
files = sorted(glob.glob(os.path.join(result_dir, '*.csv')))
results = []

# 添加你提供的额外数据
additional_data = [
    {'file': '20250722-sample_test.csv', 'tg': 'TG1_HTTP Request', 'avg_rt': 3830.90, 'success': 100.00, 'throughput': 11.44},
    {'file': '20250722-sample_test.csv', 'tg': 'TG2_HTTP Request', 'avg_rt': 4939.10, 'success': 100.00, 'throughput': 0.66},
    {'file': '20250725-sample_test.csv', 'tg': 'TG1_HTTP Request', 'avg_rt': 760.30, 'success': 100.00, 'throughput': 11.48},
    {'file': '20250725-sample_test.csv', 'tg': 'TG2_HTTP Request', 'avg_rt': 743.60, 'success': 100.00, 'throughput': 38.76}
]

# 处理CSV文件
for file in files:
    # 假设文件名如 20250722-sample_test.csv
    base = os.path.basename(file)
    # 提取日期部分
    date_part = base.split('-')[0]
    # 如果你有一天多次测试，可以加上文件的修改时间
    file_mtime = os.path.getmtime(file)
    dt = datetime.datetime.fromtimestamp(file_mtime)
    # 格式化为 日期_时间
    label = f"{date_part}_{dt.strftime('%H%M')}"

    df = pd.read_csv(file)
    for tg in ['TG1_HTTP Request', 'TG2_HTTP Request']:
        tg_df = df[df['label'] == tg]
        if not tg_df.empty:
            avg_rt = tg_df['elapsed'].mean()
            success = tg_df['success'].mean() * 100
            # 计算 throughput（每秒采样数）
            if len(tg_df) > 1:
                duration = (tg_df['timeStamp'].max() - tg_df['timeStamp'].min()) / 1000
                throughput = len(tg_df) / duration if duration > 0 else 0
            else:
                throughput = 0
            results.append({
                'label': label,
                'file': base,
                'tg': tg,
                'avg_rt': avg_rt,
                'success': success,
                'throughput': throughput
            })

# 添加额外数据
for data in additional_data:
    date_part = data['file'].split('-')[0]
    label = f"{date_part}_0000"  # 使用默认时间
    results.append({
        'label': label,
        'file': data['file'],
        'tg': data['tg'],
        'avg_rt': data['avg_rt'],
        'success': data['success'],
        'throughput': data['throughput']
    })

result_df = pd.DataFrame(results)

# 按日期排序
result_df['date'] = pd.to_datetime(result_df['label'].str[:8], format='%Y%m%d')
result_df = result_df.sort_values('date')

if not result_df.empty:
    # 创建图表 - 进一步减小尺寸
    fig, axes = plt.subplots(2, 2, figsize=(8, 6))
    fig.suptitle('JMeter Performance Analysis Dashboard', fontsize=10, fontweight='bold')
    
    # 响应时间趋势
    for i, tg in enumerate(['TG1_HTTP Request', 'TG2_HTTP Request']):
        subset = result_df[result_df['tg'] == tg]
        axes[0, 0].plot(subset['label'], subset['avg_rt'], marker='o', label=tg, linewidth=1, markersize=3)
    axes[0, 0].set_xlabel('Test Date', fontsize=7)
    axes[0, 0].set_ylabel('Average Response Time (ms)', fontsize=7)
    axes[0, 0].set_title('Response Time Trend', fontsize=8)
    axes[0, 0].legend(fontsize=6)
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].tick_params(axis='both', which='major', labelsize=6)
    
    # 成功率趋势
    for i, tg in enumerate(['TG1_HTTP Request', 'TG2_HTTP Request']):
        subset = result_df[result_df['tg'] == tg]
        axes[0, 1].plot(subset['label'], subset['success'], marker='s', label=tg, linewidth=1, markersize=3)
    axes[0, 1].set_xlabel('Test Date', fontsize=7)
    axes[0, 1].set_ylabel('Success Rate (%)', fontsize=7)
    axes[0, 1].set_title('Success Rate Trend', fontsize=8)
    axes[0, 1].legend(fontsize=6)
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].tick_params(axis='both', which='major', labelsize=6)
    
    # 吞吐量趋势
    for i, tg in enumerate(['TG1_HTTP Request', 'TG2_HTTP Request']):
        subset = result_df[result_df['tg'] == tg]
        axes[1, 0].plot(subset['label'], subset['throughput'], marker='^', label=tg, linewidth=1, markersize=3)
    axes[1, 0].set_xlabel('Test Date', fontsize=7)
    axes[1, 0].set_ylabel('Throughput (samples/sec)', fontsize=7)
    axes[1, 0].set_title('Throughput Trend', fontsize=8)
    axes[1, 0].legend(fontsize=6)
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].tick_params(axis='both', which='major', labelsize=6)
    
    # 性能对比柱状图
    latest_data = result_df.groupby('tg').last()
    x = range(len(latest_data))
    axes[1, 1].bar([i-0.2 for i in x], latest_data['avg_rt'], width=0.4, label='Response Time (ms)', alpha=0.7)
    axes[1, 1].set_xlabel('Thread Groups', fontsize=7)
    axes[1, 1].set_ylabel('Response Time (ms)', fontsize=7)
    axes[1, 1].set_title('Latest Performance Comparison', fontsize=8)
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(latest_data.index, rotation=45, fontsize=6)
    axes[1, 1].legend(fontsize=6)
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].tick_params(axis='both', which='major', labelsize=6)
    
    plt.tight_layout()
    plt.savefig(os.path.join(result_dir, 'performance_dashboard.png'), dpi=120, bbox_inches='tight')
    plt.close()

# 生成 dashboard.html
dashboard_template = """
<!DOCTYPE html>
<html>
<head>
    <title>JMeter Performance Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            box-sizing: border-box;
        }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 5px; 
            background-color: #f5f5f5;
            font-size: 12px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 15px;
            border-radius: 6px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        
        h1 { 
            color: #2c3e50; 
            text-align: center;
            border-bottom: 2px solid #3498db;
            padding-bottom: 6px;
            font-size: 18px;
            margin-bottom: 15px;
        }
        
        h2 { 
            color: #34495e; 
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 14px;
        }
        
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 10px 0;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px;
            border-radius: 6px;
            text-align: center;
        }
        
        .stat-card h3 {
            margin: 0 0 5px 0;
            font-size: 10px;
            opacity: 0.9;
        }
        
        .stat-card .value {
            font-size: 16px;
            font-weight: bold;
        }
        
        table { 
            border-collapse: collapse; 
            width: 100%; 
            margin: 10px 0;
            border-radius: 4px;
            overflow: hidden;
            box-shadow: 0 0 6px rgba(0,0,0,0.1);
            font-size: 10px;
        }
        
        th, td { 
            border: 1px solid #ddd; 
            padding: 6px; 
            text-align: center; 
        }
        
        th { 
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            font-weight: bold;
            font-size: 10px;
        }
        
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:hover { background-color: #f0f0f0; }
        
        img { 
            max-width: 400px; 
            height: auto;
            border-radius: 4px;
            box-shadow: 0 0 6px rgba(0,0,0,0.1);
            margin: 10px 0;
        }
        
        .compact-mode img {
            max-width: 300px;
        }
        
        .ultra-compact img {
            max-width: 250px;
        }
        
        .chart-container {
            text-align: center;
            margin: 15px 0;
        }
        
        .performance-insights {
            background: #e8f4fd;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            border-left: 2px solid #3498db;
            font-size: 11px;
        }
        
        .performance-insights ul {
            margin: 8px 0;
            padding-left: 15px;
        }
        
        .performance-insights li {
            margin: 3px 0;
        }
        
        /* 响应式设计 */
        @media (max-width: 768px) {
            .container {
                padding: 10px;
                margin: 3px;
            }
            
            .summary-stats {
                grid-template-columns: repeat(2, 1fr);
                gap: 8px;
            }
            
            .stat-card {
                padding: 8px;
            }
            
            .stat-card .value {
                font-size: 14px;
            }
            
            table {
                font-size: 9px;
            }
            
            th, td {
                padding: 4px;
            }
        }
        
        /* 紧凑模式 */
        .compact-mode {
            font-size: 10px;
        }
        
        .compact-mode .container {
            padding: 10px;
            max-width: 600px;
        }
        
        .compact-mode h1 {
            font-size: 16px;
            margin-bottom: 10px;
        }
        
        .compact-mode h2 {
            font-size: 12px;
            margin-top: 15px;
        }
        
        .compact-mode .summary-stats {
            gap: 8px;
        }
        
        .compact-mode .stat-card {
            padding: 8px;
        }
        
        .compact-mode .stat-card .value {
            font-size: 14px;
        }
        
        .compact-mode .performance-insights {
            padding: 8px;
            font-size: 10px;
        }
        
        /* 添加切换按钮 */
        .toggle-container {
            text-align: center;
            margin-bottom: 10px;
        }
        
        .toggle-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 10px;
            margin: 0 3px;
        }
        
        .toggle-btn:hover {
            background: #2980b9;
        }
        
        .toggle-btn.active {
            background: #27ae60;
        }
        
        /* 超紧凑模式 */
        .ultra-compact {
            font-size: 9px;
        }
        
        .ultra-compact .container {
            padding: 8px;
            max-width: 500px;
        }
        
        .ultra-compact h1 {
            font-size: 14px;
            margin-bottom: 8px;
        }
        
        .ultra-compact h2 {
            font-size: 11px;
            margin-top: 12px;
        }
        
        .ultra-compact .summary-stats {
            gap: 6px;
        }
        
        .ultra-compact .stat-card {
            padding: 6px;
        }
        
        .ultra-compact .stat-card .value {
            font-size: 12px;
        }
        
        .ultra-compact table {
            font-size: 8px;
        }
        
        .ultra-compact th, .ultra-compact td {
            padding: 3px;
        }
        
        .ultra-compact .performance-insights {
            padding: 6px;
            font-size: 9px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="toggle-container">
            <button class="toggle-btn active" onclick="toggleMode('normal')">标准</button>
            <button class="toggle-btn" onclick="toggleMode('compact')">紧凑</button>
            <button class="toggle-btn" onclick="toggleMode('ultra')">超紧凑</button>
        </div>
        
        <h1>🚀 JMeter Performance Dashboard</h1>
        
        <div class="summary-stats">
            <div class="stat-card">
                <h3>总测试次数</h3>
                <div class="value">{{ total_runs }}</div>
            </div>
            <div class="stat-card">
                <h3>平均响应时间</h3>
                <div class="value">{{ "%.1f"|format(avg_response_time) }} ms</div>
            </div>
            <div class="stat-card">
                <h3>成功率</h3>
                <div class="value">{{ "%.1f"|format(avg_success_rate) }}%</div>
            </div>
            <div class="stat-card">
                <h3>平均吞吐量</h3>
                <div class="value">{{ "%.1f"|format(avg_throughput) }} req/s</div>
            </div>
        </div>

        <div class="chart-container">
            <h2>📊 Performance Dashboard</h2>
            <img src="performance_dashboard.png" alt="Performance Dashboard" style="max-width: 400px; height: auto;">
        </div>

        <div class="performance-insights">
            <h2>💡 Performance Insights</h2>
            <ul>
                <li><strong>Response Time Improvement:</strong> From 3830ms (2025-07-22) to 760ms (2025-07-25) - 80% improvement!</li>
                <li><strong>Throughput Enhancement:</strong> TG2 throughput increased from 0.66 to 38.76 req/s - 5800% improvement!</li>
                <li><strong>Consistent Success Rate:</strong> 100% success rate maintained across all tests</li>
                <li><strong>Performance Stability:</strong> Both thread groups show consistent performance patterns</li>
            </ul>
        </div>

        <h2>📋 Raw Data</h2>
        <table>
            <tr>
                <th>Test File</th>
                <th>Thread Group</th>
                <th>Avg Response Time (ms)</th>
                <th>Success %</th>
                <th>Throughput (samples/sec)</th>
            </tr>
            {% for row in rows %}
            <tr>
                <td>{{ row.file }}</td>
                <td>{{ row.tg }}</td>
                <td>{{ "%.2f"|format(row.avg_rt) }}</td>
                <td>{{ "%.2f"|format(row.success) }}</td>
                <td>{{ "%.2f"|format(row.throughput) }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    
    <script>
        function toggleMode(mode) {
            const body = document.body;
            const buttons = document.querySelectorAll('.toggle-btn');
            
            // 移除所有模式类
            body.classList.remove('compact-mode', 'ultra-compact');
            
            // 移除所有按钮的active类
            buttons.forEach(btn => btn.classList.remove('active'));
            
            // 添加选中的模式
            if (mode === 'compact') {
                body.classList.add('compact-mode');
                buttons[1].classList.add('active');
            } else if (mode === 'ultra') {
                body.classList.add('ultra-compact');
                buttons[2].classList.add('active');
            } else {
                buttons[0].classList.add('active');
            }
        }
        
        // 自动检测窗口大小并调整
        function adjustLayout() {
            if (window.innerWidth < 600) {
                toggleMode('ultra');
            } else if (window.innerWidth < 900) {
                toggleMode('compact');
            } else {
                toggleMode('normal');
            }
        }
        
        // 页面加载时调整
        window.addEventListener('load', adjustLayout);
        window.addEventListener('resize', adjustLayout);
    </script>
</body>
</html>
"""

# 计算统计信息
if not result_df.empty:
    total_runs = len(result_df)
    avg_response_time = result_df['avg_rt'].mean()
    avg_success_rate = result_df['success'].mean()
    avg_throughput = result_df['throughput'].mean()
else:
    total_runs = 0
    avg_response_time = 0
    avg_success_rate = 0
    avg_throughput = 0

output_path = os.path.join(result_dir, 'dashboard.html')
os.makedirs(result_dir, exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(Template(dashboard_template).render(
        rows=results,
        total_runs=total_runs,
        avg_response_time=avg_response_time,
        avg_success_rate=avg_success_rate,
        avg_throughput=avg_throughput
    ))

print('Dashboard generated: compare_results/dashboard.html')
print(f'Total test runs analyzed: {total_runs}')
print(f'Average response time: {avg_response_time:.1f} ms')
print(f'Average success rate: {avg_success_rate:.1f}%')
print(f'Average throughput: {avg_throughput:.1f} req/s')