# =============================================================================
# 模块 10：A/B Test 设计 — 首页推荐算法优化
# =============================================================================

## 1. 实验背景 (Background)

当前电商平台的首页推荐算法基于协同过滤（Collaborative Filtering），
用户看到的推荐商品主要依据"看了还看"、"买了还买"的逻辑。
我们提出优化方案：引入深度学习排序模型（DeepFM），
结合用户实时行为序列，提升推荐精准度。

## 2. 实验目标 (Objective)

**核心目标：** 提升首页推荐流的整体购买转化率 (CVR)

**辅助目标：**
- 提升推荐位的点击率 (CTR)
- 提升用户平均浏览深度 (PV/UV)
- 不降低用户次日留存率

**北极星指标：** 推荐位 GMV（成交总额）

## 3. 实验对象 (Experiment Subjects)

- **目标人群：** 过去30天内有至少1次活跃行为的用户
- **样本量估算：**
  - 基础转化率（对照组）: 2.0%
  - 预期提升: 相对提升10%（即目标CVR = 2.2%）
  - 显著性水平 α = 0.05, 统计功效 1-β = 0.80
  - 所需样本量（每组）: ~160,000 用户
  - 为保险预留20%缓冲 → 每组约 200,000 用户
- **流量分配：** 实验组 50% / 对照组 50%

## 4. 实验分组 (Experiment Groups)

| 分组 | 算法 | 说明 | 流量占比 |
|------|------|------|---------|
| 对照组 (Control) | 现有协同过滤 + LR | 当前线上版本 | 50% |
| 实验组 (Treatment) | DeepFM + 行为序列 | 新模型版本 | 50% |

**分流方式：** 按 user_id hash（一致性哈希）进行随机分流，
确保同一用户始终在同一组，避免交叉污染。

## 5. 实验周期 (Experiment Duration)

| 阶段 | 时间 | 说明 |
|------|------|------|
| 预实验 | 3天 | 小流量（5%）验证无功能性bug |
| 正式实验 | 14天 | 全量50%分流 |
| 观察期 | 7天 | 停止实验后追踪用户留存效应 |
| **总计** | **24天** | 含预实验和观察期 |

**周期选择理由：**
- 覆盖2个完整周末（周末行为模式不同）
- 14天足够让用户完成从浏览→购买的完整决策周期
- 7天观察期用于评估对留存的影响

## 6. 核心评估指标 (Core Metrics)

### 6.1 主要指标 (Primary)

| 指标 | 定义 | 计算方式 |
|------|------|---------|
| 推荐位 CTR | 推荐位点击量 / 推荐位曝光量 | Click / Impression |
| 推荐位 CVR | 推荐位带来的购买 / 推荐位点击 | Conversion / Click |
| 推荐位 GMV | 推荐位带来的成交总额 | ∑(订单金额) |
| 用户次日留存 | 次日回访用户 / 当日活跃用户 | D1 Retention |

### 6.2 辅助指标 (Secondary)

| 指标 | 定义 | 关注原因 |
|------|------|---------|
| 平均浏览深度 | PV / UV | 推荐是否增加了浏览 |
| 加购率 | 加购用户 / 浏览用户 | 中间转化环节 |
| 跳出率 | 单页访问用户 / 总用户 | 推荐相关性 |
| 人均停留时长 | 总时长 / UV | 用户参与度 |

### 6.3 护栏指标 (Guardrail)

| 指标 | 阈值 | 原因 |
|------|------|------|
| 页面加载时间 | 增加不超过5% | 新模型不能影响性能 |
| 用户投诉率 | 不超过0.1% | 推荐质量不能下降 |
| 整体DAU | 下降不超过1% | 不能造成用户流失 |

## 7. 统计检验方法 (Statistical Testing)

### 7.1 假设检验

```
H0 (零假设): CTR_实验组 = CTR_对照组 （新算法无效果）
H1 (备择假设): CTR_实验组 > CTR_对照组 （新算法有效果）
```

### 7.2 检验方法

| 指标类型 | 检验方法 | 说明 |
|---------|---------|------|
| CTR / CVR | 双比例Z检验 | 适用于二项分布指标 |
| GMV / 人均指标 | Mann-Whitney U检验 | 非正态分布指标 |
| 留存率 | 卡方检验 | 分类变量独立性检验 |

### 7.3 显著水平

- **统计显著性：** α = 0.05（双尾）
- **实际显著性：** 相对提升 ≥ 5%（仅统计显著不够，还需业务意义）
- **多重比较校正：** Bonferroni校正（多个指标同时检验时）
- **最小样本量验证：** 实验结束后使用 power.prop.test 验证样本量充足性

### 7.4 采样期间AA检验

正式实验前，通过AA测试（两组均使用旧算法运行3天）验证：
- 分流是否均匀（两组用户数差异 < 1%）
- 核心指标无显著差异（p > 0.05）
- 若AA检验失败，重新hash分流

## 8. 实验分析流程 (Analysis Pipeline)

### 8.1 实验结束后分析步骤

```
Step 1: 数据清洗
  - 剔除异常用户（爬虫、测试账号）
  - 按层（新用户/老用户）分别统计

Step 2: 描述性统计
  - 两组样本量、均值、标准差
  - 核心指标的分布可视化

Step 3: 假设检验
  - 对各核心指标执行相应统计检验
  - 计算p值和效应量（Cohen's d / Relative Lift）

Step 4: 分层分析 (Stratified Analysis)
  - 新用户 vs 老用户
  - 高活跃 vs 低活跃用户
  - 不同端侧（iOS / Android / Web）

Step 5: 稳健性检验
  - 剔除极端值后重新检验
  - 使用bootstrap方法验证置信区间稳定性

Step 6: 长期效应评估
  - 追踪实验组用户在实验结束后的7天留存
  - 评估是否存在" novelty effect "（新奇效应衰减）

Step 7: 决策结论
  - 显著正向 → 全量上线
  - 无显著差异 → 继续迭代优化
  - 显著负向 → 回滚旧版本，复盘原因
```

### 8.2 分析代码示例（Python伪代码）

```python
import numpy as np
from scipy import stats

def analyze_ab_test(control_data, treatment_data, metric='cvr'):
    """A/B Test 结果分析"""

    if metric in ['ctr', 'cvr']:
        # 比例类指标 - Z检验
        n_control = len(control_data)
        n_treatment = len(treatment_data)
        successes_control = control_data.sum()
        successes_treatment = treatment_data.sum()

        p_control = successes_control / n_control
        p_treatment = successes_treatment / n_treatment

        #  pooled proportion
        p_pool = (successes_control + successes_treatment) / (n_control + n_treatment)
        se = np.sqrt(p_pool * (1 - p_pool) * (1/n_control + 1/n_treatment))

        z_stat = (p_treatment - p_control) / se
        p_value = 1 - stats.norm.cdf(z_stat)
        relative_lift = (p_treatment - p_control) / p_control * 100

        return {
            'control_rate': p_control,
            'treatment_rate': p_treatment,
            'relative_lift': relative_lift,
            'z_stat': z_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }

    elif metric in ['gmv', 'duration']:
        # 连续变量 - Mann-Whitney U检验
        stat, p_value = stats.mannwhitneyu(
            treatment_data, control_data, alternative='greater'
        )
        relative_lift = (
            treatment_data.mean() - control_data.mean()
        ) / control_data.mean() * 100

        return {
            'control_mean': control_data.mean(),
            'treatment_mean': treatment_data.mean(),
            'relative_lift': relative_lift,
            'mw_stat': stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
```

## 9. 实验注意事项

1. **Novelty Effect（新奇效应）：** 新算法初期CTR可能虚高，
   至少运行2周待效应衰减后评估真实效果
2. **网络效应：** 推荐算法改变可能影响用户行为模式，
   需关注实验组用户的行为是否"污染"对照组用户（SUTVA假设）
3. **Day-of-week效应：** 确保实验周期覆盖完整周末周期
4. **早停规则：** 若实验组护栏指标（如页面性能、投诉率）
   出现显著恶化，立即停止实验
5. **SSOT（单一事实来源）：** 实验数据以服务端埋点日志为准，
   不以客户端上报数据做主分析
