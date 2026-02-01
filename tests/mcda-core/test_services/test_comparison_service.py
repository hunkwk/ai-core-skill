"""
算法对比服务测试

测试多算法结果对比功能。
"""

import pytest
import numpy as np
from mcda_core.services.comparison_service import (
    ComparisonService,
    ComparisonValidationError
)


class TestCompareAlgorithms:
    """算法对比测试"""

    def test_compare_two_algorithms(self):
        """测试：对比两个算法"""
        decision_matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
            [20, 30, 40],
        ])

        weights = np.array([0.5, 0.3, 0.2])

        service = ComparisonService()

        # 对比 WSM 和 TOPSIS
        result = service.compare_algorithms(
            decision_matrix,
            weights,
            algorithms=["wsm", "topsis"]
        )

        # 验证返回结构
        assert "rankings" in result
        assert "correlations" in result
        assert "differences" in result

        # 验证排名数量
        assert len(result["rankings"]) == 2  # 两个算法
        assert len(result["rankings"][0]["ranking"]) == 3  # 3个方案

    def test_compare_multiple_algorithms(self):
        """测试：对比多个算法"""
        decision_matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
            [20, 30, 40],
            [25, 35, 45],
        ])

        weights = np.array([0.4, 0.3, 0.3])

        service = ComparisonService()

        # 对比 4 个算法
        result = service.compare_algorithms(
            decision_matrix,
            weights,
            algorithms=["wsm", "wpm", "topsis", "vikor"]
        )

        # 验证
        assert len(result["rankings"]) == 4
        assert len(result["correlations"]) > 0

    def test_compare_with_criteria_directions(self):
        """测试：带准则方向的对比"""
        decision_matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
        ])

        weights = np.array([0.5, 0.3, 0.2])

        # 第一个准则越大越好，第二个越小越好
        criteria_directions = ["higher_better", "lower_better", "higher_better"]

        service = ComparisonService()

        result = service.compare_algorithms(
            decision_matrix,
            weights,
            algorithms=["wsm", "topsis"],
            criteria_directions=criteria_directions
        )

        # 验证结果包含方向信息
        assert "rankings" in result

    def test_invalid_algorithm_name(self):
        """测试：无效的算法名称"""
        decision_matrix = np.array([
            [10, 20],
            [15, 25],
        ])

        weights = np.array([0.6, 0.4])

        service = ComparisonService()

        with pytest.raises(ComparisonValidationError, match="算法"):
            service.compare_algorithms(
                decision_matrix,
                weights,
                algorithms=["invalid_algorithm"]
            )


class TestRankingCorrelation:
    """排名相关性测试"""

    def test_spearman_correlation_identical(self):
        """测试：完全相同的排名（相关系数 = 1）"""
        ranking1 = [0, 1, 2, 3]  # 方案A排第0，B排第1...
        ranking2 = [0, 1, 2, 3]

        service = ComparisonService()
        correlation = service.calculate_ranking_correlation(ranking1, ranking2)

        # Spearman 相关系数应该为 1
        assert abs(correlation - 1.0) < 0.0001

    def test_spearman_correlation_opposite(self):
        """测试：完全相反的排名（相关系数 = -1）"""
        ranking1 = [0, 1, 2, 3]
        ranking2 = [3, 2, 1, 0]  # 完全相反

        service = ComparisonService()
        correlation = service.calculate_ranking_correlation(ranking1, ranking2)

        # Spearman 相关系数应该为 -1
        assert abs(correlation - (-1.0)) < 0.0001

    def test_spearman_correlation_partial(self):
        """测试：部分相关的排名"""
        ranking1 = [0, 1, 2, 3, 4]
        ranking2 = [0, 2, 1, 4, 3]  # 部分不同

        service = ComparisonService()
        correlation = service.calculate_ranking_correlation(ranking1, ranking2)

        # 相关系数应该在 -1 和 1 之间
        assert -1 <= correlation <= 1

    def test_correlation_different_length(self):
        """测试：不同长度的排名"""
        ranking1 = [0, 1, 2]
        ranking2 = [0, 1, 2, 3]

        service = ComparisonService()

        with pytest.raises(ValueError, match="长度"):
            service.calculate_ranking_correlation(ranking1, ranking2)


class TestIdentifyDifferences:
    """识别排名差异测试"""

    def test_identify_no_differences(self):
        """测试：完全相同的排名（无差异）"""
        rankings = {
            "wsm": [0, 1, 2],
            "topsis": [0, 1, 2]
        }

        service = ComparisonService()
        differences = service.identify_ranking_differences(rankings)

        # 应该没有差异
        assert len(differences) == 0

    def test_identify_differences(self):
        """测试：识别排名差异"""
        rankings = {
            "wsm": [0, 1, 2],
            "topsis": [1, 0, 2]  # A和B排名互换
        }

        service = ComparisonService()
        differences = service.identify_ranking_differences(rankings)

        # 应该识别出差异
        assert len(differences) > 0

        # 验证差异信息
        diff = differences[0]
        assert "alternative" in diff
        assert "algorithms" in diff
        assert "ranks" in diff

    def test_identify_differences_multiple(self):
        """测试：多个方案的排名差异"""
        rankings = {
            "wsm": [0, 1, 2, 3],
            "topsis": [1, 0, 3, 2],
            "vikor": [2, 1, 0, 3]
        }

        service = ComparisonService()
        differences = service.identify_ranking_differences(rankings)

        # 应该识别出多个差异
        assert len(differences) > 0


class TestFullWorkflow:
    """完整工作流测试"""

    def test_comparison_full_workflow(self):
        """测试：完整的算法对比工作流"""
        decision_matrix = np.array([
            [80, 5, 100],   # 供应商 A
            [90, 3, 120],   # 供应商 B
            [70, 7, 90],    # 供应商 C
        ])

        weights = np.array([0.4, 0.3, 0.3])

        alternatives = ["Supplier A", "Supplier B", "Supplier C"]

        service = ComparisonService()

        result = service.compare_algorithms(
            decision_matrix,
            weights,
            algorithms=["wsm", "topsis", "vikor"],
            alternatives=alternatives
        )

        # 验证返回结构
        assert "rankings" in result
        assert "correlations" in result
        assert "differences" in result
        assert "summary" in result

        # 验证每个算法的排名包含方案名称
        for algo_result in result["rankings"]:
            assert "algorithm" in algo_result
            assert "ranking" in algo_result
            assert len(algo_result["ranking"]) == 3

    def test_comparison_report_generation(self):
        """测试：生成对比报告"""
        decision_matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
        ])

        weights = np.array([0.5, 0.3, 0.2])

        service = ComparisonService()

        result = service.compare_algorithms(
            decision_matrix,
            weights,
            algorithms=["wsm", "topsis"]
        )

        # 生成文本报告
        report = service.generate_comparison_report(result)

        # 验证报告内容
        assert len(report) > 0
        assert "WSM" in report or "wsm" in report
        assert "TOPSIS" in report or "topsis" in report


class TestEdgeCases:
    """边界条件测试"""

    def test_single_alternative(self):
        """测试：单个方案"""
        decision_matrix = np.array([
            [10, 20, 30],
        ])

        weights = np.array([0.5, 0.3, 0.2])

        service = ComparisonService()

        result = service.compare_algorithms(
            decision_matrix,
            weights,
            algorithms=["wsm", "topsis"]
        )

        # 单个方案，所有算法应该给出相同排名
        assert len(result["rankings"][0]["ranking"]) == 1

    def test_two_alternatives_minimum(self):
        """测试：最少2个方案"""
        decision_matrix = np.array([
            [10, 20],
            [15, 25],
        ])

        weights = np.array([0.6, 0.4])

        service = ComparisonService()

        result = service.compare_algorithms(
            decision_matrix,
            weights,
            algorithms=["wsm"]
        )

        assert len(result["rankings"][0]["ranking"]) == 2

    def test_large_dataset(self):
        """测试：大规模数据集"""
        n_alternatives = 50
        n_criteria = 10

        # 生成随机数据
        np.random.seed(42)
        decision_matrix = np.random.rand(n_alternatives, n_criteria) * 100
        weights = np.random.rand(n_criteria)
        weights = weights / np.sum(weights)

        service = ComparisonService()

        result = service.compare_algorithms(
            decision_matrix,
            weights,
            algorithms=["wsm", "topsis"]
        )

        # 验证
        assert len(result["rankings"]) == 2
        assert len(result["rankings"][0]["ranking"]) == n_alternatives


class TestErrorHandling:
    """错误处理测试"""

    def test_invalid_matrix_shape(self):
        """测试：无效矩阵形状"""
        decision_matrix = np.array([10, 20, 30])  # 1D 数组
        weights = np.array([0.5, 0.3, 0.2])

        service = ComparisonService()

        with pytest.raises(ComparisonValidationError):
            service.compare_algorithms(
                decision_matrix,
                weights,
                algorithms=["wsm"]
            )

    def test_mismatched_weights_count(self):
        """测试：权重数量不匹配"""
        decision_matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
        ])

        weights = np.array([0.5, 0.5])  # 2个权重，但矩阵有3列

        service = ComparisonService()

        with pytest.raises(ValueError, match="权重"):
            service.compare_algorithms(
                decision_matrix,
                weights,
                algorithms=["wsm"]
            )

    def test_empty_algorithm_list(self):
        """测试：空算法列表"""
        decision_matrix = np.array([
            [10, 20],
            [15, 25],
        ])

        weights = np.array([0.6, 0.4])

        service = ComparisonService()

        with pytest.raises(ComparisonValidationError, match="算法"):
            service.compare_algorithms(
                decision_matrix,
                weights,
                algorithms=[]
            )
