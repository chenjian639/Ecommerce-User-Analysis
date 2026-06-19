-- =============================================================================
-- 电商平台用户增长分析与运营策略优化
-- 模块 9：SQL 分析 (MySQL 8语法)
-- =============================================================================
-- 数据集：user_behavior
-- 字段：user_id, item_id, category_id, behavior, ts, datetime, date, hour, weekday
-- =============================================================================

-- 建表语句
CREATE TABLE user_behavior (
    user_id INT,
    item_id INT,
    category_id INT,
    behavior VARCHAR(10),    -- 'pv', 'fav', 'cart', 'buy'
    ts INT,                  -- Unix timestamp
    datetime DATETIME,
    date DATE,
    hour INT,
    weekday TINYINT,         -- 0=Mon, 6=Sun
    weekday_name VARCHAR(5)
);

-- ============================================================================
-- 1. 每日 DAU (Daily Active Users)
-- ============================================================================
SELECT
    date,
    COUNT(DISTINCT user_id) AS dau
FROM user_behavior
GROUP BY date
ORDER BY date;

-- ============================================================================
-- 2. 每日 PV (Page Views)
-- ============================================================================
SELECT
    date,
    COUNT(*) AS pv
FROM user_behavior
WHERE behavior = 'pv'
GROUP BY date
ORDER BY date;

-- ============================================================================
-- 3. 每日 UV (Unique Visitors)
-- ============================================================================
SELECT
    date,
    COUNT(DISTINCT user_id) AS uv
FROM user_behavior
GROUP BY date
ORDER BY date;

-- ============================================================================
-- 4. Top 20 热门商品（按总行为量）
-- ============================================================================
SELECT
    item_id,
    COUNT(*) AS total_actions,
    COUNT(DISTINCT user_id) AS unique_users,
    SUM(CASE WHEN behavior = 'buy' THEN 1 ELSE 0 END) AS purchases,
    SUM(CASE WHEN behavior = 'cart' THEN 1 ELSE 0 END) AS cart_adds,
    SUM(CASE WHEN behavior = 'fav' THEN 1 ELSE 0 END) AS favorites,
    SUM(CASE WHEN behavior = 'pv' THEN 1 ELSE 0 END) AS page_views
FROM user_behavior
GROUP BY item_id
ORDER BY total_actions DESC
LIMIT 20;

-- ============================================================================
-- 5. Top 20 热门品类（按总行为量）
-- ============================================================================
SELECT
    category_id,
    COUNT(*) AS total_actions,
    COUNT(DISTINCT user_id) AS unique_users,
    COUNT(DISTINCT item_id) AS unique_items,
    SUM(CASE WHEN behavior = 'buy' THEN 1 ELSE 0 END) AS purchases,
    SUM(CASE WHEN behavior = 'cart' THEN 1 ELSE 0 END) AS cart_adds,
    SUM(CASE WHEN behavior = 'fav' THEN 1 ELSE 0 END) AS favorites,
    SUM(CASE WHEN behavior = 'pv' THEN 1 ELSE 0 END) AS page_views
FROM user_behavior
GROUP BY category_id
ORDER BY total_actions DESC
LIMIT 20;

-- ============================================================================
-- 6. 用户购买次数分布
-- ============================================================================
SELECT
    purchase_count,
    COUNT(DISTINCT user_id) AS user_count
FROM (
    SELECT
        user_id,
        COUNT(*) AS purchase_count
    FROM user_behavior
    WHERE behavior = 'buy'
    GROUP BY user_id
) AS user_purchases
GROUP BY purchase_count
ORDER BY purchase_count;

-- ============================================================================
-- 7. 各行为转化率（事件级漏斗）
-- ============================================================================
WITH funnel AS (
    SELECT
        COUNT(*) FILTER (WHERE behavior = 'pv') AS pv,
        COUNT(*) FILTER (WHERE behavior = 'fav') AS fav,
        COUNT(*) FILTER (WHERE behavior = 'cart') AS cart,
        COUNT(*) FILTER (WHERE behavior = 'buy') AS buy
    FROM user_behavior
)
SELECT
    pv,
    fav,
    ROUND(fav / pv * 100, 2) AS pv_to_fav_cvr,
    cart,
    ROUND(cart / pv * 100, 2) AS pv_to_cart_cvr,
    buy,
    ROUND(buy / pv * 100, 2) AS overall_cvr
FROM funnel;

-- ============================================================================
-- 8. 热门时间段分析（按小时统计购买率）
-- ============================================================================
SELECT
    hour,
    COUNT(*) AS total_actions,
    SUM(CASE WHEN behavior = 'buy' THEN 1 ELSE 0 END) AS purchases,
    ROUND(SUM(CASE WHEN behavior = 'buy' THEN 1 ELSE 0 END) / COUNT(*) * 100, 3) AS buy_ratio,
    SUM(CASE WHEN behavior = 'pv' THEN 1 ELSE 0 END) AS page_views,
    SUM(CASE WHEN behavior = 'cart' THEN 1 ELSE 0 END) AS cart_adds
FROM user_behavior
GROUP BY hour
ORDER BY purchases DESC;

-- ============================================================================
-- 9. 窗口函数排名：每个用户按行为时间的序列（Rank）
-- ============================================================================
SELECT
    user_id,
    datetime,
    behavior,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY datetime) AS action_seq,
    RANK() OVER (PARTITION BY user_id ORDER BY datetime) AS action_rank,
    DENSE_RANK() OVER (PARTITION BY user_id ORDER BY date) AS active_day_rank
FROM user_behavior
LIMIT 100;

-- ============================================================================
-- 10. 用户行为路径：首次行为 vs 末次行为
-- ============================================================================
WITH first_last_action AS (
    SELECT
        user_id,
        FIRST_VALUE(behavior) OVER (PARTITION BY user_id ORDER BY datetime) AS first_behavior,
        LAST_VALUE(behavior) OVER (PARTITION BY user_id ORDER BY datetime
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_behavior
    FROM user_behavior
)
SELECT
    first_behavior,
    last_behavior,
    COUNT(DISTINCT user_id) AS user_count
FROM first_last_action
GROUP BY first_behavior, last_behavior
ORDER BY user_count DESC;

-- ============================================================================
-- 11. 用户分层：按总行为量划分
-- ============================================================================
WITH user_stats AS (
    SELECT
        user_id,
        COUNT(*) AS total_actions,
        SUM(CASE WHEN behavior = 'buy' THEN 1 ELSE 0 END) AS purchases
    FROM user_behavior
    GROUP BY user_id
)
SELECT
    CASE
        WHEN total_actions >= 100 THEN 'High Activity'
        WHEN total_actions >= 50 THEN 'Medium Activity'
        WHEN total_actions >= 10 THEN 'Low Activity'
        ELSE 'Very Low Activity'
    END AS activity_level,
    COUNT(DISTINCT user_id) AS user_count,
    ROUND(AVG(purchases), 2) AS avg_purchases,
    ROUND(SUM(purchases) / SUM(total_actions) * 100, 3) AS buy_ratio
FROM user_stats
GROUP BY activity_level
ORDER BY user_count DESC;

-- ============================================================================
-- 12. 每小时活跃用户数（窗口函数版）
-- ============================================================================
SELECT DISTINCT
    hour,
    COUNT(DISTINCT user_id) OVER (PARTITION BY hour) AS active_users,
    COUNT(*) OVER (PARTITION BY hour) AS total_actions
FROM user_behavior
ORDER BY hour;

-- ============================================================================
-- 13. 每周留存率（Cohort Analysis via SQL）
-- ============================================================================
WITH user_first_week AS (
    SELECT
        user_id,
        MIN(DATE_FORMAT(date, '%Y-%u')) AS first_week
    FROM user_behavior
    GROUP BY user_id
),
user_weekly AS (
    SELECT DISTINCT
        ub.user_id,
        ufw.first_week,
        DATE_FORMAT(ub.date, '%Y-%u') AS active_week
    FROM user_behavior ub
    JOIN user_first_week ufw ON ub.user_id = ufw.user_id
),
cohort_size AS (
    SELECT
        first_week,
        COUNT(DISTINCT user_id) AS cohort_users
    FROM user_first_week
    GROUP BY first_week
)
SELECT
    uw.first_week,
    uw.active_week,
    cs.cohort_users,
    COUNT(DISTINCT uw.user_id) AS retained_users,
    ROUND(COUNT(DISTINCT uw.user_id) / cs.cohort_users * 100, 2) AS retention_rate,
    ROUND((WEEK(STR_TO_DATE(CONCAT(uw.active_week, ' Monday'), '%Y-%u %W')) -
           WEEK(STR_TO_DATE(CONCAT(uw.first_week, ' Monday'), '%Y-%u %W'))) * 1.0, 0) AS week_offset
FROM user_weekly uw
JOIN cohort_size cs ON uw.first_week = cs.first_week
GROUP BY uw.first_week, uw.active_week, cs.cohort_users
HAVING week_offset BETWEEN 0 AND 12
ORDER BY uw.first_week, week_offset;

-- ============================================================================
-- 14. 商品级转化率（按品类汇总）
-- ============================================================================
SELECT
    category_id,
    SUM(CASE WHEN behavior = 'pv' THEN 1 ELSE 0 END) AS views,
    SUM(CASE WHEN behavior = 'cart' THEN 1 ELSE 0 END) AS carts,
    SUM(CASE WHEN behavior = 'fav' THEN 1 ELSE 0 END) AS favs,
    SUM(CASE WHEN behavior = 'buy' THEN 1 ELSE 0 END) AS buys,
    ROUND(
        SUM(CASE WHEN behavior = 'buy' THEN 1 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN behavior = 'pv' THEN 1 ELSE 0 END), 0) * 100, 3
    ) AS view_to_buy_cvr,
    ROUND(
        SUM(CASE WHEN behavior = 'buy' THEN 1 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN behavior = 'cart' THEN 1 ELSE 0 END), 0) * 100, 3
    ) AS cart_to_buy_cvr
FROM user_behavior
GROUP BY category_id
HAVING views >= 100
ORDER BY view_to_buy_cvr DESC
LIMIT 20;

-- ============================================================================
-- 15. 用户连续活跃天数（最长连续活跃）
-- ============================================================================
WITH user_active_dates AS (
    SELECT DISTINCT user_id, date
    FROM user_behavior
),
user_date_rank AS (
    SELECT
        user_id,
        date,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY date) AS rn,
        DATE_SUB(date, INTERVAL ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY date) DAY) AS date_group
    FROM user_active_dates
)
SELECT
    user_id,
    COUNT(*) AS consecutive_days,
    MIN(date) AS start_date,
    MAX(date) AS end_date
FROM user_date_rank
GROUP BY user_id, date_group
HAVING consecutive_days >= 3
ORDER BY consecutive_days DESC
LIMIT 20;
