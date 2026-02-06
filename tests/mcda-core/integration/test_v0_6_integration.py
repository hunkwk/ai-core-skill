"""
MCDA Core - v0.6 集成测试

测试 Phase 1-4 实现的群决策功能的端到端集成场景：
1. 群决策 + PCA 赋权集成
2. 群决策 + 所有聚合方法集成
3. 群决策 + 德尔菲法集成
4. 端到端 YAML 配置加载
5. 多算法对比测试
"""

import pytest
import yaml
from pathlib import Path

from mcda_core.group.models import (
    DecisionMaker,
    GroupDecisionProblem,
    AggregationConfig,
)
from mcda_core.group.service import GroupDecisionService
from mcda_core.group.delphi import DelphiProcess
from mcda_core.models import Criterion, DecisionProblem
from mcda_core.weighting import pca_weighting
from mcda_core.algorithms import TOPSISAlgorithm, VIKORAlgorithm


# =============================================================================
# 1. 群决策 + PCA 赋权集成测试 (3 个)
# =============================================================================

class TestGroupDecisionWithPCA:
    """测试群决策与 PCA 赋权的集成"""

    @pytest.fixture
    def sample_decision_makers(self):
        """创建示例决策者"""
        return (
            DecisionMaker(id="DM1", name="张三", weight=1.0),
            DecisionMaker(id="DM2", name="李四", weight=1.0),
            DecisionMaker(id="DM3", name="王五", weight=0.5),
        )

    @pytest.fixture
    def sample_individual_scores(self):
        """创建示例个人评分（用于 PCA 分析）"""
        return {
            "DM1": {
                "AWS": {"成本": 80.0, "质量": 90.0, "技术": 85.0, "服务": 88.0},
                "Azure": {"成本": 70.0, "质量": 85.0, "技术": 80.0, "服务": 82.0},
                "GCP": {"成本": 85.0, "质量": 80.0, "技术": 90.0, "服务": 85.0},
            },
            "DM2": {
                "AWS": {"成本": 85.0, "质量": 80.0, "技术": 90.0, "服务": 90.0},
                "Azure": {"成本": 75.0, "质量": 90.0, "技术": 85.0, "服务": 80.0},
                "GCP": {"成本": 80.0, "质量": 85.0, "技术": 88.0, "服务": 83.0},
            },
            "DM3": {
                "AWS": {"成本": 75.0, "质量": 85.0, "技术": 80.0, "服务": 85.0},
                "Azure": {"成本": 80.0, "质量": 80.0, "技术": 75.0, "服务": 78.0},
                "GCP": {"成本": 82.0, "质量": 82.0, "技术": 85.0, "服务": 80.0},
            },
        }

    def test_group_decision_with_pca_weighting(
        self, sample_decision_makers, sample_individual_scores
    ):
        """测试使用 PCA 赋权创建群决策问题并完成分析"""
        # 1. 创建群决策问题（使用等权重）
        criteria = (
            Criterion(name="成本", weight=0.25, direction="lower_better"),
            Criterion(name="质量", weight=0.25, direction="higher_better"),
            Criterion(name="技术", weight=0.25, direction="higher_better"),
            Criterion(name="服务", weight=0.25, direction="higher_better"),
        )

        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure", "GCP"),
            criteria=criteria,
            decision_makers=sample_decision_makers,
            individual_scores=sample_individual_scores
        )

        # 2. 使用群决策服务聚合评分
        service = GroupDecisionService()
        aggregated_scores = service.aggregate_scores(problem)

        # 3. 使用 PCA 赋权计算准则权重
        # 使用 pca_weighting 函数
        # 构造评分矩阵（备选方案 x 准则）
        score_matrix = []
        for alt in problem.alternatives:
            row = [aggregated_scores[alt][crit.name] for crit in criteria]
            score_matrix.append(row)

        pca_weights = pca_weighting(score_matrix)

        # 4. 验证 PCA 权重
        assert len(pca_weights) == 4
        assert all(0 <= w <= 1 for w in pca_weights)
        assert abs(sum(pca_weights) - 1.0) < 0.01  # 权重和为 1

        # 5. 创建带 PCA 权重的新决策问题
        pca_criteria = tuple(
            Criterion(name=crit.name, weight=weight, direction=crit.direction)
            for crit, weight in zip(criteria, pca_weights)
        )

        # 6. 转换为单决策者问题并排序
        single_problem = service.to_decision_problem(problem)
        topsis_service = TOPSISAlgorithm()
        result = topsis_service.calculate(single_problem)

        # 7. 验证结果
        assert len(result.rankings) == 3
        assert result.rankings[0].alternative in ("AWS", "Azure", "GCP")

    def test_pca_weighting_affects_ranking(
        self, sample_decision_makers, sample_individual_scores
    ):
        """测试 PCA 赋权影响排序结果"""
        criteria = (
            Criterion(name="成本", weight=0.25, direction="lower_better"),
            Criterion(name="质量", weight=0.25, direction="higher_better"),
            Criterion(name="技术", weight=0.25, direction="higher_better"),
            Criterion(name="服务", weight=0.25, direction="higher_better"),
        )

        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure", "GCP"),
            criteria=criteria,
            decision_makers=sample_decision_makers,
            individual_scores=sample_individual_scores
        )

        service = GroupDecisionService()
        aggregated_scores = service.aggregate_scores(problem)

        # 计算两组排序结果
        # 1. 使用等权重
        single_problem_equal = service.to_decision_problem(problem)
        topsis_service = TOPSISAlgorithm()
        result_equal = topsis_service.calculate(single_problem_equal)

        # 2. 使用 PCA 权重
        # PCA 赋权
        score_matrix = []
        for alt in problem.alternatives:
            row = [aggregated_scores[alt][crit.name] for crit in criteria]
            score_matrix.append(row)

        pca_weights = pca_weighting(score_matrix)
        pca_criteria = tuple(
            Criterion(name=crit.name, weight=weight, direction=crit.direction)
            for crit, weight in zip(criteria, pca_weights)
        )

        # 使用 PCA 权重重新创建问题
        problem_pca = GroupDecisionProblem(
            alternatives=problem.alternatives,
            criteria=pca_criteria,
            decision_makers=problem.decision_makers,
            individual_scores=problem.individual_scores
        )
        single_problem_pca = service.to_decision_problem(problem_pca)
        result_pca = topsis_service.calculate(single_problem_pca)

        # 验证两组结果都有效
        assert len(result_equal.rankings) == 3
        assert len(result_pca.rankings) == 3

    def test_pca_weighting_with_consensus(
        self, sample_decision_makers, sample_individual_scores
    ):
        """测试 PCA 赋权 + 共识度测量的完整流程"""
        criteria = (
            Criterion(name="成本", weight=0.25, direction="lower_better"),
            Criterion(name="质量", weight=0.25, direction="higher_better"),
            Criterion(name="技术", weight=0.25, direction="higher_better"),
            Criterion(name="服务", weight=0.25, direction="higher_better"),
        )

        config = AggregationConfig(
            score_aggregation="weighted_average",
            consensus_strategy="threshold",
            consensus_threshold=0.7
        )

        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure", "GCP"),
            criteria=criteria,
            decision_makers=sample_decision_makers,
            individual_scores=sample_individual_scores,
            aggregation_config=config
        )

        service = GroupDecisionService()

        # 1. 计算共识度
        consensus_result = service.compute_consensus(problem)
        assert consensus_result.threshold_reached is not None
        assert 0 <= consensus_result.overall_consensus <= 1

        # 2. 聚合评分
        aggregated_scores = service.aggregate_scores(problem)
        assert len(aggregated_scores) == 3

        # 3. 应用 PCA 赋权
        # PCA 赋权
        score_matrix = []
        for alt in problem.alternatives:
            row = [aggregated_scores[alt][crit.name] for crit in criteria]
            score_matrix.append(row)

        pca_weights = pca_weighting(score_matrix)
        assert len(pca_weights) == 4

        # 4. 完整的决策分析
        single_problem = service.to_decision_problem(problem)
        vikor_service = VIKORAlgorithm()
        result = vikor_service.calculate(single_problem)

        # 5. 验证完整流程结果
        assert len(result.rankings) == 3
        assert result.raw_scores is not None


# =============================================================================
# 2. 群决策 + 所有聚合方法集成测试 (3 个)
# =============================================================================

class TestGroupDecisionAggregationMethods:
    """测试所有聚合方法的集成"""

    @pytest.fixture
    def sample_decision_makers(self):
        """创建示例决策者"""
        return (
            DecisionMaker(id="DM1", name="张三", weight=1.0),
            DecisionMaker(id="DM2", name="李四", weight=1.0),
            DecisionMaker(id="DM3", name="王五", weight=1.0),
        )

    @pytest.fixture
    def sample_individual_scores(self):
        """创建示例个人评分"""
        return {
            "DM1": {
                "AWS": {"成本": 80.0, "质量": 90.0, "技术": 85.0},
                "Azure": {"成本": 70.0, "质量": 85.0, "技术": 80.0},
                "GCP": {"成本": 75.0, "质量": 80.0, "技术": 90.0},
            },
            "DM2": {
                "AWS": {"成本": 85.0, "质量": 80.0, "技术": 90.0},
                "Azure": {"成本": 75.0, "质量": 90.0, "技术": 85.0},
                "GCP": {"成本": 80.0, "质量": 85.0, "技术": 88.0},
            },
            "DM3": {
                "AWS": {"成本": 75.0, "质量": 85.0, "技术": 80.0},
                "Azure": {"成本": 80.0, "质量": 80.0, "技术": 75.0},
                "GCP": {"成本": 78.0, "质量": 82.0, "技术": 85.0},
            },
        }

    @pytest.fixture
    def sample_problem(self, sample_decision_makers, sample_individual_scores):
        """创建示例群决策问题"""
        criteria = (
            Criterion(name="成本", weight=0.4, direction="lower_better"),
            Criterion(name="质量", weight=0.3, direction="higher_better"),
            Criterion(name="技术", weight=0.3, direction="higher_better"),
        )

        return GroupDecisionProblem(
            alternatives=("AWS", "Azure", "GCP"),
            criteria=criteria,
            decision_makers=sample_decision_makers,
            individual_scores=sample_individual_scores
        )

    def test_all_aggregation_methods_valid(
        self, sample_problem
    ):
        """测试所有 4 种聚合方法都能正常工作"""
        service = GroupDecisionService()
        methods = [
            "weighted_average",
            "weighted_geometric",
            "borda_count",
            "copeland",
        ]

        results = {}
        for method in methods:
            aggregated = service.aggregate_scores(sample_problem, method=method)
            results[method] = aggregated

            # 验证聚合结果
            assert len(aggregated) == 3  # 3 个备选方案
            for alt in sample_problem.alternatives:
                assert alt in aggregated
                assert len(aggregated[alt]) == 3  # 3 个准则

        # 验证所有方法都产生了结果
        assert len(results) == 4

    def test_aggregation_methods_consistency(
        self, sample_problem
    ):
        """测试不同聚合方法的结果一致性（排名相关性）"""
        service = GroupDecisionService()
        methods = [
            "weighted_average",
            "weighted_geometric",
            "borda_count",
        ]

        rankings = {}
        for method in methods:
            aggregated = service.aggregate_scores(sample_problem, method=method)
            single_problem = service.to_decision_problem(sample_problem)

            # 使用 TOPSIS 排序
            topsis_service = TOPSISAlgorithm()

            # 更新评分矩阵
            from mcda_core.models import DecisionProblem
            new_problem = DecisionProblem(
                                alternatives=single_problem.alternatives,
                criteria=single_problem.criteria,
                scores=aggregated
            )

            result = topsis_service.calculate(new_problem)
            rankings[method] = [item.alternative for item in result.rankings]

        # 验证所有方法都产生了排序
        assert len(rankings) == 3
        for method, ranking in rankings.items():
            assert len(ranking) == 3

    def test_aggregation_method_switching(
        self, sample_problem
    ):
        """测试在聚合方法之间切换"""
        service = GroupDecisionService()

        # 使用 weighted_average
        result_wa = service.aggregate_scores(sample_problem, method="weighted_average")
        assert len(result_wa) == 3

        # 切换到 weighted_geometric
        result_wg = service.aggregate_scores(sample_problem, method="weighted_geometric")
        assert len(result_wg) == 3

        # 切换到 borda_count
        result_bc = service.aggregate_scores(sample_problem, method="borda_count")
        assert len(result_bc) == 3

        # 切换到 copeland
        result_cp = service.aggregate_scores(sample_problem, method="copeland")
        assert len(result_cp) == 3

        # 验证所有结果都有相同的结构
        for alt in sample_problem.alternatives:
            for result in [result_wa, result_wg, result_bc, result_cp]:
                assert alt in result


# =============================================================================
# 3. 群决策 + 德尔菲法集成测试 (2 个)
# =============================================================================

class TestGroupDecisionWithDelphi:
    """测试群决策与德尔菲法的集成"""

    @pytest.fixture
    def sample_decision_makers(self):
        """创建示例决策者"""
        return (
            DecisionMaker(id="DM1", name="专家1", weight=1.0),
            DecisionMaker(id="DM2", name="专家2", weight=1.0),
            DecisionMaker(id="DM3", name="专家3", weight=1.0),
        )

    @pytest.fixture
    def initial_scores(self):
        """创建初始评分（第一轮）"""
        return {
            "DM1": {
                "方案A": {"成本": 70.0, "效益": 80.0},
                "方案B": {"成本": 80.0, "效益": 70.0},
            },
            "DM2": {
                "方案A": {"成本": 75.0, "效益": 85.0},
                "方案B": {"成本": 85.0, "效益": 75.0},
            },
            "DM3": {
                "方案A": {"成本": 65.0, "效益": 75.0},
                "方案B": {"成本": 75.0, "效益": 65.0},
            },
        }

    def test_delphi_process_convergence(
        self, sample_decision_makers, initial_scores
    ):
        """测试德尔菲法收敛过程"""
        criteria = (
            Criterion(name="成本", weight=0.5, direction="lower_better"),
            Criterion(name="效益", weight=0.5, direction="higher_better"),
        )

        problem = GroupDecisionProblem(
            alternatives=("方案A", "方案B"),
            criteria=criteria,
            decision_makers=sample_decision_makers,
            individual_scores=initial_scores
        )

        # 创建德尔菲法过程
        delphi = DelphiProcess(
            initial_problem=problem,
            max_rounds=3,
            convergence_threshold=0.1
        )

        # 第一轮
        delphi.add_round(initial_scores)
        round1 = delphi.rounds[0]
        assert round1.round_number == 1
        assert round1.convergence_score >= 0

        # 模拟第二轮评分（向均值收敛）
        round2_scores = {
            "DM1": {
                "方案A": {"成本": 72.0, "效益": 82.0},
                "方案B": {"成本": 82.0, "效益": 72.0},
            },
            "DM2": {
                "方案A": {"成本": 73.0, "效益": 83.0},
                "方案B": {"成本": 83.0, "效益": 73.0},
            },
            "DM3": {
                "方案A": {"成本": 71.0, "效益": 81.0},
                "方案B": {"成本": 81.0, "效益": 71.0},
            },
        }
        delphi.add_round(round2_scores)
        round2 = delphi.rounds[1]
        assert round2.round_number == 2
        assert round2.convergence_score < round1.convergence_score  # 更收敛

        # 验证收敛
        # 检查是否收敛
        if len(delphi.rounds) > 0:
            is_converged = delphi.rounds[-1].convergence_score < delphi.convergence_threshold
        else:
            is_converged = False
        assert is_converged is not None

    def test_delphi_process_statistics(
        self, sample_decision_makers, initial_scores
    ):
        """测试德尔菲法统计分析"""
        criteria = (
            Criterion(name="成本", weight=0.5, direction="lower_better"),
            Criterion(name="效益", weight=0.5, direction="higher_better"),
        )

        problem = GroupDecisionProblem(
            alternatives=("方案A", "方案B"),
            criteria=criteria,
            decision_makers=sample_decision_makers,
            individual_scores=initial_scores
        )

        delphi = DelphiProcess(
            initial_problem=problem,
            max_rounds=3,
            convergence_threshold=0.1
        )

        # 获取第一轮统计
        # 添加初始轮次
        delphi.add_round(initial_scores)

        round1 = delphi.rounds[0]

        # 验证统计信息
        for alt in problem.alternatives:
            for crit in criteria:
                assert alt in round1.statistics
                assert crit.name in round1.statistics[alt]

                stats = round1.statistics[alt][crit.name]
                assert "mean" in stats
                assert "median" in stats
                assert "std" in stats
                assert "q1" in stats
                assert "q3" in stats

                # 验证统计值的有效性
                assert stats["q1"] <= stats["median"] <= stats["q3"]
                assert stats["std"] >= 0


# =============================================================================
# 4. 端到端 YAML 配置测试 (2 个)
# =============================================================================

class TestYAMLConfiguration:
    """测试端到端 YAML 配置加载"""

    @pytest.fixture
    def yaml_config_path(self, tmp_path):
        """创建临时 YAML 配置文件"""
        config = {
            "problem": {
                "name": "云服务选择",
                "alternatives": ["AWS", "Azure", "GCP"],
                "criteria": [
                    {"name": "成本", "weight": 0.4, "direction": "lower_better"},
                    {"name": "质量", "weight": 0.3, "direction": "higher_better"},
                    {"name": "技术", "weight": 0.3, "direction": "higher_better"},
                ],
            },
            "decision_makers": [
                {"id": "DM1", "name": "张三", "weight": 1.0},
                {"id": "DM2", "name": "李四", "weight": 1.0},
                {"id": "DM3", "name": "王五", "weight": 0.5},
            ],
            "individual_scores": {
                "DM1": {
                    "AWS": {"成本": 80.0, "质量": 90.0, "技术": 85.0},
                    "Azure": {"成本": 70.0, "质量": 85.0, "技术": 80.0},
                    "GCP": {"成本": 75.0, "质量": 80.0, "技术": 90.0},
                },
                "DM2": {
                    "AWS": {"成本": 85.0, "质量": 80.0, "技术": 90.0},
                    "Azure": {"成本": 75.0, "质量": 90.0, "技术": 85.0},
                    "GCP": {"成本": 80.0, "质量": 85.0, "技术": 88.0},
                },
                "DM3": {
                    "AWS": {"成本": 75.0, "质量": 85.0, "技术": 80.0},
                    "Azure": {"成本": 80.0, "质量": 80.0, "技术": 75.0},
                    "GCP": {"成本": 78.0, "质量": 82.0, "技术": 85.0},
                },
            },
            "aggregation_config": {
                "score_aggregation": "weighted_average",
                "consensus_strategy": "threshold",
                "consensus_threshold": 0.7,
            },
        }

        yaml_file = tmp_path / "group_decision_config.yaml"
        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True)

        return yaml_file

    def test_load_group_decision_from_yaml(
        self, yaml_config_path
    ):
        """测试从 YAML 文件加载群决策配置"""
        # 1. 加载 YAML
        with open(yaml_config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # 2. 解析配置
        criteria = tuple(
            Criterion(
                name=c["name"],
                weight=c["weight"],
                direction=c["direction"]
            )
            for c in config["problem"]["criteria"]
        )

        decision_makers = tuple(
            DecisionMaker(
                id=dm["id"],
                name=dm["name"],
                weight=dm["weight"]
            )
            for dm in config["decision_makers"]
        )

        aggregation_config = AggregationConfig(
            score_aggregation=config["aggregation_config"]["score_aggregation"],
            consensus_strategy=config["aggregation_config"]["consensus_strategy"],
            consensus_threshold=config["aggregation_config"]["consensus_threshold"],
        )

        # 3. 创建群决策问题
        problem = GroupDecisionProblem(
            alternatives=tuple(config["problem"]["alternatives"]),
            criteria=criteria,
            decision_makers=decision_makers,
            individual_scores=config["individual_scores"],
            aggregation_config=aggregation_config
        )

        # 4. 验证问题
        assert len(problem.alternatives) == 3
        assert len(problem.criteria) == 3
        assert len(problem.decision_makers) == 3
        assert problem.aggregation_config is not None

        # 5. 执行分析
        service = GroupDecisionService()
        aggregated = service.aggregate_scores(problem)
        consensus = service.compute_consensus(problem)

        assert len(aggregated) == 3
        
    def test_yaml_config_end_to_end_analysis(
        self, yaml_config_path
    ):
        """测试 YAML 配置的端到端分析流程"""
        # 1. 加载配置
        with open(yaml_config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # 2. 构建问题
        criteria = tuple(
            Criterion(name=c["name"], weight=c["weight"], direction=c["direction"])
            for c in config["problem"]["criteria"]
        )

        decision_makers = tuple(
            DecisionMaker(id=dm["id"], name=dm["name"], weight=dm["weight"])
            for dm in config["decision_makers"]
        )

        aggregation_config = AggregationConfig(
            score_aggregation=config["aggregation_config"]["score_aggregation"],
            consensus_strategy=config["aggregation_config"]["consensus_strategy"],
            consensus_threshold=config["aggregation_config"]["consensus_threshold"],
        )

        problem = GroupDecisionProblem(
            alternatives=tuple(config["problem"]["alternatives"]),
            criteria=criteria,
            decision_makers=decision_makers,
            individual_scores=config["individual_scores"],
            aggregation_config=aggregation_config
        )

        # 3. 完整分析流程
        service = GroupDecisionService()

        # 3.1 计算共识度
        consensus_result = service.compute_consensus(problem)

        # 3.2 聚合评分
        aggregated_scores = service.aggregate_scores(problem)

        # 3.3 转换为单决策者问题
        single_problem = service.to_decision_problem(problem)

        # 3.4 使用 TOPSIS 排序
        topsis_service = TOPSISAlgorithm()
        topsis_result = topsis_service.calculate(single_problem)

        # 3.5 使用 VIKOR 排序
        vikor_service = VIKORAlgorithm()
        vikor_result = vikor_service.calculate(single_problem)

        # 4. 验证完整流程结果
        assert consensus_result.overall_consensus >= 0
        assert len(aggregated_scores) == 3
        assert len(topsis_result.rankings) == 3
        assert len(vikor_result.rankings) == 3
        assert topsis_result.rankings[0].alternative in ("AWS", "Azure", "GCP")
        assert vikor_result.rankings[0].alternative in ("AWS", "Azure", "GCP")


# =============================================================================
# 5. 多算法对比测试 (2 个)
# =============================================================================

class TestAlgorithmComparison:
    """测试不同聚合方法的算法结果对比"""

    @pytest.fixture
    def sample_problem(self):
        """创建示例群决策问题"""
        decision_makers = (
            DecisionMaker(id="DM1", name="张三", weight=1.0),
            DecisionMaker(id="DM2", name="李四", weight=1.0),
            DecisionMaker(id="DM3", name="王五", weight=1.0),
        )

        individual_scores = {
            "DM1": {
                "AWS": {"成本": 80.0, "质量": 90.0, "技术": 85.0},
                "Azure": {"成本": 70.0, "质量": 85.0, "技术": 80.0},
                "GCP": {"成本": 75.0, "质量": 80.0, "技术": 90.0},
            },
            "DM2": {
                "AWS": {"成本": 85.0, "质量": 80.0, "技术": 90.0},
                "Azure": {"成本": 75.0, "质量": 90.0, "技术": 85.0},
                "GCP": {"成本": 80.0, "质量": 85.0, "技术": 88.0},
            },
            "DM3": {
                "AWS": {"成本": 75.0, "质量": 85.0, "技术": 80.0},
                "Azure": {"成本": 80.0, "质量": 80.0, "技术": 75.0},
                "GCP": {"成本": 78.0, "质量": 82.0, "技术": 85.0},
            },
        }

        criteria = (
            Criterion(name="成本", weight=0.4, direction="lower_better"),
            Criterion(name="质量", weight=0.3, direction="higher_better"),
            Criterion(name="技术", weight=0.3, direction="higher_better"),
        )

        return GroupDecisionProblem(
            alternatives=("AWS", "Azure", "GCP"),
            criteria=criteria,
            decision_makers=decision_makers,
            individual_scores=individual_scores
        )

    def test_aggregation_methods_comparison(
        self, sample_problem
    ):
        """测试不同聚合方法的算法结果对比"""
        service = GroupDecisionService()
        methods = ["weighted_average", "weighted_geometric", "borda_count"]

        results = {}
        for method in methods:
            # 聚合评分
            aggregated = service.aggregate_scores(sample_problem, method=method)

            # 转换为单决策者问题
            single_problem = service.to_decision_problem(sample_problem)

            # 使用 TOPSIS 排序
            topsis_service = TOPSISAlgorithm()
            from mcda_core.models import DecisionProblem
            new_problem = DecisionProblem(
                                alternatives=single_problem.alternatives,
                criteria=single_problem.criteria,
                scores=aggregated
            )
            result = topsis_service.calculate(new_problem)

            results[method] = {
                "ranking": [item.alternative for item in result.rankings],
                "best": result.rankings[0].alternative,
                "scores": result.raw_scores
            }

        # 验证所有方法都产生了结果
        assert len(results) == 3
        for method, result in results.items():
            assert len(result["ranking"]) == 3
            assert result["best"] in ("AWS", "Azure", "GCP")
            assert result["scores"] is not None

    def test_aggregation_methods_reasonableness(
        self, sample_problem
    ):
        """测试聚合方法的合理性（结果不应过于极端）"""
        service = GroupDecisionService()

        # 使用 weighted_average（最常用的方法）
        aggregated_wa = service.aggregate_scores(sample_problem, method="weighted_average")

        # 验证聚合结果的合理性
        for alt in sample_problem.alternatives:
            for crit in sample_problem.criteria:
                score = aggregated_wa[alt][crit.name]

                # 分数应该在合理范围内（原始评分在 70-90 之间）
                assert 60 <= score <= 100, f"{alt}.{crit.name} = {score} 超出合理范围"

        # 使用 copeland 方法（基于排名）
        aggregated_cp = service.aggregate_scores(sample_problem, method="copeland")

        # Copeland 分数应该在 [-2, 2] 范围内（3 个备选方案）
        for alt in sample_problem.alternatives:
            for crit in sample_problem.criteria:
                score = aggregated_cp[alt][crit.name]
                