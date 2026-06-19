"""
电商平台用户增长分析 - 数据清洗模块
功能：读取数据、缺失值/重复值/异常值处理、时间字段扩展
"""
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# 获取脚本所在目录的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_PATH = os.path.join(DATA_DIR, 'UserBehavior.csv')
COLUMNS = ['user_id', 'item_id', 'category_id', 'behavior', 'timestamp']

print("=" * 60)
print("电商平台用户增长分析 - 数据清洗模块")
print("=" * 60)

# ========== 1. 读取数据 ==========
print("\n[Step 1] 读取原始数据...")
df = pd.read_csv(
    RAW_PATH, names=COLUMNS, header=None,
    dtype={'user_id': 'int32', 'item_id': 'int32', 'category_id': 'int32',
           'behavior': 'category', 'timestamp': 'float64'}
)
print(f"  原始数据: {len(df):,} 行, {len(df.columns)} 列")

# ========== 2. 数据基本情况 ==========
print("\n[Step 2] 数据基本情况...")
print(f"  数据类型:\n{df.dtypes}")
mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
print(f"  内存占用: {mem_mb:.2f} MB")

beh_counts = df['behavior'].value_counts()
print(f"  行为分布:")
for b, c in beh_counts.items():
    print(f"    {b}: {c:,} ({c / len(df) * 100:.2f}%)")

print(f"  用户数: {df['user_id'].nunique():,}")
print(f"  商品数: {df['item_id'].nunique():,}")
print(f"  品类数: {df['category_id'].nunique():,}")

# ========== 3. 缺失值分析 ==========
print("\n[Step 3] 缺失值分析...")
null_count = df.isnull().sum().sum()
print(f"  {'数据集中无缺失值' if null_count == 0 else f'发现{null_count}个缺失值'}")

# ========== 4. 重复值分析 ==========
print("\n[Step 4] 重复值分析...")
full_dup = df.duplicated().sum()
print(f"  完全重复行: {full_dup}")
df = df.drop_duplicates()

log_dup = df.duplicated(subset=['user_id', 'item_id', 'behavior', 'timestamp']).sum()
print(f"  逻辑重复行: {log_dup}")
df = df.drop_duplicates(subset=['user_id', 'item_id', 'behavior', 'timestamp'])
print(f"  去重后: {len(df):,} 行")

# ========== 5. 异常值分析 ==========
print("\n[Step 5] 异常值分析...")

# 5.1 时间戳空值
null_ts = df['timestamp'].isnull().sum()
print(f"  空时间戳: {null_ts}")
df = df.dropna(subset=['timestamp'])
df['timestamp'] = df['timestamp'].astype('int32')
ts_min, ts_max = int(df['timestamp'].min()), int(df['timestamp'].max())
print(f"  时间戳范围: {ts_min} ~ {ts_max}")
print(f"  对应日期: {datetime.fromtimestamp(ts_min)} ~ {datetime.fromtimestamp(ts_max)}")

# 5.2 时间戳合理范围（2016-2024年）
min_valid, max_valid = 1451606400, 1704067199
invalid_ts = ((df['timestamp'] < min_valid) | (df['timestamp'] > max_valid)).sum()
print(f"  异常时间戳: {invalid_ts}")
df = df[(df['timestamp'] >= min_valid) & (df['timestamp'] <= max_valid)]

# 5.3 行为类型有效性
invalid_beh = (~df['behavior'].isin(['pv', 'fav', 'cart', 'buy'])).sum()
print(f"  异常行为: {invalid_beh}")
df = df[df['behavior'].isin(['pv', 'fav', 'cart', 'buy'])]

print(f"  处理后: {len(df):,} 行")

# ========== 6. 时间戳转换 ==========
print("\n[Step 6] 时间戳转换...")
df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
print(f"  时间范围: {df['datetime'].min()} ~ {df['datetime'].max()}")

# ========== 7. 增加时间字段 ==========
print("\n[Step 7] 增加时间字段...")
df['date'] = df['datetime'].dt.date
df['hour'] = df['datetime'].dt.hour
df['weekday'] = df['datetime'].dt.dayofweek
wd_map = {0: '周一', 1: '周二', 2: '周三', 3: '周四', 4: '周五', 5: '周六', 6: '周日'}
df['weekday_name'] = df['weekday'].map(wd_map)
print("  新增字段: date, hour, weekday, weekday_name")
print(df[['user_id', 'behavior', 'datetime', 'date', 'hour', 'weekday_name']].head())

# ========== 8. 保存清洗数据 ==========
print("\n[Step 8] 保存清洗后数据...")
out_cols = ['user_id', 'item_id', 'category_id', 'behavior',
            'timestamp', 'datetime', 'date', 'hour', 'weekday', 'weekday_name']
df_cleaned = df[out_cols]
cleaned_path = os.path.join(DATA_DIR, 'cleaned_data.csv')
df_cleaned.to_csv(cleaned_path, index=False, encoding='utf-8')
print(f"  已保存: {cleaned_path}")
print(f"  最终数据: {len(df_cleaned):,} 行, {len(df_cleaned.columns)} 列")

# ========== 9. 数据概况报告 ==========
print("\n[Step 9] 生成数据概况报告...")
profile_path = os.path.join(DATA_DIR, 'data_profile.txt')
with open(profile_path, 'w', encoding='utf-8') as f:
    f.write("=" * 50 + "\n")
    f.write("电商用户行为数据 - 数据概况报告\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"清洗后数据量: {len(df_cleaned):,} 行\n")
    f.write(f"字段数: {len(df_cleaned.columns)}\n")
    f.write(f"内存占用: {mem_mb:.2f} MB\n\n")
    f.write(f"用户数: {df_cleaned['user_id'].nunique():,}\n")
    f.write(f"商品数: {df_cleaned['item_id'].nunique():,}\n")
    f.write(f"品类数: {df_cleaned['category_id'].nunique():,}\n\n")
    f.write("行为分布:\n")
    for b, c in beh_counts.items():
        f.write(f"  {b}: {c:,} ({c / len(df) * 100:.2f}%)\n")
    f.write(f"\n时间范围: {df_cleaned['datetime'].min()} ~ {df_cleaned['datetime'].max()}\n")
    f.write("缺失值: 无\n重复值: 已处理\n异常值: 已处理\n")
print(f"  已保存: {profile_path}")
print("\n" + "=" * 60)
print("数据清洗模块执行完毕！")
print("=" * 60)
