import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# 结果文件目录
result_dir = 'compare_results'
files = sorted(glob.glob(os.path.join(result_dir, '*.csv')))

tg1_avgs = []
tg2_avgs = []
builds = []

for i, file in enumerate(files):
    try:
        df = pd.read_csv(file)
        # 适配你的 label 名称
        tg1 = df[df['label'] == 'TG1_HTTP Request']
        tg2 = df[df['label'] == 'TG2_HTTP Request']
        tg1_avgs.append(tg1['elapsed'].mean() if not tg1.empty else 0)
        tg2_avgs.append(tg2['elapsed'].mean() if not tg2.empty else 0)
        builds.append(f'#{i+1}')
    except Exception as e:
        print(f"Error processing {file}: {e}")

plt.figure(figsize=(10,6))
plt.plot(builds, tg1_avgs, marker='o', label='TG1 Avg')
plt.plot(builds, tg2_avgs, marker='o', label='TG2 Avg')
plt.xlabel('Build')
plt.ylabel('Avg Response Time (ms)')
plt.title('TG1 vs TG2 Avg Response Time Across Builds')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(result_dir, 'tg_compare.png'))
print('对比图已生成：compare_results/tg_compare.png')