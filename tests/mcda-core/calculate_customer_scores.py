"""
Customer Scoring Calculator - 评分计算器

实现评分规则应用器，计算所有客户的评分和排名
"""

import json
from pathlib import Path
from typing import Dict, Any


class ScoringApplier:
    """评分规则应用器"""

    @staticmethod
    def apply_threshold(value: float, rule: Dict[str, Any]) -> float:
        """
        应用阈值评分规则

        Args:
            value: 原始值
            rule: 评分规则配置

        Returns:
            评分（0-100）
        """
        ranges = rule.get('ranges', [])
        default_score = rule.get('default_score', 0.0)

        # 检查每个区间
        for range_rule in ranges:
            min_val = range_rule.get('min')
            max_val = range_rule.get('max')

            # 判断是否在区间内
            in_range = True

            if min_val is not None and value < min_val:
                in_range = False
            if max_val is not None and value >= max_val:
                in_range = False

            if in_range:
                return float(range_rule['score'])

        return float(default_score)

    @staticmethod
    def apply_minmax(value: float, rule: Dict[str, Any]) -> float:
        """
        应用 MinMax 评分规则（线性评分）

        Args:
            value: 原始值
            rule: 评分规则配置

        Returns:
            评分（0-100）
        """
        min_val = rule['min']
        max_val = rule['max']
        scale = rule.get('scale', 100.0)

        # 限制在范围内
        clamped_value = max(min_val, min(max_val, value))

        # 线性映射
        if max_val == min_val:
            return 0.0

        score = scale * (clamped_value - min_val) / (max_val - min_val)
        return float(score)


def load_yaml_config(yaml_path: Path) -> Dict[str, Any]:
    """手动解析 YAML 配置（简化版）"""
    import re

    with open(yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    config = {
        'criteria': [],
        'algorithm': {'name': 'wsm'}
    }

    # 解析准则配置
    criteria_blocks = content.split('- name:')[1:]

    for block in criteria_blocks:
        lines = block.strip().split('\n')

        criterion = {
            'name': lines[0].strip(),
            'weight': 0.0,
            'direction': 'higher_better',
            'column': None,
            'scoring_rule': None
        }

        for line in lines[1:]:
            if 'weight:' in line:
                criterion['weight'] = float(line.split('weight:')[1].strip())
            elif 'direction:' in line:
                criterion['direction'] = line.split('direction:')[1].strip()
            elif 'column:' in line:
                criterion['column'] = line.split('column:')[1].strip()
            elif 'scoring_rule:' in line:
                # 解析评分规则
                rule_start = lines.index(line)
                rule_lines = []
                indent_level = len(line) - len(line.lstrip())

                for i in range(rule_start, len(lines)):
                    rule_lines.append(lines[i])
                    # 检查是否到了下一个准则或同级别字段
                    if i > rule_start:
                        current_indent = len(lines[i]) - len(lines[i].lstrip())
                        if lines[i].strip() and current_indent <= indent_level and '- name:' not in lines[i]:
                            break

                # 提取评分规则类型
                rule_content = '\n'.join(rule_lines)
                if 'type: threshold' in rule_content:
                    criterion['scoring_rule'] = parse_threshold_rule(rule_content)
                elif 'type: minmax' in rule_content:
                    criterion['scoring_rule'] = parse_minmax_rule(rule_content)

        config['criteria'].append(criterion)

    return config


def parse_threshold_rule(content: str) -> Dict[str, Any]:
    """解析阈值评分规则"""
    import re

    rule = {
        'type': 'threshold',
        'ranges': [],
        'default_score': 0.0
    }

    # 提取 default_score
    default_match = re.search(r'default_score:\s*([\d.]+)', content)
    if default_match:
        rule['default_score'] = float(default_match.group(1))

    # 提取 ranges
    range_pattern = r'- \{min:\s*([\d.]+)?(?:,\s*max:\s*([\d.]+))?,\s*score:\s*([\d.]+)\}'
    for match in re.finditer(range_pattern, content):
        min_val = match.group(1)
        max_val = match.group(2)
        score = match.group(3)

        range_rule = {'score': float(score)}

        if min_val is not None:
            range_rule['min'] = float(min_val)
        if max_val is not None:
            range_rule['max'] = float(max_val)

        rule['ranges'].append(range_rule)

    # 处理只有 max 或只有 min 的情况
    range_pattern2 = r'- \{(min|max):\s*([\d.]+)(?:,\s*score:\s*([\d.]+))?\}'
    for match in re.finditer(range_pattern2, content):
        key = match.group(1)
        val = float(match.group(2))
        score = float(match.group(3)) if match.group(3) else None

        # 检查是否已经处理过这个 range
        if score:
            range_rule = {'score': score}
            range_rule[key] = val

            # 检查重复
            is_duplicate = False
            for existing in rule['ranges']:
                if existing.get('score') == score:
                    is_duplicate = True
                    break

            if not is_duplicate:
                rule['ranges'].append(range_rule)

    return rule


def parse_minmax_rule(content: str) -> Dict[str, Any]:
    """解析 MinMax 评分规则"""
    import re

    rule = {
        'type': 'minmax',
        'min': 0.0,
        'max': 100.0,
        'scale': 100.0
    }

    min_match = re.search(r'min:\s*([-\d.]+)', content)
    if min_match:
        rule['min'] = float(min_match.group(1))

    max_match = re.search(r'max:\s*([-\d.]+)', content)
    if max_match:
        rule['max'] = float(max_match.group(1))

    scale_match = re.search(r'scale:\s*([\d.]+)', content)
    if scale_match:
        rule['scale'] = float(scale_match.group(1))

    return rule


def calculate_customer_scores(customers: list, config: dict) -> list:
    """计算所有客户的评分"""

    applier = ScoringApplier()
    results = []

    # 归一化权重
    total_weight = sum(c['weight'] for c in config['criteria'])
    for criterion in config['criteria']:
        criterion['weight'] /= total_weight

    for customer in customers:
        name = customer['name']
        scores = {}
        weighted_score = 0.0

        # 计算每个准则的评分
        for criterion in config['criteria']:
            crit_name = criterion['name']
            column_name = criterion.get('column') or crit_name

            # 获取原始值
            if column_name not in customer:
                raise ValueError(f"Customer {name} missing field: {column_name}")

            raw_value = customer[column_name]

            # 应用评分规则
            rule = criterion.get('scoring_rule')
            if rule:
                if rule['type'] == 'threshold':
                    score = applier.apply_threshold(raw_value, rule)
                elif rule['type'] == 'minmax':
                    score = applier.apply_minmax(raw_value, rule)
                else:
                    score = 0.0
            else:
                # 没有评分规则，直接使用原始值
                score = float(raw_value)

            scores[crit_name] = score

            # 累加加权分
            weighted_score += criterion['weight'] * score

        results.append({
            'name': name,
            'scores': scores,
            'weighted_score': weighted_score
        })

    # 按总分降序排序
    results.sort(key=lambda x: x['weighted_score'], reverse=True)

    return results


def main():
    print("=" * 120)
    print("CUSTOMER SCORING RESULTS - 客户评分结果")
    print("=" * 120)

    # 路径
    test_dir = Path(__file__).parent
    json_path = test_dir / "fixtures" / "customer_50_data.json"
    yaml_path = test_dir / "fixtures" / "customer_scoring_50.yaml"

    # 加载数据
    print("\n[1] Loading Data...")
    with open(json_path, "r", encoding="utf-8") as f:
        customers = json.load(f)
    print(f"    Customers: {len(customers)}")

    # 加载配置
    print("\n[2] Loading Configuration...")
    config = load_yaml_config(yaml_path)
    print(f"    Criteria: {len(config['criteria'])}")
    print(f"    Algorithm: {config['algorithm']['name']}")

    # 计算评分
    print("\n[3] Calculating Scores...")
    results = calculate_customer_scores(customers, config)
    print(f"    Calculation completed for {len(results)} customers")

    # 输出结果
    print("\n" + "=" * 120)
    print("TOP 10 CUSTOMERS - 前 10 名客户")
    print("=" * 120)

    print(f"{'Rank':<6s} {'Customer':<15s} {'Total':>8s} {'Details (Top 5 Criteria)':<80s}")
    print("-" * 120)

    for i, result in enumerate(results[:10], 1):
        name = result['name']
        total = result['weighted_score']

        # 获取权重最高的 5 个准则的评分
        top_criteria = sorted(
            config['criteria'],
            key=lambda x: x['weight'],
            reverse=True
        )[:5]

        details = []
        for crit in top_criteria:
            crit_name = crit['name']
            score = result['scores'][crit_name]
            weight = crit['weight']
            details.append(f"{crit_name[:12]}:{score:.1f}")

        details_str = " | ".join(details)

        print(f"{i:<6d} {name:<15s} {total:>7.2f}  {details_str:<80s}")

    print("\n" + "=" * 120)
    print("BOTTOM 10 CUSTOMERS - 后 10 名客户")
    print("=" * 120)

    print(f"{'Rank':<6s} {'Customer':<15s} {'Total':>8s} {'Details (Top 5 Criteria)':<80s}")
    print("-" * 120)

    for i, result in enumerate(results[-10:], len(results) - 9):
        name = result['name']
        total = result['weighted_score']

        # 获取权重最高的 5 个准则的评分
        top_criteria = sorted(
            config['criteria'],
            key=lambda x: x['weight'],
            reverse=True
        )[:5]

        details = []
        for crit in top_criteria:
            crit_name = crit['name']
            score = result['scores'][crit_name]
            weight = crit['weight']
            details.append(f"{crit_name[:12]}:{score:.1f}")

        details_str = " | ".join(details)

        print(f"{i:<6d} {name:<15s} {total:>7.2f}  {details_str:<80s}")

    # 详细评分示例（前 3 名）
    print("\n" + "=" * 120)
    print("DETAILED SCORES - TOP 3 CUSTOMERS (前 3 名详细评分)")
    print("=" * 120)

    for i, result in enumerate(results[:3], 1):
        print(f"\n{'#' * 50} Rank #{i}: {result['name']} {'#' * 50}")
        print(f"Total Score: {result['weighted_score']:.2f}\n")

        print(f"{'Criterion':<25s} {'Weight':>8s} {'Raw':>10s} {'Score':>8s} {'Weighted':>10s}")
        print("-" * 70)

        # 按权重排序显示
        sorted_criteria = sorted(
            config['criteria'],
            key=lambda x: x['weight'],
            reverse=True
        )

        for criterion in sorted_criteria:
            crit_name = criterion['name']
            column_name = criterion.get('column') or crit_name
            weight = criterion['weight']

            # 获取原始值
            raw_value = customers[next(
                idx for idx, c in enumerate(customers)
                if c['name'] == result['name']
            )][column_name]

            score = result['scores'][crit_name]
            weighted = weight * score

            print(f"{crit_name:<25s} {weight:>7.2%} {raw_value:>10.2f} {score:>8.2f} {weighted:>10.2f}")

    # 统计信息
    print("\n" + "=" * 120)
    print("STATISTICS - 统计信息")
    print("=" * 120)

    all_scores = [r['weighted_score'] for r in results]

    print(f"\nTotal Score Statistics:")
    print(f"  Max:  {max(all_scores):.2f}")
    print(f"  Min:  {min(all_scores):.2f}")
    print(f"  Avg:  {sum(all_scores) / len(all_scores):.2f}")
    print(f"  Std:  {(sum((x - sum(all_scores)/len(all_scores))**2 for x in all_scores) / len(all_scores))**0.5:.2f}")

    # 客户分级
    print(f"\nCustomer Grading:")
    score_80_plus = sum(1 for s in all_scores if s >= 80)
    score_70_80 = sum(1 for s in all_scores if 70 <= s < 80)
    score_60_70 = sum(1 for s in all_scores if 60 <= s < 70)
    score_below_60 = sum(1 for s in all_scores if s < 60)

    print(f"  S Grade (>=80): {score_80_plus} customers ({score_80_plus/len(all_scores)*100:.1f}%)")
    print(f"  A Grade (70-80): {score_70_80} customers ({score_70_80/len(all_scores)*100:.1f}%)")
    print(f"  B Grade (60-70): {score_60_70} customers ({score_60_70/len(all_scores)*100:.1f}%)")
    print(f"  C Grade (<60): {score_below_60} customers ({score_below_60/len(all_scores)*100:.1f}%)")

    print("\n" + "=" * 120)
    print("[END OF REPORT]")
    print("=" * 120)


if __name__ == "__main__":
    main()
