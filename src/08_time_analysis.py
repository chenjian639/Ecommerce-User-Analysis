# -*- coding: utf-8 -*-
"""
Module 8: Time Pattern Analysis
Output: figures/time_heatmaps.png, figures/hourly_pv_vs_buy.png
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

df = pd.read_csv(os.path.join(data_dir,'cleaned_data.csv'),
    parse_dates=['datetime'], usecols=['behavior','datetime','hour','weekday_name'])
df['wd_num'] = df['datetime'].dt.dayofweek
print("="*50)
print("Module 8: Time Analysis")
print("="*50)

# Peak hours per behavior
hour_beh = df.groupby(['hour','behavior'],observed=True).size().reset_index(name='count')
print("Hourly peaks:")
for b in ['pv','fav','cart','buy']:
    d = hour_beh[hour_beh['behavior']==b]
    pk = d.loc[d['count'].idxmax()]
    print(f"  {b} peak: {int(pk['hour']):02d}:00 ({pk['count']:,})")

# Chart 1: 4 heatmaps (hour x weekday per behavior)
fig, axes = plt.subplots(2,2,figsize=(16,12))
titles = [('PV 浏览','pv'),('FAV 收藏','fav'),('CART 加购','cart'),('BUY 购买','buy')]
for idx,(title,b) in enumerate(titles):
    ax = axes[idx//2,idx%2]
    d = df[df['behavior']==b].groupby(['wd_num','hour'],observed=True).size().reset_index(name='count')
    piv = d.pivot_table(index='wd_num',columns='hour',values='count',fill_value=0)
    full = pd.DataFrame(0,index=range(7),columns=range(24))
    for r in piv.index:
        for c in piv.columns:
            full.loc[r,c] = piv.loc[r,c]
    im = ax.imshow(full.values,aspect='auto',cmap='YlOrRd')
    ax.set_xticks(range(0,24,3)); ax.set_yticks(range(7))
    ax.set_yticklabels(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])
    ax.set_title(f'{title} 活跃热力图',fontsize=12,fontweight='bold')
    ax.set_xlabel('小时 Hour')
    plt.colorbar(im,ax=ax,shrink=0.6)
plt.suptitle('用户行为热力图: 星期 x 小时',fontsize=15,fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(fig_dir,'time_heatmaps.png'),dpi=150,bbox_inches='tight')
plt.close()
print("  -> figures/time_heatmaps.png")

# Chart 2: PV vs Buy dual-axis
hpv = hour_beh[hour_beh['behavior']=='pv'].set_index('hour')['count']
hby = hour_beh[hour_beh['behavior']=='buy'].set_index('hour')['count']

fig, ax1 = plt.subplots(figsize=(14,6))
ax1.bar(range(24),hpv.values,color='#5B9BD5',alpha=0.6,label='PV 浏览')
ax1.set_xlabel('小时 Hour',fontsize=12)
ax1.set_ylabel('浏览 PV',fontsize=12,color='#5B9BD5')
ax1.tick_params(axis='y',labelcolor='#5B9BD5')
ax2 = ax1.twinx()
ax2.plot(range(24),hby.values,color='#70AD47',marker='o',linewidth=2.5,label='购买 Buy')
ax2.set_ylabel('购买 Purchases',fontsize=12,color='#70AD47')
ax2.tick_params(axis='y',labelcolor='#70AD47')
l1,lb1 = ax1.get_legend_handles_labels()
l2,lb2 = ax2.get_legend_handles_labels()
ax1.legend(l1+l2,lb1+lb2,loc='upper right')
ax1.set_title('每小时浏览量与购买量对比',fontsize=14,fontweight='bold')
ax1.set_xticks(range(0,24,2)); ax1.grid(True,alpha=0.3,axis='x')
plt.tight_layout()
plt.savefig(os.path.join(fig_dir,'hourly_pv_vs_buy.png'),dpi=150)
plt.close()
print("  -> figures/hourly_pv_vs_buy.png")

# Weekday summary
wd = df.groupby('weekday_name',observed=True).size().reset_index(name='count')
wd = wd.sort_values('count',ascending=False)
print(f"\nPeak day: {wd.iloc[0]['weekday_name']} ({wd.iloc[0]['count']:,} actions)")
print("Module 8 complete.")
