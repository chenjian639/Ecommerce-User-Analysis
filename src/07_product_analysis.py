# -*- coding: utf-8 -*-
"""
Module 7: Product & Category Analysis
Output: figures/top20_items.png, figures/top20_categories.png
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
    usecols=['item_id','category_id','behavior'], dtype={'item_id':'int32','category_id':'int32','behavior':'category'})
print("="*50)
print("Module 7: Product Analysis")
print("="*50)

# Top 20 Items
top_items = df['item_id'].value_counts().head(20)

fig, ax = plt.subplots(figsize=(14,6))
ax.bar(range(20),top_items.values,color='#5B9BD5',edgecolor='white')
ax.set_xticks(range(20))
ax.set_xticklabels([str(i) for i in top_items.index],rotation=45,fontsize=8)
ax.set_title('Top 20 热门商品',fontsize=14,fontweight='bold')
ax.set_xlabel('商品 ID',fontsize=12); ax.set_ylabel('行为总量',fontsize=12)
ax.grid(True,alpha=0.3,axis='y')
plt.tight_layout()
plt.savefig(os.path.join(fig_dir,'top20_items.png'),dpi=150)
plt.close()
print("  -> figures/top20_items.png")

print("\nTop 20 Items:")
for i,(item,count) in enumerate(top_items.items()):
    print(f"  {i+1}. {item}: {count:,}")

# Top 20 Categories
top_cats = df['category_id'].value_counts().head(20)

fig, ax = plt.subplots(figsize=(14,6))
ax.bar(range(20),top_cats.values,color='#ED7D31',edgecolor='white')
ax.set_xticks(range(20))
ax.set_xticklabels([str(c) for c in top_cats.index],rotation=45,fontsize=8)
ax.set_title('Top 20 热门品类',fontsize=14,fontweight='bold')
ax.set_xlabel('品类 ID',fontsize=12); ax.set_ylabel('行为总量',fontsize=12)
ax.grid(True,alpha=0.3,axis='y')
plt.tight_layout()
plt.savefig(os.path.join(fig_dir,'top20_categories.png'),dpi=150)
plt.close()
print("\n  -> figures/top20_categories.png")

print("\nTop 20 Categories:")
for i,(cat,count) in enumerate(top_cats.items()):
    print(f"  {i+1}. {cat}: {count:,}")

# Category CVR
cat_all = df.groupby('category_id',observed=True).agg(
    total=('behavior','count'),buys=('behavior',lambda x:(x=='buy').sum()),
    pvs=('behavior',lambda x:(x=='pv').sum())).reset_index()
cat_all['cvr'] = cat_all['buys']/cat_all['pvs']*100
top_cvr = cat_all[cat_all['pvs']>=100].sort_values('cvr',ascending=False).head(5)
print("\nTop 5 Categories by CVR (>100 PV):")
for _,r in top_cvr.iterrows():
    print(f"  {int(r['category_id'])}: {r['cvr']:.2f}% ({r['buys']}/{r['pvs']})")

print("Module 7 complete.")
