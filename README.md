# 电商平台用户增长分析与运营策略优化

> 基于电商平台用户行为日志数据的完整数据分析项目，模拟互联网公司数据分析工作流程。
> 适合写入本科生数据分析方向简历。

---

## 项目概述

| 项目 | 说明 |
|------|------|
| **数据来源** | UserBehavior.csv（淘宝用户行为日志数据集） |
| **数据量** | 原始267万行 → 清洗后106万行 |
| **用户数** | 10,347 |
| **时间跨度** | 2017年9月 - 2018年8月 |
| **行为类型** | PV（浏览）、FAV（收藏）、CART（加购）、BUY（购买） |

## 项目结构

```
Ecommerce_User_Analysis/
│
├── data/                        # 数据文件
│   ├── UserBehavior.csv         # 原始数据
│   └── cleaned_data.csv         # 清洗后数据 [来源: src/01]
│
├── sql/                         # SQL分析代码
│   └── analysis_queries.sql     # 15个MySQL 8查询 [来源: 模块9]
│
├── figures/                     # 可视化图表 (12张)
│   │
│   │  ── 模块2: 指标体系 ──
│   ├── dau_trend.png            # DAU每日趋势
│   ├── hourly_activity.png      # 每小时活跃度 + 各行为分布
│   ├── behavior_pie.png         # 用户行为饼图
│   ├── weekly_activity.png      # 各星期活跃度对比
│   │
│   │  ── 模块3: 用户行为分析 ──
│   ├── behavior_daily_trend.png # 每日四类行为趋势
│   │
│   │  ── 模块4: 漏斗分析 ──
│   ├── funnel_user.png          # 用户级转化漏斗 (浏览→收藏→加购→购买)
│   │
│   │  ── 模块5: 留存分析 ──
│   ├── retention_day_n.png      # Day1/3/7/14/30 留存率对比
│   ├── retention_cohort_heatmap.png # 周级 Cohort 留存热力图
│   │
│   │  ── 模块6: RFM用户分层 ──
│   ├── rfm_clusters.png         # K-Means 用户聚类散点图
│   │
│   │  ── 模块7: 商品分析 ──
│   ├── top20_items.png          # Top20 热门商品
│   ├── top20_categories.png     # Top20 热门品类
│   │
│   │  ── 模块8: 时间分析 ──
│   ├── time_heatmaps.png        # 星期×小时 四行为热力图矩阵
│   └── hourly_pv_vs_buy.png     # 每小时 PV vs 购买 双轴对比
│
├── report/                      # 分析报告
│   ├── business_analysis_report.md  # 完整商业分析报告 [来源: 模块12]
│   ├── ab_test_design.md        # A/B Test 实验设计 [来源: 模块10]
│   ├── dashboard_design.md      # Dashboard 看板设计 [来源: 模块11]
│   └── resume_description.md    # 可直接写入简历的项目描述 [来源: 模块13]
│
├── src/                         # Python 源代码 (8个模块)
│   ├── 01_data_cleaning.py      # 模块1: 数据清洗 + 特征工程
│   ├── 02_metrics_analysis.py   # 模块2: 指标体系 (DAU/活跃时段/行为占比)
│   ├── 03_user_behavior.py      # 模块3: 用户行为分析 (趋势/行为路径)
│   ├── 04_funnel_analysis.py    # 模块4: 漏斗分析 (转化率/流失归因)
│   ├── 05_retention_analysis.py # 模块5: 留存分析 (Day N / Cohort热力图)
│   ├── 06_rfm_analysis.py       # 模块6: RFM用户分层 (K-Means聚类)
│   ├── 07_product_analysis.py   # 模块7: 商品分析 (Top20商品/品类/CVR)
│   └── 08_time_analysis.py      # 模块8: 时间分析 (热力图/双轴对比)
│
└── README.md                    # 项目说明
```

## 分析模块导航

| # | 模块 | 核心内容 | 产出文件 |
|---|------|---------|---------|
| 1 | **数据清洗** | 缺失值/重复值/异常值处理，时间戳转换 | `src/01_data_cleaning.py` · `data/cleaned_data.csv` |
| 2 | **指标体系分析** | PV/UV/DAU/人均浏览/活跃时段 | `figures/dau_trend.png` · `hourly_activity.png` · `behavior_pie.png` · `weekly_activity.png` |
| 3 | **用户行为分析** | 行为分布、趋势、行为路径 | `figures/behavior_daily_trend.png` |
| 4 | **漏斗分析** | 四阶段转化漏斗、流失定位、优化建议 | `figures/funnel_user.png` |
| 5 | **留存分析** | Day1/3/7留存、Cohort热力图 | `figures/retention_day_n.png` · `retention_cohort_heatmap.png` |
| 6 | **RFM分析** | 用户聚类、四类用户分层 | `figures/rfm_clusters.png` |
| 7 | **商品分析** | Top20商品/品类、转化率分析 | `figures/top20_items.png` · `top20_categories.png` |
| 8 | **时间分析** | 小时/星期/日期行为模式 | `figures/time_heatmaps.png` · `hourly_pv_vs_buy.png` |
| 9 | **SQL分析** | 15个MySQL 8查询（窗口函数、Cohort SQL等） | `sql/analysis_queries.sql` |
| 10 | **A/B Test设计** | 首页推荐算法优化完整实验方案 | `report/ab_test_design.md` |
| 11 | **Dashboard设计** | 7类图表设计及Power BI/Tableau/Excel选型 | `report/dashboard_design.md` |
| 12 | **商业报告** | 完整分析报告、10条运营建议 | `report/business_analysis_report.md` |
| 13 | **简历描述** | 可直接写入简历的项目经历（中英双语） | `report/resume_description.md` |

> 每个模块都有独立的 Python 源码文件（`src/01~08`），可单独运行或按顺序复现全部分析流程。

## 核心发现

### 1. 转化漏斗
- **浏览→购买转化率：** 2.03%（行业中等水平）
- **最大流失环节：** 浏览→加购（94.5%浏览未加购）
- **加购→购买转化：** 36.76%（63%加购未支付）

### 2. 用户活跃
- **最活跃时段：** 12:00-15:00（午间高峰）
- **最活跃星期：** 周六（工作日2.5倍）
- **峰值DAU：** 9,895（2017-12-02，周末+月初效应）

### 3. 用户分层
| 类型 | 占比 | 购买率 | 策略 |
|------|------|--------|------|
| 高价值 | 20.2% | 81.5% | VIP运营 |
| 潜力 | 32.6% | 73.2% | 转化提速 |
| 沉默 | 30.6% | 64.1% | 召回激活 |
| 流失 | 16.6% | 52.6% | 挽回 |

### 4. 留存
- Day 1留存：74.34%
- Day 7留存：82.58%（周末效应）
- 规律用户（65.5%）是核心运营群体

## 环境要求

```bash
Python 3.8+
pandas>=1.3
numpy>=1.21
matplotlib>=3.4
```

## 复现步骤

```bash
# 1. 克隆项目
cd Ecommerce_User_Analysis

# 2. 安装依赖
pip install pandas numpy matplotlib

# 3. 准备数据
# 将 UserBehavior.csv 放入 data/ 目录

# 4. 依次运行分析模块 (按顺序 01→08)
python src/01_data_cleaning.py      # 数据清洗
python src/02_metrics_analysis.py   # 指标体系
python src/03_user_behavior.py      # 用户行为
python src/04_funnel_analysis.py    # 漏斗分析
python src/05_retention_analysis.py # 留存分析
python src/06_rfm_analysis.py       # RFM分层
python src/07_product_analysis.py   # 商品分析
python src/08_time_analysis.py      # 时间分析

# 5. SQL分析
# 将 data/cleaned_data.csv 导入 MySQL 8
# 执行 sql/analysis_queries.sql
```

## 技术栈

| 类别 | 技术 |
|------|------|
| **数据处理** | Python (Pandas, NumPy) |
| **数据可视化** | Matplotlib |
| **统计分析** | K-Means聚类、假设检验 |
| **数据库** | MySQL 8（窗口函数、CTE） |
| **BI工具** | Power BI / Tableau / Excel |

## 联系

本项目为数据分析方向简历项目，欢迎交流与建议。

---

*最后更新：2026年6月*
