# -*- coding: utf-8 -*-
"""
Module 3: User Behavior Analysis
Output: figures/behavior_daily_trend.png
"""
import pandas as pd, numpy as np, os, glob, warnings
warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(root, 'data')
fig_dir = os.path.join(root, 'figures')
os.makedirs(fig_dir, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

COLORS = {'pv':'#5B9BD5','fav':'#FFC000','cart':'#ED7D31','buy':'#70AD47'}

df = pd.read_csv(os.path.join(data_dir,'cleaned_data.csv'), parse_dates=['datetime'])
print("="*50)
print("Module 3: User Behavior Analysis")
print("="*50)

# Behavior count
beh = df['behavior'].value_counts()
beh_pct = df['behavior'].value_counts(normalize=True)*100
for b in ['pv','fav','cart','buy']:
    print(f"  {b}: {beh.get(b,0):,} ({beh_pct.get(b,0):.2f}%)")

# Users per behavior
user_beh = df.groupby(['user_id','behavior']).size().reset_index(name='c')
up = user_beh.pivot_table(index='user_id',columns='behavior',values='c',fill_value=0)
for b in ['pv','fav','cart','buy']:
    if b in up.columns:
        n = (up[b]>0).sum(); avg = up[b].mean()
        print(f"  Users with {b}: {n:,} ({n/len(up)*100:.1f}%), avg {avg:.1f} times")

# Daily behavior trend chart
daily_beh = df.groupby(['date','behavior']).size().reset_index(name='count')
daily_beh['date'] = pd.to_datetime(daily_beh['date'])

fig, ax = plt.subplots(figsize=(16,6))
for b in ['pv','fav','cart','buy']:
    d = daily_beh[daily_beh['behavior']==b]
    ax.plot(d['date'],d['count'],color=COLORS[b],label=b,linewidth=1.5,alpha=0.8)
ax.set_title('每日用户行为趋势',fontsize=14,fontweight='bold')
ax.set_xlabel('日期',fontsize=12); ax.set_ylabel('数量',fontsize=12)
ax.legend(fontsize=11); ax.grid(True,alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(fig_dir,'behavior_daily_trend.png'),dpi=150)
plt.close()
print("\n  -> figures/behavior_daily_trend.png")
print("Module 3 complete.")
