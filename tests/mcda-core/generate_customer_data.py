"""
客户评分场景 - 50 个客户测试数据生成

包含 15 个客户评价指标：
- 正向指标（越高越好）：年度采购额、采购增长率、毛利率、付款及时率等
- 负向指标（越低越好）：投诉次数、退货率、逾期天数、价格敏感度等
"""

import random
import json
from pathlib import Path

# 设置随机种子保证可重现
random.seed(42)

# 生成 50 个客户数据
customers = []
for i in range(1, 51):
    customer = {
        "name": f"客户_{i:03d}",

        # ===== 正向指标（higher_better）=====

        # 1. 年度采购额（万元）- 范围：50-1500
        "annual_purchase": random.uniform(50, 1500),

        # 2. 采购增长率（%）- 范围：-20% ~ 50%
        "purchase_growth_rate": random.uniform(-20, 50),

        # 3. 毛利率（%）- 范围：5% ~ 35%
        "gross_margin": random.uniform(5, 35),

        # 4. 付款及时率（%）- 范围：40% ~ 100%
        "payment_timeliness": random.uniform(40, 100),

        # 5. 合作年限（年）- 范围：0.5 ~ 15 年
        "cooperation_years": random.uniform(0.5, 15),

        # 6. 订单频率（次/月）- 范围：1 ~ 30
        "order_frequency": random.uniform(1, 30),

        # 7. 推荐意愿（1-10分）- 范围：1 ~ 10
        "recommendation_score": random.uniform(1, 10),

        # 8. 忠诚度评分（1-100分）- 范围：20 ~ 100
        "loyalty_score": random.uniform(20, 100),

        # 9. 市场影响力（1-10分）- 范围：1 ~ 10
        "market_influence": random.uniform(1, 10),

        # 10. 创新合作度（1-10分）- 范围：1 ~ 10
        "innovation_cooperation": random.uniform(1, 10),

        # ===== 负向指标（lower_better）=====

        # 11. 投诉次数（次/年）- 范围：0 ~ 20
        "complaint_count": random.randint(0, 20),

        # 12. 退货率（%）- 范围：0% ~ 15%
        "return_rate": random.uniform(0, 15),

        # 13. 逾期天数（天/年）- 范围：0 ~ 90
        "overdue_days": random.randint(0, 90),

        # 14. 价格敏感度（1-10分）- 范围：1 ~ 10（越低越不敏感）
        "price_sensitivity": random.uniform(1, 10),

        # 15. 服务支持成本（万元/年）- 范围：1 ~ 50
        "service_cost": random.uniform(1, 50),
    }
    customers.append(customer)

# 保存为 JSON 文件
output_path = Path(__file__).parent / "fixtures" / "customer_50_data.json"
output_path.parent.mkdir(exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(customers, f, ensure_ascii=False, indent=2)

print(f"[OK] Generated {len(customers)} customer records")
print(f"Path: {output_path}")
print(f"\nData samples (first 3):")
for customer in customers[:3]:
    print(f"\nCustomer: {customer['name']}")
    print(f"  Annual Purchase: {customer['annual_purchase']:.2f}K")
    print(f"  Growth Rate: {customer['purchase_growth_rate']:.2f}%")
    print(f"  Complaint Count: {customer['complaint_count']}")
    print(f"  Return Rate: {customer['return_rate']:.2f}%")
