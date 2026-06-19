# -*- coding: utf-8 -*-
"""
Module 5: Retention Analysis (Key)
Output: figures/retention_day_n.png, figures/retention_cohort_heatmap.png
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
df['date'] = pd.to_datetime(df['date'])
print("="*50)
print("Module 5: Retention Analysis")
print("="*50)

# User first date
uf = df.groupby('user_id')['date'].min().reset_index()
uf.columns = ['user_id','first_date']
df = df.merge(uf, on='user_id')
df['day_since_acq'] = (df['date']-df['first_date']).dt.days

# Active days per user
active_days = df.groupby('user_id')['day_since_acq'].apply(set).reset_index()
total_users = len(uf)

print("Day N Retention:")
ret = []
for day in [1,3,7,14,30]:
    kept = active_days[active_days['day_since_acq'].apply(lambda x: day in x)]
    rate = len(kept)/total_users*100
    ret.append({'day':day,'rate':rate})
    print(f"  Day {day}: {len(kept):,} users ({rate:.1f}%)")
ret = pd.DataFrame(ret)

# Chart 1: Day N retention
fig, ax = plt.subplots(figsize=(10,6))
colors = ['#5B9BD5','#A8D8EA','#FFC000','#ED7D31','#C0392B']
bars = ax.bar(range(len(ret)),ret['rate'],color=colors,edgecolor='white',width=0.6)
for bar,rate in zip(bars,ret['rate']):
    ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.5,
            f'{rate:.1f}%',ha='center',fontsize=12,fontweight='bold')
ax.set_xticks(range(len(ret)))
ax.set_xticklabels([f'Day {d}' for d in ret['day']])
ax.set_title('用户第N天留存率',fontsize=14,fontweight='bold')
ax.set_ylabel('留存率 (%)',fontsize=12); ax.set_ylim(0,max(ret['rate'])*1.3)
ax.grid(True,alpha=0.3,axis='y')
plt.tight_layout()
plt.savefig(os.path.join(fig_dir,'retention_day_n.png'),dpi=150)
plt.close()
print("  -> figures/retention_day_n.png")

# Chart 2: Cohort heatmap
df['acq_week'] = df['first_date'].dt.isocalendar().week.astype(int)
df['acq_year'] = df['first_date'].dt.year
df['cw'] = df['acq_year'].astype(str)+'-W'+df['acq_week'].astype(str).str.zfill(2)
df['week_since'] = (df['date']-df['first_date']).dt.days//7

cohort_sizes = df.groupby('cw')['user_id'].nunique().reset_index()
cohort_sizes.columns = ['cohort','total']
cohort_act = df.groupby(['cw','week_since'])['user_id'].nunique().reset_index()
cohort_act.columns = ['cohort','period','active']
cohort_act = cohort_act.merge(cohort_sizes,on='cohort')
cohort_act['rate'] = cohort_act['active']/cohort_act['total']*100

pivot = cohort_act.pivot_table(index='cohort',columns='period',values='rate',aggfunc='mean')
pivot = pivot[pivot.index.isin(cohort_sizes[cohort_sizes['total']>10]['cohort'])]
pivot = pivot.iloc[:,:12]

if len(pivot)>0 and pivot.shape[1]>1:
    fig, ax = plt.subplots(figsize=(14,max(6,len(pivot)*0.45)))
    im = ax.imshow(pivot.values,aspect='auto',cmap='YlOrRd',vmin=0,vmax=100)
    ax.set_xticks(range(pivot.shape[1]))
    ax.set_xticklabels([f'W{i}' for i in range(pivot.shape[1])])
    ax.set_yticks(range(len(pivot))); ax.set_yticklabels(pivot.index.tolist())
    for i in range(len(pivot)):
        for j in range(pivot.shape[1]):
            v = pivot.iloc[i,j]
            if not np.isnan(v): ax.text(j,i,f'{v:.1f}',ha='center',va='center',fontsize=8)
    ax.set_title('周级用户留存热力图 (Cohort Retention)',fontsize=14,fontweight='bold')
    ax.set_xlabel('周数偏移',fontsize=12); ax.set_ylabel('获客周',fontsize=12)
    plt.colorbar(im,ax=ax,label='留存率 (%)')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir,'retention_cohort_heatmap.png'),dpi=150,bbox_inches='tight')
    plt.close()
    print("  -> figures/retention_cohort_heatmap.png")

print("Module 5 complete.")
