# -*- coding: utf-8 -*-
"""
Module 6: RFM User Segmentation (Key)
Output: figures/rfm_clusters.png
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
ref = df['datetime'].max()
print("="*50)
print("Module 6: RFM Analysis")
print("="*50)
print(f"Reference date: {ref}")

# R & F
rec = df.groupby('user_id')['datetime'].max().reset_index()
rec.columns = ['user_id','last']
rec['recency'] = (ref-rec['last']).dt.days
freq = df.groupby('user_id').size().reset_index(name='freq')
pur = df[df['behavior']=='buy'].groupby('user_id').size().reset_index(name='purchases')
rf = rec.merge(freq,on='user_id').merge(pur,on='user_id',how='left')
rf['purchases'] = rf['purchases'].fillna(0).astype(int)

print(f"Recency: mean={rf['recency'].mean():.0f}d")
print(f"Frequency: mean={rf['freq'].mean():.0f}")
print(f"Buyers: {(rf['purchases']>0).sum():,}/{(rf['purchases']>0).mean()*100:.1f}%")

# Manual KMeans (4 clusters)
X = np.column_stack([-rf['recency'].values,np.log1p(rf['freq'].values)])
X = (X-X.mean(0))/X.std(0)
np.random.seed(42)
idx = np.random.choice(len(X),4,replace=False)
c = X[idx].copy()
for _ in range(20):
    dist = np.sqrt(((X[:,None]-c)**2).sum(2))
    lbl = np.argmin(dist,1)
    nc = np.array([X[lbl==i].mean(0) for i in range(4)])
    if np.all(np.abs(nc-c)<1e-4): break
    c = nc
rf['cluster'] = lbl

ci = []
for i in range(4):
    m = rf['cluster']==i
    ci.append({'c':i,'cnt':m.sum(),'f':rf.loc[m,'freq'].mean()})
ci = pd.DataFrame(ci).sort_values('f',ascending=False).reset_index(drop=True)
lm = {int(ci.iloc[0]['c']):'高价值 High Value',
      int(ci.iloc[1]['c']):'潜力 Potential',
      int(ci.iloc[2]['c']):'沉默 Silent',
      int(ci.iloc[3]['c']):'流失 Churned'}
rf['seg'] = rf['cluster'].map(lm)

print("\nSegments:")
for s in ['高价值 High Value','潜力 Potential','沉默 Silent','流失 Churned']:
    sub = rf[rf['seg']==s]
    bp = (sub['purchases']>0).mean()*100
    print(f"  {s}: {len(sub):,} users ({len(sub)/len(rf)*100:.1f}%), "
          f"buy rate: {bp:.1f}%")

# Scatter chart
seg_order = ['高价值 High Value','潜力 Potential','沉默 Silent','流失 Churned']
cmap = {'高价值 High Value':'#2ECC71','潜力 Potential':'#5B9BD5',
        '沉默 Silent':'#FFC000','流失 Churned':'#E74C3C'}

fig, ax = plt.subplots(figsize=(12,8))
for seg in seg_order:
    mask = rf['seg']==seg
    ax.scatter(rf.loc[mask,'recency'],rf.loc[mask,'freq'],
               c=cmap.get(seg,'#999'),label=seg,alpha=0.5,s=10,edgecolors='none')
    sub = rf[rf['seg']==seg]
    if len(sub)>0:
        cx,cy = sub['recency'].mean(),sub['freq'].mean()
        ax.scatter(cx,cy,c=cmap.get(seg),marker='X',s=200,
                   edgecolors='black',linewidth=2,zorder=5)
ax.set_xlabel('Recency (距上次活跃天数)',fontsize=12)
ax.set_ylabel('Frequency (总行为次数)',fontsize=12)
ax.set_title('RF 用户聚类分析 (K-Means)',fontsize=14,fontweight='bold')
ax.legend(fontsize=10,loc='upper right'); ax.grid(True,alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(fig_dir,'rfm_clusters.png'),dpi=150)
plt.close()
print("\n  -> figures/rfm_clusters.png")
print("Module 6 complete.")
