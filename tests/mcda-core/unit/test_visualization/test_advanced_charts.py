"""
高级可视化图表单元测试

测试高级分析和可视化功能：
- 敏感性分析热力图
- 决策路径追踪图
- 权重敏感性分析
- 方案稳定性分析
"""

import pytest
from pathlib import Path
import sys
import numpy as np

# 添加路径
project_root = Path(__file__).parent.parent.parent.parent.parent
mcda_core_path = project_root / "skills" / "mcda-core" / "scripts"
if str(mcda_core_path) not in sys.path:
    sys.path.insert(0, str(mcda_core_path))

from visualization.advanced_charts import AdvancedChartGenerator


class TestSensitivityAnalysis:
    """敏感性分析测试"""

    def test_plot_sensitivity_heatmap(self):
        """测试敏感性分析热力图"""
        generator = AdvancedChartGenerator()

        sensitivity_data = {
            ('方案A', '成本'): 0.85,
            ('方案A', '质量'): 0.72,
            ('方案B', '成本'): 0.63,
            ('方案B', '质量'): 0.91,
            ('方案C', '成本'): 0.55,
            ('方案C', '质量'): 0.68
        }

        fig = generator.plot_sensitivity_heatmap(
            sensitivity_data=sensitivity_data,
            alternatives=['方案A', '方案B', '方案C'],
            criteria=['成本', '质量']
        )

        assert fig is not None

    def test_compute_sensitivity_indices(self):
        """测试计算敏感性指数"""
        generator = AdvancedChartGenerator()

        # 创建示例决策矩阵
        decision_matrix = np.array([
            [80, 75, 90],
            [70, 85, 80],
            [85, 70, 75]
        ])

        weights = np.array([0.3, 0.4, 0.3])
        direction = ['higher_better', 'higher_better', 'higher_better']

        sensitivity = generator.compute_sensitivity_indices(
            decision_matrix, weights, direction
        )

        assert isinstance(sensitivity, dict)
        assert len(sensitivity) > 0

    def test_sensitivity_with_different_directions(self):
        """测试混合标准方向的敏感性分析"""
        generator = AdvancedChartGenerator()

        decision_matrix = np.array([
            [80, 50, 90],
            [70, 60, 80],
            [85, 45, 75]
        ])

        weights = np.array([0.3, 0.4, 0.3])
        direction = ['higher_better', 'lower_better', 'higher_better']

        sensitivity = generator.compute_sensitivity_indices(
            decision_matrix, weights, direction
        )

        assert sensitivity is not None


class TestDecisionPath:
    """决策路径追踪测试"""

    def test_plot_decision_path(self):
        """测试决策路径追踪图"""
        generator = AdvancedChartGenerator()

        path_data = {
            '方案A': [(0.3, 0.4), (0.5, 0.6), (0.7, 0.8)],
            '方案B': [(0.4, 0.3), (0.6, 0.5), (0.8, 0.7)],
            '方案C': [(0.2, 0.3), (0.4, 0.5), (0.6, 0.7)]
        }

        fig = generator.plot_decision_path(path_data)

        assert fig is not None

    def test_plot_ranking_evolution(self):
        """测试排名演化图"""
        generator = AdvancedChartGenerator()

        rankings_data = {
            '方案A': [2, 1, 1, 2],
            '方案B': [1, 2, 3, 1],
            '方案C': [3, 3, 2, 3]
        }

        stages = ['阶段1', '阶段2', '阶段3', '阶段4']

        fig = generator.plot_ranking_evolution(rankings_data, stages)

        assert fig is not None


class TestWeightSensitivity:
    """权重敏感性分析测试"""

    def test_plot_weight_sensitivity(self):
        """测试权重敏感性分析图"""
        generator = AdvancedChartGenerator()

        weight_changes = {
            '成本': np.linspace(0.2, 0.4, 10),
            '质量': np.linspace(0.3, 0.5, 10),
            '时间': np.linspace(0.2, 0.3, 10)
        }

        score_changes = {
            '方案A': np.linspace(0.7, 0.8, 10),
            '方案B': np.linspace(0.6, 0.75, 10),
            '方案C': np.linspace(0.65, 0.7, 10)
        }

        fig = generator.plot_weight_sensitivity(weight_changes, score_changes)

        assert fig is not None


class TestStabilityAnalysis:
    """稳定性分析测试"""

    def test_plot_stability_analysis(self):
        """测试方案稳定性分析图"""
        generator = AdvancedChartGenerator()

        stability_scores = {
            '方案A': 0.75,
            '方案B': 0.68,
            '方案C': 0.82
        }

        confidence_intervals = {
            '方案A': (0.70, 0.80),
            '方案B': (0.62, 0.74),
            '方案C': (0.78, 0.86)
        }

        fig = generator.plot_stability_analysis(
            stability_scores, confidence_intervals
        )

        assert fig is not None


class TestComprehensiveAnalysis:
    """综合分析测试"""

    def test_plot_comprehensive_sensitivity(self):
        """测试综合敏感性分析图"""
        generator = AdvancedChartGenerator()

        decision_matrix = np.array([
            [80, 75, 90, 85],
            [70, 85, 80, 75],
            [85, 70, 75, 80],
            [75, 80, 85, 70]
        ])

        weights = np.array([0.25, 0.35, 0.25, 0.15])
        alternatives = ['方案A', '方案B', '方案C', '方案D']
        criteria = ['成本', '质量', '时间', '风险']
        direction = ['higher_better', 'higher_better', 'lower_better', 'lower_better']

        fig = generator.plot_comprehensive_sensitivity(
            decision_matrix, weights, alternatives, criteria, direction
        )

        assert fig is not None


class TestUtilityMethods:
    """工具方法测试"""

    def test_normalize_matrix_higher_better(self):
        """测试标准化矩阵（效益型）"""
        generator = AdvancedChartGenerator()

        matrix = np.array([
            [80, 75],
            [70, 85],
            [85, 70]
        ])

        normalized = generator._normalize_matrix(
            matrix, ['higher_better', 'higher_better']
        )

        assert normalized.shape == matrix.shape
        assert np.all(normalized >= 0)
        assert np.all(normalized <= 1)

    def test_normalize_matrix_mixed(self):
        """测试标准化矩阵（混合型）"""
        generator = AdvancedChartGenerator()

        matrix = np.array([
            [80, 50],
            [70, 60],
            [85, 45]
        ])

        normalized = generator._normalize_matrix(
            matrix, ['higher_better', 'lower_better']
        )

        assert normalized.shape == matrix.shape

    def test_compute_topsis_scores(self):
        """测试 TOPSIS 得分计算"""
        generator = AdvancedChartGenerator()

        normalized = np.array([
            [0.5, 0.6, 0.7],
            [0.6, 0.5, 0.6],
            [0.7, 0.7, 0.5]
        ])

        weights = np.array([0.3, 0.4, 0.3])

        scores = generator._compute_topsis_scores(normalized, weights)

        assert len(scores) == 3
        assert np.all(scores >= 0)
        assert np.all(scores <= 1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
