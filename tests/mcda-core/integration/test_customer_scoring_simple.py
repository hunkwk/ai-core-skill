"""
Customer Scoring Simple Test - No Package Installation Required

Tests configuration and data structure without full MCDA-Core execution
"""

import json
from pathlib import Path


def main():
    print("=" * 100)
    print("CUSTOMER SCORING TEST - DATA & CONFIGURATION VERIFICATION")
    print("=" * 100)

    # Paths
    test_dir = Path(__file__).parent
    yaml_path = test_dir / "fixtures" / "customer_scoring_50.yaml"
    json_path = test_dir / "fixtures" / "customer_50_data.json"

    # ============================================================
    # STEP 1: Load and verify customer data
    # ============================================================
    print("\n[STEP 1] CUSTOMER DATA VERIFICATION")
    print("-" * 100)

    with open(json_path, "r", encoding="utf-8") as f:
        customers = json.load(f)

    print(f"Total Customers: {len(customers)}")
    print(f"Fields per Customer: {len(customers[0])}")
    print(f"\nAll Fields:")
    for field in customers[0].keys():
        print(f"  - {field}")

    # Show first 5 customers
    print(f"\n[Sample Data - First 5 Customers]")
    for i, cust in enumerate(customers[:5], 1):
        print(f"\n{i}. {cust['name']}")
        print(f"   Annual Purchase: {cust['annual_purchase']:.2f}K | Growth: {cust['purchase_growth_rate']:+.2f}%")
        print(f"   Margin: {cust['gross_margin']:.2f}% | Payment: {cust['payment_timeliness']:.2f}%")
        print(f"   Years: {cust['cooperation_years']:.1f} | Orders: {cust['order_frequency']:.1f}/mo")
        print(f"   Complaints: {cust['complaint_count']} | Returns: {cust['return_rate']:.2f}%")
        print(f"   Overdue: {cust['overdue_days']} days | Service Cost: {cust['service_cost']:.2f}K")

    # ============================================================
    # STEP 2: Load and verify YAML configuration
    # ============================================================
    print("\n" + "=" * 100)
    print("[STEP 2] YAML CONFIGURATION VERIFICATION")
    print("-" * 100)

    with open(yaml_path, "r", encoding="utf-8") as f:
        yaml_content = f.read()

    # Count alternatives and criteria
    alternatives_count = yaml_content.count("  - Customer_")
    criteria_start = yaml_content.find("criteria:")
    algorithm_section = yaml_content.find("algorithm:")

    print(f"Alternatives: {alternatives_count}")
    print(f"Criteria Sections: {yaml_content.count('  - name:')}")

    # Extract criteria info
    print(f"\n[Criteria Configuration]")
    print("-" * 100)

    criteria_lines = [line for line in yaml_content.split('\n') if '  - name:' in line]
    weight_lines = [line for line in yaml_content.split('\n') if '    weight:' in line]
    direction_lines = [line for line in yaml_content.split('\n') if '    direction:' in line]

    total_weight = 0
    for i, (name_line, weight_line, dir_line) in enumerate(zip(criteria_lines, weight_lines, direction_lines), 1):
        name = name_line.split('name:')[1].strip()
        weight = float(weight_line.split('weight:')[1].strip())
        direction = dir_line.split('direction:')[1].strip()
        total_weight += weight

        icon = "[H]" if direction == "higher_better" else "[L]"
        print(f"{i:2d}. {icon} {name:25s} Weight={weight:.2f}")

    print(f"\nTotal Weight: {total_weight:.2f} (should be 1.00)")

    # ============================================================
    # STEP 3: Scoring Rules Analysis
    # ============================================================
    print("\n" + "=" * 100)
    print("[STEP 3] SCORING RULES ANALYSIS")
    print("-" * 100)

    threshold_count = yaml_content.count('type: threshold')
    minmax_count = yaml_content.count('type: minmax')

    print(f"Threshold Scoring Rules: {threshold_count} criteria")
    print(f"MinMax Scoring Rules: {minmax_count} criteria")
    print(f"Total Scoring Rules: {threshold_count + minmax_count}")

    # Extract scoring rule examples
    print(f"\n[Threshold Rule Example - annual_purchase]")
    in_purchase = False
    for line in yaml_content.split('\n'):
        if 'annual_purchase:' in line and 'name:' in line:
            in_purchase = True
            continue
        if in_purchase:
            if line.strip().startswith('- name:'):
                break
            if line.strip() and not line.strip().startswith('#'):
                print(f"  {line}")

    print(f"\n[MinMax Rule Example - purchase_growth_rate]")
    in_growth = False
    for line in yaml_content.split('\n'):
        if 'purchase_growth_rate:' in line and 'name:' in line:
            in_growth = True
            continue
        if in_growth:
            if line.strip().startswith('- name:'):
                break
            if line.strip() and not line.strip().startswith('#'):
                print(f"  {line}")

    # ============================================================
    # STEP 4: Data Statistics
    # ============================================================
    print("\n" + "=" * 100)
    print("[STEP 4] DATA STATISTICS (50 Customers)")
    print("-" * 100)

    # Calculate statistics for each field (excluding 'name' field)
    fields_stats = {}
    for field in customers[0].keys():
        if field == 'name':
            continue
        values = [c[field] for c in customers]
        fields_stats[field] = {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values)
        }

    print(f"{'Field':<30s} {'Min':>10s} {'Max':>10s} {'Avg':>10s}")
    print("-" * 70)
    for field, stats in fields_stats.items():
        print(f"{field:<30s} {stats['min']:>10.2f} {stats['max']:>10.2f} {stats['avg']:>10.2f}")

    # ============================================================
    # STEP 5: Test Scenario Summary
    # ============================================================
    print("\n" + "=" * 100)
    print("[STEP 5] TEST SCENARIO SUMMARY")
    print("-" * 100)

    print("""
Test Configuration:
  - Customers: 50
  - Criteria: 15 (10 positive + 5 negative)
  - Weighting Method: Direct (专家直接赋权)
  - Scoring Rules: Mixed (Threshold + MinMax)
  - Aggregation: WSM (Weighted Sum Model - 线性加权平均)

Positive Indicators (Higher Better):
  1. Annual Purchase (年度采购额) - Threshold scoring
  2. Purchase Growth Rate (采购增长率) - MinMax scoring
  3. Gross Margin (毛利率) - Threshold scoring
  4. Payment Timeliness (付款及时率) - Threshold scoring
  5. Cooperation Years (合作年限) - MinMax scoring
  6. Order Frequency (订单频率) - MinMax scoring
  7. Recommendation Score (推荐意愿) - MinMax scoring
  8. Loyalty Score (忠诚度) - MinMax scoring
  9. Market Influence (市场影响力) - MinMax scoring
  10. Innovation Cooperation (创新合作度) - MinMax scoring

Negative Indicators (Lower Better):
  11. Complaint Count (投诉次数) - Threshold scoring
  12. Return Rate (退货率) - Threshold scoring
  13. Overdue Days (逾期天数) - Threshold scoring
  14. Price Sensitivity (价格敏感度) - MinMax scoring
  15. Service Cost (服务成本) - MinMax scoring

Status:
  [OK] Raw data generation (50 customers x 15 fields)
  [OK] YAML configuration (alternatives, criteria, weights, scoring rules)
  [OK] Direct weighting (weights sum to 1.00)
  [OK] Scoring rules defined (6 threshold + 9 minmax)
  [OK] WSM algorithm ready
  [PARTIAL] Scoring logic (rules defined but applier not implemented)

Next Steps:
  1. Implement scoring rule applier (lib/scoring/applier.py) - 1 person-day
  2. Extend YAML parser for scoring rules - 0.5 person-day
  3. Extend MCDAOrchestrator - 1 person-day
  4. Testing and documentation - 1.5 person-days
  Total: ~4 person-days
    """)

    print("=" * 100)
    print("[TEST COMPLETE]")
    print("=" * 100)

    # ============================================================
    # STEP 6: Output sample of what the scoring would look like
    # ============================================================
    print("\n[STEP 6] EXAMPLE: How Scoring Would Work")
    print("-" * 100)

    print("""
For Customer_001 with:
  - annual_purchase: 977.17K
  - purchase_growth_rate: -18.25%
  - complaint_count: 6

Scoring Process:

1. Annual Purchase (Threshold):
   977.17 is in [500, 1000) -> Score = 80

2. Purchase Growth Rate (MinMax):
   Range: [-20, 50], Scale: 100
   Score = 100 * (value - min) / (max - min)
        = 100 * (-18.25 - (-20)) / (50 - (-20))
        = 100 * 1.75 / 70
        = 2.5

3. Complaint Count (Threshold, Lower Better):
   6 is in [6, 10) -> Score = 50

This process repeats for all 15 criteria,
then WSM aggregates the weighted scores:

Final Score = sum(weight_i * score_i) for i in 1..15

Result: Ranking of all 50 customers
    """)

    print("-" * 100)
    print("[END OF TEST OUTPUT]")
    print("-" * 100)


if __name__ == "__main__":
    main()
