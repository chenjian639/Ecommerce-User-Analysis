# -*- coding: utf-8 -*-
"""
模块 9: 数据导出 — 为 Power BI Dashboard 准备数据

功能：
  将清洗后的数据分析结果整理为多张宽表，
  供 Power BI 直接导入建模。

输出：
  ../powerbi/dim_date.csv         日期维度表
  ../powerbi/dim_hour.csv         小时维度表
  ../powerbi/fact_daily.csv       每日核心指标
  ../powerbi/fact_hourly.csv      每小时各行为明细
  ../powerbi/fact_user_rfm.csv    用户级RFM分层数据
  ../powerbi/fact_funnel.csv      转化漏斗聚合
  ../powerbi/fact_top_items.csv   Top 商品/品类
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
PBI_DIR = os.path.join(PROJECT_ROOT, 'powerbi')
os.makedirs(PBI_DIR, exist_ok=True)

print("=" * 60)
print("模块 9: Power BI 数据导出")
print("=" * 60)

# ============================================================
# 读取清洗后数据
# ============================================================
data_path = os.path.join(DATA_DIR, 'cleaned_data.csv')
df = pd.read_csv(data_path, parse_dates=['datetime'])
print(f"\n读取数据: {len(df):,} 行")

# ============================================================
# 1. dim_date — 日期维度表
# ============================================================
print("\n[1/7] 生成日期维度表 ...")
date_range = pd.date_range(df['datetime'].min().date(), df['datetime'].max().date())
dim_date = pd.DataFrame({'date': date_range})
dim_date['year'] = dim_date['date'].dt.year
dim_date['month'] = dim_date['date'].dt.month
dim_date['day'] = dim_date['date'].dt.day
dim_date['weekday'] = dim_date['date'].dt.dayofweek  # 0=周一
wd_map = {0: '周一', 1: '周二', 2: '周三', 3: '周四', 4: '周五', 5: '周六', 6: '周日'}
dim_date['weekday_name'] = dim_date['weekday'].map(wd_map)
dim_date['is_weekend'] = dim_date['weekday'].isin([5, 6]).astype(int)
dim_date['week_of_year'] = dim_date['date'].dt.isocalendar().week.astype(int)
dim_date.to_csv(os.path.join(PBI_DIR, 'dim_date.csv'), index=False, encoding='utf-8-sig')
print(f"   -> {len(dim_date)} 行")

# ============================================================
# 2. dim_hour — 小时维度表
# ============================================================
print("[2/7] 生成小时维度表 ...")
dim_hour = pd.DataFrame({'hour': range(24)})
dim_hour['period'] = dim_hour['hour'].apply(
    lambda h: '凌晨' if h < 6 else ('上午' if h < 12 else ('下午' if h < 18 else '晚上'))
)
dim_hour.to_csv(os.path.join(PBI_DIR, 'dim_hour.csv'), index=False, encoding='utf-8-sig')
print(f"   -> {len(dim_hour)} 行")

# ============================================================
# 3. fact_daily — 每日核心指标
# ============================================================
print("[3/7] 生成每日指标表 ...")

# DAU
dau = df.groupby('date')['user_id'].nunique().reset_index(name='dau')
# PV & 各行为
daily_behav = df.groupby(['date', 'behavior']).size().reset_index(name='count')
daily_pivot = daily_behav.pivot(index='date', columns='behavior', values='count').fillna(0).reset_index()
daily_pivot.columns.name = None
for b in ['pv', 'fav', 'cart', 'buy']:
    if b not in daily_pivot.columns:
        daily_pivot[b] = 0

# 合并
fact_daily = dau.merge(daily_pivot, on='date', how='left')
fact_daily['pv_per_user'] = (fact_daily['pv'] / fact_daily['dau']).round(2)
fact_daily['cvr'] = (fact_daily['buy'] / fact_daily['pv'] * 100).round(2)
fact_daily['cart_buy_cvr'] = (fact_daily['buy'] / fact_daily['cart'] * 100).round(2)
fact_daily['fav_rate'] = (fact_daily['fav'] / fact_daily['pv'] * 100).round(2)
fact_daily['cart_rate'] = (fact_daily['cart'] / fact_daily['pv'] * 100).round(2)
fact_daily['buy_rate'] = (fact_daily['buy'] / fact_daily['pv'] * 100).round(2)
fact_daily['date'] = pd.to_datetime(fact_daily['date'])
fact_daily = fact_daily.sort_values('date')

fact_daily.to_csv(os.path.join(PBI_DIR, 'fact_daily.csv'), index=False, encoding='utf-8-sig')
print(f"   -> {len(fact_daily)} 行, {len(fact_daily.columns)} 列")

# ============================================================
# 4. fact_hourly — 每小时各行为明细
# ============================================================
print("[4/7] 生成小时级行为表 ...")

hourly_behav = df.groupby(['date', 'hour', 'behavior']).size().reset_index(name='count')
hourly_behav['date'] = pd.to_datetime(hourly_behav['date'])
hourly_behav['datetime'] = hourly_behav['date'] + pd.to_timedelta(hourly_behav['hour'], unit='h')
hourly_behav.to_csv(os.path.join(PBI_DIR, 'fact_hourly.csv'), index=False, encoding='utf-8-sig')
print(f"   -> {len(hourly_behav):,} 行")

# ============================================================
# 5. fact_user_rfm — 用户级RFM分层数据
# ============================================================
print("[5/7] 生成用户RFM分层表 ...")

ref_date = df['datetime'].max()
user_stats = df.groupby('user_id').agg(
    recency=('datetime', lambda x: (ref_date - x.max()).days),
    frequency=('user_id', 'count'),
    buy_count=('behavior', lambda x: (x == 'buy').sum()),
    fav_count=('behavior', lambda x: (x == 'fav').sum()),
    cart_count=('behavior', lambda x: (x == 'cart').sum()),
    pv_count=('behavior', lambda x: (x == 'pv').sum()),
    first_date=('datetime', 'min'),
    last_date=('datetime', 'max'),
    total_days=('date', lambda x: x.nunique()),
).reset_index()

user_stats['has_bought'] = (user_stats['buy_count'] > 0).astype(int)
user_stats['cvr'] = (user_stats['buy_count'] / user_stats['frequency'] * 100).round(2)

# RFM 分箱（rank 分位，避免数据集中导致 qcut 报错）
user_stats['r_rank'] = user_stats['recency'].rank(method='first', pct=True)
user_stats['r_level'] = pd.cut(
    user_stats['r_rank'], bins=5,
    labels=['1-最近', '2-近', '3-中', '4-远', '5-最远'],
    include_lowest=True
)
user_stats['f_rank'] = user_stats['frequency'].rank(method='first', pct=True)
user_stats['f_level'] = pd.cut(
    user_stats['f_rank'], bins=5,
    labels=['1-低频', '2-中低频', '3-中频', '4-高频', '5-最高频'],
    include_lowest=True
)

# 用户分层
def segment_user(row):
    r, f = row['r_level'], row['f_level']
    if pd.isna(r) or pd.isna(f):
        return '流失用户'
    if f in ['4-高频', '5-最高频'] and r in ['1-最近', '2-近']:
        return '高价值用户'
    elif f in ['3-中频', '4-高频'] and r in ['1-最近', '2-近', '3-中']:
        return '潜力用户'
    elif f in ['1-低频', '2-中低频'] and r in ['3-中', '4-远']:
        return '沉默用户'
    else:
        return '流失用户'

user_stats['segment'] = user_stats.apply(segment_user, axis=1)
user_stats['has_bought'] = (user_stats['buy_count'] > 0).astype(int)

user_stats.to_csv(os.path.join(PBI_DIR, 'fact_user_rfm.csv'), index=False, encoding='utf-8-sig')
print(f"   -> {len(user_stats):,} 用户")

# 打印分层概览
seg_summary = user_stats['segment'].value_counts()
print("\n  用户分层:")
for seg, cnt in seg_summary.items():
    pct = cnt / len(user_stats) * 100
    buy_rate = user_stats[user_stats['segment'] == seg]['has_bought'].mean() * 100
    print(f"    {seg}: {cnt:,} ({pct:.1f}%), 购买率: {buy_rate:.1f}%")

# ============================================================
# 6. fact_funnel — 转化漏斗
# ============================================================
print("\n[6/7] 生成漏斗数据表 ...")

funnel_data = {
    'stage': ['浏览(PV)', '收藏(FAV)', '加购(CART)', '购买(BUY)'],
    'users': [
        df['user_id'].nunique(),
        df[df['behavior'] == 'fav']['user_id'].nunique(),
        df[df['behavior'] == 'cart']['user_id'].nunique(),
        df[df['behavior'] == 'buy']['user_id'].nunique(),
    ]
}
fact_funnel = pd.DataFrame(funnel_data)
# 阶段转化率
for i in range(1, len(fact_funnel)):
    prev = fact_funnel.loc[i-1, 'users']
    curr = fact_funnel.loc[i, 'users']
    fact_funnel.loc[i, 'stage_cvr'] = round(curr / prev * 100, 2) if prev > 0 else 0
# 整体转化率
fact_funnel['overall_cvr'] = round(fact_funnel['users'] / fact_funnel['users'].iloc[0] * 100, 2)
# 流失率
fact_funnel['drop_rate'] = 100 - fact_funnel['overall_cvr']

fact_funnel.to_csv(os.path.join(PBI_DIR, 'fact_funnel.csv'), index=False, encoding='utf-8-sig')
print(f"   -> {len(fact_funnel)} 阶段")
for _, r in fact_funnel.iterrows():
    print(f"    {r['stage']}: {r['users']:,} 人, 整体转化 {r['overall_cvr']}%")

# ============================================================
# 7. fact_top_items — Top 商品 & 品类
# ============================================================
print("\n[7/7] 生成商品分析表 ...")

top_items = df.groupby('item_id').agg(
    total_actions=('behavior', 'count'),
    pv=('behavior', lambda x: (x == 'pv').sum()),
    fav=('behavior', lambda x: (x == 'fav').sum()),
    cart=('behavior', lambda x: (x == 'cart').sum()),
    buy=('behavior', lambda x: (x == 'buy').sum()),
    unique_users=('user_id', 'nunique'),
).reset_index()
top_items['cvr'] = (top_items['buy'] / top_items['pv'] * 100).round(2)
top_items['rank'] = top_items['total_actions'].rank(ascending=False, method='dense').astype(int)
top_items_20 = top_items[top_items['rank'] <= 20].copy()

top_cats = df.groupby('category_id').agg(
    total_actions=('behavior', 'count'),
    pv=('behavior', lambda x: (x == 'pv').sum()),
    buy=('behavior', lambda x: (x == 'buy').sum()),
    unique_items=('item_id', 'nunique'),
    unique_users=('user_id', 'nunique'),
).reset_index()
top_cats['cvr'] = (top_cats['buy'] / top_cats['pv'] * 100).round(2)
top_cats['rank'] = top_cats['total_actions'].rank(ascending=False, method='dense').astype(int)
top_cats_20 = top_cats[top_cats['rank'] <= 20].copy()

fact_top_items = pd.concat([
    top_items_20.assign(type='商品').rename(columns={'item_id': 'id'}),
    top_cats_20.assign(type='品类').rename(columns={'category_id': 'id'})
], ignore_index=True)

fact_top_items.to_csv(os.path.join(PBI_DIR, 'fact_top_items.csv'), index=False, encoding='utf-8-sig')
print(f"   -> {len(top_items_20)} 商品 + {len(top_cats_20)} 品类")

# ============================================================
# 完成
# ============================================================
print("\n" + "=" * 60)
print("Power BI 数据导出完成!")
print("=" * 60)
print(f"\n输出目录: {PBI_DIR}/")
print("\n文件列表:")
for f in sorted(os.listdir(PBI_DIR)):
    size = os.path.getsize(os.path.join(PBI_DIR, f))
    print(f"  {f:30s} {size/1024:>8.1f} KB")
print("\n在 Power BI 中依次导入这些 CSV，然后建立表间关系:")
print("  dim_date.date ← fact_daily.date → fact_hourly.date")
print("  dim_hour.hour ← fact_hourly.hour")
print("  dim_date.date ← fact_user_rfm.first/last_date (可选)")
