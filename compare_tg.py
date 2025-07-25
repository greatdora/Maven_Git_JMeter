import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from jinja2 import Template

# result_dir = '/data/compare_results'  # 注释掉这行
result_dir = 'compare_results'          # 用相对路径
files = sorted(glob.glob(os.path.join(result_dir, '*.csv')))
results = []

for file in files:
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
                'file': os.path.basename(file),
                'tg': tg,
                'avg_rt': avg_rt,
                'success': success,
                'throughput': throughput
            })

result_df = pd.DataFrame(results)
if not result_df.empty:
    for metric, ylabel, title in [
        ('avg_rt', 'Avg Response Time (ms)', 'Response Time Trend'),
        ('success', 'Success %', 'Success Rate Trend'),
        ('throughput', 'Throughput (samples/sec)', 'Throughput Trend')
    ]:
        plt.figure(figsize=(12,6))
        for tg in ['TG1_HTTP Request', 'TG2_HTTP Request']:
            subset = result_df[result_df['tg'] == tg]
            plt.plot(subset['file'], subset[metric], marker='o', label=tg)
        plt.xlabel('Test File')
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(result_dir, f'{metric}_trend.png'))
        plt.close()

# 生成 dashboard.html
dashboard_template = """
<html>
<head>
    <title>JMeter Performance Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; }
        h1 { color: #2c3e50; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
        th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: center; }
        th { background: #f4f4f4; }
        img { margin-bottom: 30px; }
    </style>
</head>
<body>
    <h1>JMeter Performance Dashboard</h1>
    <h2>Response Time Trend</h2>
    <img src="avg_rt_trend.png" width="800">
    <h2>Success Rate Trend</h2>
    <img src="success_trend.png" width="800">
    <h2>Throughput Trend</h2>
    <img src="throughput_trend.png" width="800">
    <h2>Raw Data</h2>
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
</body>
</html>
"""

output_path = os.path.join(result_dir, 'dashboard.html')
os.makedirs(result_dir, exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(Template(dashboard_template).render(rows=results))

print('Dashboard generated: compare_results/dashboard.html')