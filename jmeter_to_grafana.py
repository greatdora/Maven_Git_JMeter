#!/usr/bin/env python3
"""
JMeter to Grafana Data Integration Script
将JMeter CSV数据转换为Grafana可用的格式
"""

import pandas as pd
import json
import time
import requests
from datetime import datetime
import os

class JMeterToGrafana:
    def __init__(self, grafana_url="http://localhost:3000", api_key=None):
        self.grafana_url = grafana_url
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}' if api_key else None
        }
    
    def process_jmeter_csv(self, csv_file):
        """处理JMeter CSV文件，提取性能指标"""
        df = pd.read_csv(csv_file)
        
        # 提取线程组名称
        df['threadGroup'] = df['threadName'].str.extract(r'(Get_\d+|Post_\d+|Put_\d+)')[0]
        
        # 按线程组聚合数据
        metrics = []
        for tg in df['threadGroup'].dropna().unique():
            tg_df = df[df['threadGroup'] == tg]
            
            # 计算性能指标
            avg_response_time = tg_df['elapsed'].mean()
            success_rate = tg_df['success'].mean() * 100
            
            # 计算吞吐量
            if len(tg_df) > 1:
                duration = (tg_df['timeStamp'].max() - tg_df['timeStamp'].min()) / 1000
                throughput = len(tg_df) / duration if duration > 0 else 0
            else:
                throughput = 0
            
            # 创建时间戳
            timestamp = int(time.time() * 1000)
            
            # 添加指标
            metrics.extend([
                {
                    "metric": "jmeter_response_time",
                    "value": avg_response_time,
                    "timestamp": timestamp,
                    "tags": {
                        "thread_group": tg,
                        "test_file": os.path.basename(csv_file)
                    }
                },
                {
                    "metric": "jmeter_success_rate",
                    "value": success_rate,
                    "timestamp": timestamp,
                    "tags": {
                        "thread_group": tg,
                        "test_file": os.path.basename(csv_file)
                    }
                },
                {
                    "metric": "jmeter_throughput",
                    "value": throughput,
                    "timestamp": timestamp,
                    "tags": {
                        "thread_group": tg,
                        "test_file": os.path.basename(csv_file)
                    }
                }
            ])
        
        return metrics
    
    def send_to_grafana(self, metrics):
        """发送数据到Grafana（通过InfluxDB或其他数据源）"""
        # 这里需要根据你的数据源配置来发送数据
        # 示例：发送到InfluxDB
        influx_data = []
        for metric in metrics:
            influx_data.append({
                "measurement": metric["metric"],
                "tags": metric["tags"],
                "time": metric["timestamp"],
                "fields": {
                    "value": metric["value"]
                }
            })
        
        return influx_data
    
    def create_grafana_dashboard(self, dashboard_config):
        """创建Grafana Dashboard"""
        if not self.api_key:
            print("Warning: No API key provided, cannot create dashboard")
            return False
        
        try:
            response = requests.post(
                f"{self.grafana_url}/api/dashboards/db",
                headers=self.headers,
                json=dashboard_config
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Dashboard created successfully: {result['url']}")
                return True
            else:
                print(f"Failed to create dashboard: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Error creating dashboard: {e}")
            return False

def main():
    """主函数"""
    # 配置
    grafana_url = "http://localhost:3000"  # Grafana URL
    api_key = None  # 你的Grafana API key
    
    # 创建转换器
    converter = JMeterToGrafana(grafana_url, api_key)
    
    # 处理JMeter CSV文件
    csv_files = [
        "compare_results/20250727_2350-simple_test.csv"
    ]
    
    all_metrics = []
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            print(f"Processing {csv_file}...")
            metrics = converter.process_jmeter_csv(csv_file)
            all_metrics.extend(metrics)
            print(f"Extracted {len(metrics)} metrics from {csv_file}")
        else:
            print(f"File not found: {csv_file}")
    
    # 显示提取的指标
    print(f"\nTotal metrics extracted: {len(all_metrics)}")
    for metric in all_metrics[:5]:  # 显示前5个指标
        print(f"  {metric['metric']}: {metric['value']} ({metric['tags']['thread_group']})")
    
    # 创建Grafana dashboard配置
    with open('grafana_dashboard.json', 'r') as f:
        dashboard_config = json.load(f)
    
    # 尝试创建dashboard
    if converter.create_grafana_dashboard(dashboard_config):
        print("Grafana dashboard created successfully!")
    else:
        print("Could not create dashboard (API key may be required)")
        print("You can manually import the grafana_dashboard.json file")

if __name__ == "__main__":
    main() 