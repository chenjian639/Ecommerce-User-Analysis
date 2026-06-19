# -*- coding: utf-8 -*-
"""
Module 4: Funnel Analysis (Key)
Output: figures/funnel_user.png
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

df = pd.read_csv(os.path.join(data_dir,'cleaned_data.csv'), parse_dates=['datetime'])
print("="*50)
print("Module 4: Funnel Analysis")
print("="*50)

# User-level funnel
uf = []
for beh in ['pv','fav','cart','buy']:
    uf.append({'stage':beh,'users':df[df['behavior']==beh]['user_id'].nunique()})
uf = pd.DataFrame(uf)
uf['prev'] = uf['users'].shift(1)
uf['cvr'] = np.where(uf['prev'].notna(),uf['users']/uf['prev']*100,100)

print("User Funnel:")
for _,r in uf.iterrows():
    print(f"  {r['stage']}: {r['users']:,} users, stage CVR: {r['cvr']:.2f}%")

# Funnel chart
fig, ax = plt.subplots(figsize=(10,7))
stages = ['pv','fav','cart','buy']
bar_colors = ['#5B9BD5','#6BA5D6','#FFC000','#ED7D31']
labels = ['浏览 PV','收藏 FAV','加购 CART','购买 BUY']
max_val = uf['users'].values[0]
for i,s in enumerate(stages):
    w = uf['users'].values[i]/max_val*100
    left = (100-w)/2
    ax.barh(3-i,w,left=left,height=0.55,color=bar_colors[i],edgecolor='white',linewidth=1.5)
    ax.text(50,3-i,f'{labels[i]}',va='center',ha='center',fontsize=12,fontweight='bold',
            color='white',bbox=dict(facecolor=bar_colors[i],alpha=0.8,boxstyle='round,pad=0.3'))
    ax.text(101,3-i,f'{uf["users"].values[i]:,} 用户',va='center',fontsize=11,fontweight='bold')
    if i>0:
        drop = 100-uf.iloc[i]['cvr']
        ax.text(-2,3-i,f'转化率 CVR: {uf.iloc[i]["cvr"]:.1f}%\n流失率 Drop: {drop:.1f}%',
                va='center',ha='right',fontsize=9)
ax.set_xlim(-20,115); ax.set_ylim(-0.8,3.8); ax.axis('off')
ax.set_title('用户级转化漏斗: 浏览 -> 购买',fontsize=15,fontweight='bold',pad=20)
overall = uf.iloc[-1]['users']/uf.iloc[0]['users']*100
ax.annotate(f'全链路转化率: {overall:.2f}%',xy=(0.5,-0.07),xycoords='axes fraction',
            ha='center',fontsize=12,
            bbox=dict(boxstyle='round,pad=0.5',facecolor='lightgreen',alpha=0.7))
plt.tight_layout()
plt.savefig(os.path.join(fig_dir,'funnel_user.png'),dpi=150,bbox_inches='tight')
plt.close()
print("\n  -> figures/funnel_user.png")

# Business Insights
print("\nBusiness Insights:")
print(f"  Max drop: PV->CART ({100-uf.iloc[1]['users']/uf.iloc[0]['users']*100:.1f}% users lost)")
print(f"  Cart->Buy CVR: {uf.iloc[3]['users']/uf.iloc[2]['users']*100:.1f}%")
print(f"  Only {overall:.1f}% complete purchase")
print(f"  Recommendations: cart reminders, CTA optimization, weekend deals")
print("Module 4 complete.")
