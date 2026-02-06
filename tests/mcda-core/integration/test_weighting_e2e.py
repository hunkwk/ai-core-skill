"""
MCDA Core - 权重计算 E2E 测试

测试各种客观权重计算方法的端到端功能。
"""

import pytest
import numpy as np

from mcda_core.core import MCDAOrchestrator
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.weighting import (
    cv_weighting,
    critic_weighting,
    GameTheoryWeighting,
    pca_weighting,
)
from mcda_core.services import (
    EntropyWeightService,
    AHPService,
)


class TestWeightingMethods:
    """权重计算方法端到端测试"""

    def test_cv_weighting(self):
        """测试: 变异系数法 (CV) 权重计算"""
        # 决策矩阵: 4 个方案 × 3 个准则
        matrix = np.array([
            [85, 70, 90],  # 方案 A
            [75, 80, 85],  # 方案 B
            [90, 65, 95],  # 方案 C
            [80, 75, 88],  # 方案 D
        ])

        # 计算 CV 权重
        weights = cv_weighting(matrix)

        # 验证权重
        assert len(weights) == 3  # 3 个准则
        assert np.allclose(weights.sum(), 1.0, atol=1e-6)  # 权重和为 1
        assert all(w > 0 for w in weights)  # 所有权重为正

    def test_critic_weighting(self):
        """测试: CRITIC 权重计算"""
        matrix = np.array([
            [85, 70, 90, 80],
            [75, 80, 85, 75],
            [90, 65, 95, 85],
            [80, 75, 88, 78],
        ])

        # 计算 CRITIC 权重
        weights = critic_weighting(matrix)

        # 验证权重
        assert len(weights) == 4
        assert np.allclose(weights.sum(), 1.0, atol=1e-6)
        assert all(w > 0 for w in weights)

    def test_entropy_weighting(self):
        """测试: 熵权法权重计算"""
        matrix = np.array([
            [85, 70, 90],
            [75, 80, 85],
            [90, 65, 95],
            [80, 75, 88],
        ])

        # 使用 EntropyWeightService
        service = EntropyWeightService()
        weights = service.calculate_weights(matrix)

        # 验证权重
        assert len(weights) == 3
        assert np.allclose(weights.sum(), 1.0, atol=1e-6)
        assert all(w > 0 for w in weights)

    def test_game_theory_weighting(self):
        """测试: 博弈论组合权重"""
        # 多种权重方法的结果
        cv_weights = np.array([0.3, 0.4, 0.3])
        entropy_weights = np.array([0.35, 0.35, 0.3])
        critic_weights = np.array([0.25, 0.45, 0.3])

        # 使用博弈论组合
        gt = GameTheoryWeighting()
        combined_weights = gt.combine_weights(
            np.array([cv_weights, entropy_weights, critic_weights])
        )

        # 验证组合权重
        assert len(combined_weights) == 3
        assert np.allclose(combined_weights.sum(), 1.0, atol=1e-6)
        assert all(w > 0 for w in combined_weights)

    def test_ahp_weighting(self):
        """测试: AHP (层次分析法) 权重计算"""
        # 判断矩阵
        judgment_matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 2],
            [1/5, 1/2, 1],
        ])

        # 使用 AHPService
        service = AHPService()
        weights = service.calculate_weights(judgment_matrix)

        # 验证权重
        assert len(weights) == 3
        assert np.allclose(weights.sum(), 1.0, atol=1e-6)
        assert all(w > 0 for w in weights)

        # 验证一致性比率 (CR < 0.1)
        cr = service.calculate_consistency_ratio(judgment_matrix)
        assert cr < 0.1

    def test_pca_weighting(self):
        """测试: PCA (主成分分析) 权重计算"""
        matrix = np.array([
            [85, 70, 90, 80],
            [75, 80, 85, 75],
            [90, 65, 95, 85],
            [80, 75, 88, 78],
            [82, 72, 92, 82],
        ])

        # 计算 PCA 权重
        weights = pca_weighting(matrix)

        # 验证权重
        assert len(weights) == 4
        assert np.allclose(weights.sum(), 1.0, atol=1e-6)
        assert all(w >= 0 for w in weights)

    def test_weighting_to_orchestrator_integration(self):
        """测试: 权重计算与编排器集成"""
        # 1. 原始决策矩阵
        matrix = np.array([
            [85, 70, 90],
            [75, 80, 85],
            [90, 65, 95],
        ])

        # 2. 计算权重
        service = EntropyWeightService()
        weights = service.calculate_weights(matrix)

        # 3. 创建带计算权重的 DecisionProblem
        criteria = [
            Criterion(name="性能", weight=weights[0], direction="higher_better"),
            Criterion(name="成本", weight=weights[1], direction="lower_better"),
            Criterion(name="质量", weight=weights[2], direction="higher_better"),
        ]

        problem = DecisionProblem(
            alternatives=("方案A", "方案B", "方案C"),
            criteria=tuple(criteria),
            scores={
                "方案A": {"性能": 85, "成本": 70, "质量": 90},
                "方案B": {"性能": 75, "成本": 80, "质量": 85},
                "方案C": {"性能": 90, "成本": 65, "质量": 95},
            }
        )

        # 4. 使用编排器分析
        orchestrator = MCDAOrchestrator()
        result = orchestrator.analyze(problem, algorithm_name="wsm")

        # 验证分析结果
        assert result is not None
        assert len(result.rankings) == 3

    def test_compare_weighting_methods(self):
        """测试: 对比不同权重计算方法"""
        matrix = np.array([
            [85, 70, 90],
            [75, 80, 85],
            [90, 65, 95],
            [80, 75, 88],
        ])

        # 计算不同方法的权重
        cv_weights = cv_weighting(matrix)
        critic_weights = critic_weighting(matrix)

        service = EntropyWeightService()
        entropy_weights = service.calculate_weights(matrix)

        # 验证所有方法都返回有效权重
        for weights in [cv_weights, critic_weights, entropy_weights]:
            assert len(weights) == 3
            assert np.allclose(weights.sum(), 1.0, atol=1e-6)
            assert all(w > 0 for w in weights)

        # 验证不同方法给出不同权重
        # (虽然可能相似，但不应完全相同)
        assert not np.allclose(cv_weights, entropy_weights, atol=1e-3)

    def test_weighting_with_single_criterion(self):
        """测试: 单准则情况下的权重计算"""
        matrix = np.array([
            [85],
            [75],
            [90],
        ])

        # CV 方法应该返回 [1.0]
        weights = cv_weighting(matrix)
        assert len(weights) == 1
        assert np.allclose(weights[0], 1.0)

    def test_weighting_with_single_alternative(self):
        """测试: 单方案情况下的权重计算"""
        matrix = np.array([
            [85, 70, 90]
        ])

        # CV 方法应该返回均匀权重
        weights = cv_weighting(matrix)
        assert len(weights) == 3
        assert np.allclose(weights, [1/3, 1/3, 1/3], atol=1e-6)
