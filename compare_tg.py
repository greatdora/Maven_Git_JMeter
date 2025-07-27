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
    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('JMeter Performance Analysis Dashboard', fontsize=16, fontweight='bold')
    
    # 响应时间趋势
    for i, tg in enumerate(['TG1_HTTP Request', 'TG2_HTTP Request']):
        subset = result_df[result_df['tg'] == tg]
        axes[0, 0].plot(subset['label'], subset['avg_rt'], marker='o', label=tg, linewidth=2, markersize=8)
    axes[0, 0].set_xlabel('Test Date')
    axes[0, 0].set_ylabel('Average Response Time (ms)')
    axes[0, 0].set_title('Response Time Trend')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 成功率趋势
    for i, tg in enumerate(['TG1_HTTP Request', 'TG2_HTTP Request']):
        subset = result_df[result_df['tg'] == tg]
        axes[0, 1].plot(subset['label'], subset['success'], marker='s', label=tg, linewidth=2, markersize=8)
    axes[0, 1].set_xlabel('Test Date')
    axes[0, 1].set_ylabel('Success Rate (%)')
    axes[0, 1].set_title('Success Rate Trend')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 吞吐量趋势
    for i, tg in enumerate(['TG1_HTTP Request', 'TG2_HTTP Request']):
        subset = result_df[result_df['tg'] == tg]
        axes[1, 0].plot(subset['label'], subset['throughput'], marker='^', label=tg, linewidth=2, markersize=8)
    axes[1, 0].set_xlabel('Test Date')
    axes[1, 0].set_ylabel('Throughput (samples/sec)')
    axes[1, 0].set_title('Throughput Trend')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 性能对比柱状图
    latest_data = result_df.groupby('tg').last()
    x = range(len(latest_data))
    axes[1, 1].bar([i-0.2 for i in x], latest_data['avg_rt'], width=0.4, label='Response Time (ms)', alpha=0.7)
    axes[1, 1].set_xlabel('Thread Groups')
    axes[1, 1].set_ylabel('Response Time (ms)')
    axes[1, 1].set_title('Latest Performance Comparison')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(latest_data.index, rotation=45)
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(result_dir, 'performance_dashboard.png'), dpi=300, bbox_inches='tight')
    plt.close()

# 生成 dashboard.html
dashboard_template = """
<!DOCTYPE html>
<html>
<head>
    <title>JMeter Performance Dashboard</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #2c3e50; 
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 { 
            color: #34495e; 
            margin-top: 30px;
        }
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-card h3 {
            margin: 0 0 10px 0;
            font-size: 14px;
            opacity: 0.9;
        }
        .stat-card .value {
            font-size: 24px;
            font-weight: bold;
        }
        table { 
            border-collapse: collapse; 
            width: 100%; 
            margin: 20px 0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 12px; 
            text-align: center; 
        }
        th { 
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:hover { background-color: #f0f0f0; }
        img { 
            max-width: 100%; 
            height: auto;
            border-radius: 8px;
            box-shadow: 0 0 15px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        .chart-container {
            text-align: center;
            margin: 30px 0;
        }
        .performance-insights {
            background: #e8f4fd;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #3498db;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 JMeter Performance Dashboard</h1>
        
        <div class="summary-stats">
            <div class="stat-card">
                <h3>Total Test Runs</h3>
                <div class="value">{{ total_runs }}</div>
            </div>
            <div class="stat-card">
                <h3>Average Response Time</h3>
                <div class="value">{{ "%.1f"|format(avg_response_time) }} ms</div>
            </div>
            <div class="stat-card">
                <h3>Success Rate</h3>
                <div class="value">{{ "%.1f"|format(avg_success_rate) }}%</div>
            </div>
            <div class="stat-card">
                <h3>Average Throughput</h3>
                <div class="value">{{ "%.1f"|format(avg_throughput) }} req/s</div>
            </div>
        </div>

        <div class="chart-container">
            <h2>📊 Performance Dashboard</h2>
            <img src="performance_dashboard.png" alt="Performance Dashboard">
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