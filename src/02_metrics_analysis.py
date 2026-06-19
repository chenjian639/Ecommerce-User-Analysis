# -*- coding: utf-8 -*-
"""
Module 2: Metrics System
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings('ignore', category=UserWarning)
import os, glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
FIGURE_DIR = os.path.join(PROJECT_ROOT, 'figures')
os.makedirs(FIGURE_DIR, exist_ok=True)

# Chinese font fallback: DejaVu (Latin) + Droid Sans Fallback (CJK)
font_path = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10

COLORS = {'pv': '#5B9BD5', 'fav': '#FFC000', 'cart': '#ED7D31', 'buy': '#70AD47'}
COLORS_LIST = ['#5B9BD5', '#FFC000', '#ED7D31', '#70AD47', '#9B59B6']

print("=" * 60)
print("Module 2: Metrics Analysis")
print("=" * 60)

data_path = os.path.join(DATA_DIR, 'cleaned_data.csv')
print(f"\nReading: {data_path}")
df = pd.read_csv(data_path, parse_dates=['datetime'])
print(f"Rows: {len(df):,}")

# === 1. Core Metrics ===
print("\n" + "-" * 40)
print("1. Core Metrics")
print("-" * 40)

pv_total = len(df)
uv_total = df['user_id'].nunique()
avg_pv_per_user = pv_total / uv_total
buy_total = (df['behavior'] == 'buy').sum()
overall_cvr = buy_total / pv_total * 100

print(f"PV: {pv_total:,}")
print(f"UV: {uv_total:,}")
print(f"PV/User: {avg_pv_per_user:.2f}")
print(f"Purchases: {buy_total:,}")
print(f"Overall CVR: {overall_cvr:.4f}%")

# === 2. DAU ===
print("\n" + "-" * 40)
print("2. DAU Analysis")
print("-" * 40)

dau = df.groupby('date')['user_id'].nunique().reset_index()
dau.columns = ['date', 'dau']
dau['date'] = pd.to_datetime(dau['date'])

daily_pv = df.groupby('date').size().reset_index(name='pv')
daily_pv['date'] = pd.to_datetime(daily_pv['date'])

daily_behaviors = df.groupby(['date', 'behavior']).size().reset_index(name='count')
daily_behaviors['date'] = pd.to_datetime(daily_behaviors['date'])

daily_metrics = dau.merge(daily_pv, on='date')
daily_metrics['avg_pv_per_user'] = daily_metrics['pv'] / daily_metrics['dau']

print(f"Avg DAU: {dau['dau'].mean():.0f}")
print(f"Max DAU: {dau['dau'].max():,} ({dau.loc[dau['dau'].idxmax(), 'date'].date()})")
print(f"Min DAU: {dau['dau'].min():,} ({dau.loc[dau['dau'].idxmin(), 'date'].date()})")
print(f"Avg Daily PV: {daily_pv['pv'].mean():,.0f}")



fig, ax = plt.subplots(figsize=(16, 5))
ax.plot(dau['date'], dau['dau'], color='#5B9BD5', linewidth=1.5, marker='o', markersize=2)
ax.set_title('DAU Trend', fontsize=14, fontweight='bold')
ax.set_xlabel('Date', fontsize=11)
ax.set_ylabel('Active Users', fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(FIGURE_DIR, 'dau_trend.png'), dpi=150)
plt.close()
print("  -> figures/dau_trend.png")

# === 3. Hourly Activity ===
print("\n" + "-" * 40)
print("3. Hourly Activity")
print("-" * 40)

hourly_activity = df.groupby('hour').agg(
    total_actions=('user_id', 'count'),
    unique_users=('user_id', 'nunique')
).reset_index()

hourly_behavior = df.groupby(['hour', 'behavior']).size().reset_index(name='count')

print(hourly_activity.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(16, 5))

ax = axes[0]
ax.bar(hourly_activity['hour'], hourly_activity['total_actions'], color='#5B9BD5', edgecolor='white')
ax.set_title('Hourly Total Actions', fontsize=13, fontweight='bold')
ax.set_xlabel('Hour', fontsize=11)
ax.set_ylabel('Action Count', fontsize=11)
ax.set_xticks(range(0, 24))
ax.grid(True, alpha=0.3, axis='y')

ax = axes[1]
behavior_types = ['pv', 'fav', 'cart', 'buy']
for beh in behavior_types:
    beh_data = hourly_behavior[hourly_behavior['behavior'] == beh]
    ax.plot(beh_data['hour'], beh_data['count'],
            color=COLORS[beh], marker='o', linewidth=2, markersize=4, label=beh)
ax.set_title('Hourly Actions by Type', fontsize=13, fontweight='bold')
ax.set_xlabel('Hour', fontsize=11)
ax.set_ylabel('Count', fontsize=11)
ax.set_xticks(range(0, 24))
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(FIGURE_DIR, 'hourly_activity.png'), dpi=150)
plt.close()
print("  -> figures/hourly_activity.png")

# === 4. Behavior Distribution ===
print("\n" + "-" * 40)
print("4. Behavior Distribution")
print("-" * 40)

behavior_counts = df['behavior'].value_counts()
behavior_pct = df['behavior'].value_counts(normalize=True) * 100

for b in ['pv', 'fav', 'cart', 'buy']:
    c = behavior_counts.get(b, 0)
    p = behavior_pct.get(b, 0)
    print(f"  {b}: {c:,} ({p:.2f}%)")

fig, ax = plt.subplots(figsize=(8, 6))
colors = [COLORS.get(b, '#999999') for b in behavior_counts.index]
wedges, texts, autotexts = ax.pie(
    behavior_counts.values, labels=behavior_counts.index,
    autopct='%1.2f%%', colors=colors, startangle=90,
    explode=[0.03] * len(behavior_counts), textprops={'fontsize': 12}
)
ax.set_title('Behavior Distribution', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIGURE_DIR, 'behavior_pie.png'), dpi=150)
plt.close()
print("  -> figures/behavior_pie.png")

# === 5. Traffic Peaks ===
print("\n" + "-" * 40)
print("5. Traffic Peaks")
print("-" * 40)

top10_days = daily_pv.sort_values('pv', ascending=False).head(10)
print("\nTop10 PV Days:")
for _, row in top10_days.iterrows():
    print(f"  {row['date'].date()}: {row['pv']:,} PV")

weekly_activity = df.groupby('weekday_name').agg(
    total_actions=('user_id', 'count'),
    unique_users=('user_id', 'nunique')
).reset_index()

wd_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
weekly_activity['wd_order'] = weekly_activity['weekday_name'].apply(
    lambda x: wd_order.index(x) if x in wd_order else 99)
weekly_activity = weekly_activity.sort_values('wd_order')

print("\nWeekly Activity:")
print(weekly_activity[['weekday_name', 'total_actions', 'unique_users']].to_string(index=False))

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(weekly_activity['weekday_name'], weekly_activity['total_actions'],
       color=COLORS_LIST, edgecolor='white')
ax.set_title('Weekly Activity', fontsize=13, fontweight='bold')
ax.set_xlabel('Day of Week', fontsize=11)
ax.set_ylabel('Actions', fontsize=11)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(os.path.join(FIGURE_DIR, 'weekly_activity.png'), dpi=150)
plt.close()
print("  -> figures/weekly_activity.png")

# === 6. Key Findings ===
print("\n" + "=" * 60)
print("Key Findings")
print("=" * 60)

peak_hour = hourly_activity.loc[hourly_activity['total_actions'].idxmax()]
print(f"\n1. Peak hour: {int(peak_hour['hour']):02d}:00 ({peak_hour['total_actions']:,} actions)")

top3 = hourly_activity.sort_values('total_actions', ascending=False).head(3)
hours_str = ' '.join([f"{int(r['hour'])}:00" for _, r in top3.iterrows()])
print(f"   Top3 hours: {hours_str}")

peak_day = weekly_activity.loc[weekly_activity['total_actions'].idxmax()]
print(f"2. Peak day: {peak_day['weekday_name']}")

peak_date = daily_pv.loc[daily_pv['pv'].idxmax()]
print(f"3. Peak date: {peak_date['date'].date()} (PV: {peak_date['pv']:,})")

print(f"\n4. PV ratio: {behavior_pct.get('pv', 0):.2f}%")
print(f"   Buy ratio: {behavior_pct.get('buy', 0):.2f}%")
print(f"   Cart ratio: {behavior_pct.get('cart', 0):.2f}%")
print(f"   Fav ratio: {behavior_pct.get('fav', 0):.2f}%")

print(f"\n5. Overall PV->Buy CVR: {overall_cvr:.4f}%")
print(f"   Avg PV per user: {avg_pv_per_user:.1f}")

print("\n" + "=" * 60)
print("Module 2 complete! Files:")
print("=" * 60)
for f in ['dau_trend.png', 'hourly_activ