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

# 移除硬编码的历史数据，只使用真实的CSV文件数据
additional_data = []

# 处理CSV文件
for file in files:
    # 从文件名提取日期
    base = os.path.basename(file)
    date_part = base.split('-')[0]
    dt = datetime.datetime.now()
    label = f"{date_part}_{dt.strftime('%H%M')}"

    df = pd.read_csv(file)
    # 按线程组名称分组
    unique_thread_groups = df['threadName'].str.extract(r'(Get_\d+|Post_\d+|Put_\d+)')[0].unique()
    for tg in unique_thread_groups:
        if pd.notna(tg):  # 确保不是NaN
            tg_df = df[df['threadName'].str.contains(tg, na=False)]
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
    
    # 获取所有唯一的线程组名称
    unique_thread_groups = result_df['tg'].unique()
    
    # 按HTTP方法分组颜色
    colors = {'Get_01': 'blue', 'Get_02': 'lightblue', 
              'Post_01': 'green', 'Post_02': 'lightgreen',
              'Put_01': 'red', 'Put_02': 'pink'}
    
    # 响应时间趋势
    for tg in unique_thread_groups:
        subset = result_df[result_df['tg'] == tg]
        color = colors.get(tg, 'gray')
        axes[0, 0].plot(subset['label'], subset['avg_rt'], marker='o', label=tg, 
                        linewidth=1, markersize=3, color=color)
    axes[0, 0].set_xlabel('Test Date', fontsize=7)
    axes[0, 0].set_ylabel('Average Response Time (ms)', fontsize=7)
    axes[0, 0].set_title('Response Time Trend', fontsize=8)
    axes[0, 0].legend(fontsize=6)
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].tick_params(axis='both', which='major', labelsize=6)
    
    # 成功率趋势
    for tg in unique_thread_groups:
        subset = result_df[result_df['tg'] == tg]
        color = colors.get(tg, 'gray')
        axes[0, 1].plot(subset['label'], subset['success'], marker='s', label=tg, 
                        linewidth=1, markersize=3, color=color)
    axes[0, 1].set_xlabel('Test Date', fontsize=7)
    axes[0, 1].set_ylabel('Success Rate (%)', fontsize=7)
    axes[0, 1].set_title('Success Rate Trend', fontsize=8)
    axes[0, 1].legend(fontsize=6)
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].tick_params(axis='both', which='major', labelsize=6)
    
    # 吞吐量趋势
    for tg in unique_thread_groups:
        subset = result_df[result_df['tg'] == tg]
        color = colors.get(tg, 'gray')
        axes[1, 0].plot(subset['label'], subset['throughput'], marker='^', label=tg, 
                        linewidth=1, markersize=3, color=color)
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
    
    # 生成过滤的图表
    print("生成过滤的图表...")
    
    # 生成不同过滤的图表
    def generate_filtered_chart(result_df, selected_groups, result_dir):
        """根据选中的线程组生成过滤后的图表"""
        if result_df.empty or not selected_groups:
            return None
        
        # 过滤数据
        filtered_df = result_df[result_df['tg'].isin(selected_groups)]
        
        if filtered_df.empty:
            return None
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(8, 6))
        fig.suptitle(f'JMeter Performance Analysis - {", ".join(selected_groups)}', fontsize=10, fontweight='bold')
        
        # 按HTTP方法分组颜色
        colors = {'Get_01': 'blue', 'Get_02': 'lightblue', 
                  'Post_01': 'green', 'Post_02': 'lightgreen',
                  'Put_01': 'red', 'Put_02': 'pink'}
        
        # 响应时间趋势
        for tg in selected_groups:
            subset = filtered_df[filtered_df['tg'] == tg]
            color = colors.get(tg, 'gray')
            axes[0, 0].plot(subset['label'], subset['avg_rt'], marker='o', label=tg, 
                            linewidth=1, markersize=3, color=color)
        axes[0, 0].set_xlabel('Test Date', fontsize=7)
        axes[0, 0].set_ylabel('Average Response Time (ms)', fontsize=7)
        axes[0, 0].set_title('Response Time Trend', fontsize=8)
        axes[0, 0].legend(fontsize=6)
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='both', which='major', labelsize=6)
        
        # 成功率趋势
        for tg in selected_groups:
            subset = filtered_df[filtered_df['tg'] == tg]
            color = colors.get(tg, 'gray')
            axes[0, 1].plot(subset['label'], subset['success'], marker='s', label=tg, 
                            linewidth=1, markersize=3, color=color)
        axes[0, 1].set_xlabel('Test Date', fontsize=7)
        axes[0, 1].set_ylabel('Success Rate (%)', fontsize=7)
        axes[0, 1].set_title('Success Rate Trend', fontsize=8)
        axes[0, 1].legend(fontsize=6)
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].tick_params(axis='both', which='major', labelsize=6)
        
        # 吞吐量趋势
        for tg in selected_groups:
            subset = filtered_df[filtered_df['tg'] == tg]
            color = colors.get(tg, 'gray')
            axes[1, 0].plot(subset['label'], subset['throughput'], marker='^', label=tg, 
                            linewidth=1, markersize=3, color=color)
        axes[1, 0].set_xlabel('Test Date', fontsize=7)
        axes[1, 0].set_ylabel('Throughput (samples/sec)', fontsize=7)
        axes[1, 0].set_title('Throughput Trend', fontsize=8)
        axes[1, 0].legend(fontsize=6)
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].tick_params(axis='both', which='major', labelsize=6)
        
        # 性能对比柱状图
        latest_data = filtered_df.groupby('tg').last()
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
        
        # 生成文件名
        groups_str = '_'.join(selected_groups).replace(' ', '_')
        filename = f'performance_dashboard_{groups_str}.png'
        filepath = os.path.join(result_dir, filename)
        
        plt.savefig(filepath, dpi=120, bbox_inches='tight')
        plt.close()
        
        return filename
    
    # 生成所有可能的过滤图表
    def generate_all_filtered_charts(result_df, result_dir):
        """生成所有可能的过滤图表组合"""
        all_groups = result_df['tg'].unique().tolist()
        chart_files = {}
        
        # 生成单个线程组的图表
        for group in all_groups:
            filename = generate_filtered_chart(result_df, [group], result_dir)
            if filename:
                chart_files[group] = filename
        
        # 生成GET组合的图表
        get_groups = [g for g in all_groups if g.startswith('Get')]
        if len(get_groups) > 1:
            filename = generate_filtered_chart(result_df, get_groups, result_dir)
            if filename:
                chart_files['Get_Only'] = filename
        
        # 生成POST组合的图表
        post_groups = [g for g in all_groups if g.startswith('Post')]
        if len(post_groups) > 1:
            filename = generate_filtered_chart(result_df, post_groups, result_dir)
            if filename:
                chart_files['Post_Only'] = filename
        
        # 生成PUT组合的图表
        put_groups = [g for g in all_groups if g.startswith('Put')]
        if len(put_groups) > 1:
            filename = generate_filtered_chart(result_df, put_groups, result_dir)
            if filename:
                chart_files['Put_Only'] = filename
        
        return chart_files
    
    filtered_charts = generate_all_filtered_charts(result_df, result_dir)
    print(f"生成了 {len(filtered_charts)} 个过滤图表")



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
            font-size: 11px;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 12px;
            border-radius: 6px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        
        h1 { 
            color: #2c3e50; 
            text-align: center;
            border-bottom: 2px solid #3498db;
            padding-bottom: 6px;
            font-size: 16px;
            margin-bottom: 12px;
        }
        
        .controls {
            background: #ecf0f1;
            padding: 8px;
            border-radius: 4px;
            margin-bottom: 12px;
            border: 1px solid #bdc3c7;
        }
        
        .controls h3 {
            margin: 0 0 8px 0;
            font-size: 12px;
            color: #2c3e50;
        }
        
        .checkbox-group {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .checkbox-item {
            display: flex;
            align-items: center;
            font-size: 10px;
        }
        
        .checkbox-item input[type="checkbox"] {
            margin-right: 4px;
        }
        
        .checkbox-item label {
            cursor: pointer;
            user-select: none;
        }
        
        .btn-group {
            margin-top: 8px;
            display: flex;
            gap: 6px;
        }
        
        .btn {
            padding: 4px 8px;
            border: none;
            border-radius: 3px;
            font-size: 10px;
            cursor: pointer;
            background: #3498db;
            color: white;
        }
        
        .btn:hover {
            background: #2980b9;
        }
        
        .btn.secondary {
            background: #95a5a6;
        }
        
        .btn.secondary:hover {
            background: #7f8c8d;
        }
        
        .performance-image {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 8px;
            margin: 12px 0;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px;
            border-radius: 4px;
            text-align: center;
            font-size: 10px;
        }
        
        .stat-value {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 2px;
        }
        
        .insights {
            background: #e8f5e8;
            border-left: 4px solid #27ae60;
            padding: 8px;
            margin: 12px 0;
            border-radius: 0 4px 4px 0;
            font-size: 10px;
        }
        
        .insights h4 {
            margin: 0 0 4px 0;
            color: #27ae60;
            font-size: 11px;
        }
        
        .insights ul {
            margin: 4px 0;
            padding-left: 16px;
        }
        
        .insights li {
            margin: 2px 0;
        }
        
        .hidden {
            display: none !important;
        }
        
        .chart-container {
            position: relative;
            margin: 12px 0;
        }
        
        .chart-overlay {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            font-size: 12px;
            color: #666;
            display: none;
        }
        
        .selection-status {
            background: #e8f5e8;
            border: 1px solid #27ae60;
            border-radius: 4px;
            padding: 8px;
            margin: 8px 0;
            font-size: 11px;
            color: #27ae60;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>JMeter Performance Analysis Dashboard</h1>
        
        <div class="controls">
            <h3>选择要显示的线程组：</h3>
            <div class="checkbox-group" id="threadGroupSelectors">
                <div class="checkbox-item">
                    <input type="checkbox" id="Get_01" value="Get_01" checked>
                    <label for="Get_01">Get_01</label>
                </div>
                <div class="checkbox-item">
                    <input type="checkbox" id="Get_02" value="Get_02" checked>
                    <label for="Get_02">Get_02</label>
                </div>
                <div class="checkbox-item">
                    <input type="checkbox" id="Post_01" value="Post_01" checked>
                    <label for="Post_01">Post_01</label>
                </div>
                <div class="checkbox-item">
                    <input type="checkbox" id="Post_02" value="Post_02" checked>
                    <label for="Post_02">Post_02</label>
                </div>
                <div class="checkbox-item">
                    <input type="checkbox" id="Put_01" value="Put_01" checked>
                    <label for="Put_01">Put_01</label>
                </div>
                <div class="checkbox-item">
                    <input type="checkbox" id="Put_02" value="Put_02" checked>
                    <label for="Put_02">Put_02</label>
                </div>
            </div>
            <div class="btn-group">
                <button class="btn" onclick="selectAll()">全选</button>
                <button class="btn secondary" onclick="selectNone()">全不选</button>
                <button class="btn" onclick="selectGetOnly()">仅GET</button>
                <button class="btn" onclick="selectPostOnly()">仅POST</button>
                <button class="btn" onclick="selectPutOnly()">仅PUT</button>
            </div>
        </div>
        
        <div class="selection-status" id="selectionStatus">
            <strong>当前显示:</strong> 所有线程组
        </div>
        
        <div class="chart-container">
            <img src="performance_dashboard.png" alt="Performance Dashboard" class="performance-image" id="dashboardImage">
            <div class="chart-overlay" id="noDataOverlay">
                请至少选择一个线程组来显示数据
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{{ total_runs }}</div>
                <div>测试运行次数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ "%.1f"|format(avg_response_time) }} ms</div>
                <div>平均响应时间</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ "%.1f"|format(avg_success_rate) }}%</div>
                <div>平均成功率</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ "%.1f"|format(avg_throughput) }} req/s</div>
                <div>平均吞吐量</div>
            </div>
        </div>
        
        <div class="insights">
            <h4>性能分析洞察</h4>
            <ul>
                <li>响应时间分析：{{ response_time_insight }}</li>
                <li>成功率分析：{{ success_rate_insight }}</li>
                <li>吞吐量分析：{{ throughput_insight }}</li>
                <li>建议：{{ recommendation }}</li>
            </ul>
        </div>
    </div>
    
    <script>
        // 获取所有复选框
        const checkboxes = document.querySelectorAll('#threadGroupSelectors input[type="checkbox"]');
        const dashboardImage = document.getElementById('dashboardImage');
        const noDataOverlay = document.getElementById('noDataOverlay');
        const selectionStatus = document.getElementById('selectionStatus');
        
        // 监听复选框变化
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateDisplay);
        });
        
        function updateDisplay() {
            const selectedGroups = Array.from(checkboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);
            
            console.log('updateDisplay called, selected groups:', selectedGroups);
            
            if (selectedGroups.length === 0) {
                dashboardImage.classList.add('hidden');
                noDataOverlay.style.display = 'block';
                selectionStatus.style.display = 'none';
                console.log('No groups selected, hiding image');
            } else {
                dashboardImage.classList.remove('hidden');
                noDataOverlay.style.display = 'none';
                selectionStatus.style.display = 'block';
                console.log('Groups selected, showing filtered image');
                
                // 更新状态显示
                selectionStatus.innerHTML = `<strong>当前显示:</strong> ${selectedGroups.join(', ')}`;
                
                // 动态更新图表
                updateChartImage(selectedGroups);
            }
        }
        
        function selectAll() {
            checkboxes.forEach(cb => cb.checked = true);
            updateDisplay();
        }
        
        function selectNone() {
            checkboxes.forEach(cb => cb.checked = false);
            updateDisplay();
        }
        
        function selectGetOnly() {
            checkboxes.forEach(cb => {
                cb.checked = cb.value.startsWith('Get');
            });
            updateDisplay();
        }
        
        function selectPostOnly() {
            checkboxes.forEach(cb => {
                cb.checked = cb.value.startsWith('Post');
            });
            updateDisplay();
        }
        
        function selectPutOnly() {
            checkboxes.forEach(cb => {
                cb.checked = cb.value.startsWith('Put');
            });
            updateDisplay();
        }
        
        function updateChartImage(selectedGroups) {
            // 根据选中的线程组选择对应的图表
            let chartFile = 'performance_dashboard.png'; // 默认显示全部
            
            if (selectedGroups.length === 1) {
                // 单个线程组
                const group = selectedGroups[0];
                chartFile = `performance_dashboard_${group}.png`;
            } else if (selectedGroups.length === 2) {
                // 检查是否是GET、POST或PUT组合
                const isGetOnly = selectedGroups.every(g => g.startsWith('Get'));
                const isPostOnly = selectedGroups.every(g => g.startsWith('Post'));
                const isPutOnly = selectedGroups.every(g => g.startsWith('Put'));
                
                if (isGetOnly) {
                    chartFile = 'performance_dashboard_Get_Only.png';
                } else if (isPostOnly) {
                    chartFile = 'performance_dashboard_Post_Only.png';
                } else if (isPutOnly) {
                    chartFile = 'performance_dashboard_Put_Only.png';
                }
            }
            
            // 更新图表
            const timestamp = new Date().getTime();
            dashboardImage.src = chartFile + '?t=' + timestamp;
            
            // 如果图表加载失败，回退到默认图表
            dashboardImage.onerror = function() {
                console.log('Filtered chart not found, using default chart');
                dashboardImage.src = 'performance_dashboard.png?t=' + timestamp;
            };
        }
        
        // 初始化显示
        updateDisplay();
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
    
    # 生成洞察
    if len(result_df) > 1:
        # 计算趋势
        latest_rt = result_df.groupby('tg')['avg_rt'].last().mean()
        earliest_rt = result_df.groupby('tg')['avg_rt'].first().mean()
        rt_trend = "改善" if latest_rt < earliest_rt else "下降" if latest_rt > earliest_rt else "稳定"
        
        latest_tp = result_df.groupby('tg')['throughput'].last().mean()
        earliest_tp = result_df.groupby('tg')['throughput'].first().mean()
        tp_trend = "提升" if latest_tp > earliest_tp else "下降" if latest_tp < earliest_tp else "稳定"
        
        response_time_insight = f"响应时间{rt_trend}，从{earliest_rt:.0f}ms到{latest_rt:.0f}ms"
        throughput_insight = f"吞吐量{tp_trend}，从{earliest_tp:.1f}到{latest_tp:.1f} req/s"
    else:
        response_time_insight = f"响应时间平均{avg_response_time:.0f}ms，在预期范围内"
        throughput_insight = f"吞吐量平均{avg_throughput:.1f} req/s，性能良好"
    
    success_rate_insight = f"成功率{avg_success_rate:.1f}%，表现{'优秀' if avg_success_rate >= 95 else '良好' if avg_success_rate >= 90 else '需要关注'}"
    
    # 生成建议
    if avg_response_time > 2000:
        recommendation = "响应时间较高，建议优化系统性能或增加服务器资源"
    elif avg_success_rate < 95:
        recommendation = "成功率偏低，建议检查系统稳定性或网络连接"
    elif avg_throughput < 5:
        recommendation = "吞吐量偏低，建议优化并发配置或系统架构"
    else:
        recommendation = "系统性能良好，建议继续监控并定期测试"
else:
    total_runs = 0
    avg_response_time = 0
    avg_success_rate = 0
    avg_throughput = 0
    response_time_insight = "暂无数据"
    success_rate_insight = "暂无数据"
    throughput_insight = "暂无数据"
    recommendation = "暂无建议"

output_path = os.path.join(result_dir, 'dashboard.html')
os.makedirs(result_dir, exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(Template(dashboard_template).render(
        total_runs=total_runs,
        avg_response_time=avg_response_time,
        avg_success_rate=avg_success_rate,
        avg_throughput=avg_throughput,
        response_time_insight=response_time_insight,
        success_rate_insight=success_rate_insight,
        throughput_insight=throughput_insight,
        recommendation=recommendation
    ))

print('Dashboard generated: compare_results/dashboard.html')
print(f'Total test runs analyzed: {total_runs}')
print(f'Average response time: {avg_response_time:.1f} ms')
print(f'Average success rate: {avg_success_rate:.1f}%')
print(f'Average throughput: {avg_throughput:.1f} req/s')
print(f'Average throughput: {avg_throughput:.1f} req/s')