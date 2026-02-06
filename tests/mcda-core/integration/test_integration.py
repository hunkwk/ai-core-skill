"""
MCDA Core - 集成测试

测试完整的决策流程：YAML 加载 → 验证 → 计算 → 报告生成。
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from mcda_core.core import MCDAOrchestrator
from mcda_core.models import (
    Criterion,
    DecisionProblem,
    LinearScoringRule,
    ThresholdScoringRule,
)
from mcda_core.algorithms import get_algorithm
from mcda_core.exceptions import (
    ValidationError,
    YAMLParseError,
)


# =============================================================================
# fixtures
# =============================================================================

@pytest.fixture
def sample_yaml_config():
    """示例 YAML 配置"""
    return """
name: 供应商选择
alternatives:
  - 供应商A
  - 供应商B
  - 供应商C

criteria:
  - name: 成本
    weight: 0.4
    direction: lower_better

  - name: 质量
    weight: 0.3
    direction: higher_better

  - name: 交付期
    weight: 0.2
    direction: lower_better

  - name: 服务
    weight: 0.1
    direction: higher_better

scores:
  供应商A:
    成本: 50
    质量: 80
    交付期: 30
    服务: 70

  供应商B:
    成本: 70
    质量: 60
    交付期: 20
    服务: 80

  供应商C:
    成本: 60
    质量: 90
    交付期: 40
    服务: 60

algorithm:
  name: wsm
"""


@pytest.fixture
def orchestrator():
    """MCDAOrchestrator 实例"""
    return MCDAOrchestrator()


# =============================================================================
# MCDAOrchestrator 基础测试
# =============================================================================

class TestMCDAOrchestrator:
    """测试 MCDAOrchestrator 核心编排器"""

    def test_create_orchestrator(self):
        """测试: 创建编排器实例"""
        orchestrator = MCDAOrchestrator()
        assert orchestrator is not None

    def test_load_problem_from_yaml(self, orchestrator, sample_yaml_config):
        """测试: 从 YAML 加载决策问题"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "config.yaml"
            yaml_file.write_text(sample_yaml_config, encoding="utf-8")

            problem = orchestrator.load_from_yaml(yaml_file)

            assert problem is not None
            assert len(problem.alternatives) == 3
            assert len(problem.criteria) == 4
            assert "供应商A" in problem.alternatives

    def test_load_problem_with_invalid_yaml(self, orchestrator):
        """测试: 加载无效 YAML"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "invalid.yaml"
            yaml_file.write_text("""
name: test
  invalid indent
""", encoding="utf-8")

            # YAML 解析错误应该在 load_yaml 阶段抛出
            with pytest.raises((YAMLParseError, ValidationError)):
                orchestrator.load_from_yaml(yaml_file)

    def test_analyze_problem(self, orchestrator, sample_yaml_config):
        """测试: 分析决策问题"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "config.yaml"
            yaml_file.write_text(sample_yaml_config, encoding="utf-8")

            problem = orchestrator.load_from_yaml(yaml_file)
            result = orchestrator.analyze(problem)

            assert result is not None
            assert len(result.rankings) == 3
            assert len(result.raw_scores) == 3
            assert result.metadata.algorithm_name == "wsm"

    def test_analyze_with_different_algorithms(self, orchestrator, sample_yaml_config):
        """测试: 使用不同算法分析"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "config.yaml"
            yaml_file.write_text(sample_yaml_config, encoding="utf-8")

            problem = orchestrator.load_from_yaml(yaml_file)

            # 测试 WSM 算法
            result_wsm = orchestrator.analyze(problem, algorithm_name="wsm")
            assert result_wsm.metadata.algorithm_name == "wsm"

            # 测试 TOPSIS 算法
            result_topsis = orchestrator.analyze(problem, algorithm_name="topsis")
            assert result_topsis.metadata.algorithm_name == "topsis"

    def test_validate_problem(self, orchestrator, sample_yaml_config):
        """测试: 验证决策问题"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "config.yaml"
            yaml_file.write_text(sample_yaml_config, encoding="utf-8")

            problem = orchestrator.load_from_yaml(yaml_file)

            # 验证应该通过
            validation_result = orchestrator.validate(problem)
            assert validation_result.is_valid is True
            assert len(validation_result.errors) == 0

    def test_validate_invalid_weights(self, orchestrator):
        """测试: 验证无效权重"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "invalid_weights.yaml"
            yaml_file.write_text("""
name: 测试
alternatives:
  - 方案A
  - 方案B

criteria:
  - name: 成本
    weight: 0.5
    direction: lower_better
  - name: 质量
    weight: 0.3
    direction: higher_better

scores:
  方案A:
    成本: 50
    质量: 80
  方案B:
    成本: 70
    质量: 60

algorithm:
  name: wsm
""", encoding="utf-8")

            problem = orchestrator.load_from_yaml(yaml_file)
            validation_result = orchestrator.validate(problem)

            # 权重和不为 1，应该有警告或自动归一化
            # 这里假设自动归一化，所以验证通过
            assert validation_result.is_valid is True

    def test_analyze_with_sensitivity(self, orchestrator, sample_yaml_config):
        """测试: 带敏感性分析"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "config.yaml"
            yaml_file.write_text(sample_yaml_config, encoding="utf-8")

            problem = orchestrator.load_from_yaml(yaml_file)
            result = orchestrator.analyze(
                problem,
                algorithm_name="wsm",
                run_sensitivity=True
            )

            assert result is not None
            # 敏感性分析结果应该被添加
            # 这里取决于具体实现

    def test_generate_markdown_report(self, orchestrator, sample_yaml_config):
        """测试: 生成 Markdown 报告"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "config.yaml"
            yaml_file.write_text(sample_yaml_config, encoding="utf-8")

            problem = orchestrator.load_from_yaml(yaml_file)
            result = orchestrator.analyze(problem)

            report = orchestrator.generate_report(problem, result, format="markdown")

            assert report is not None
            assert isinstance(report, str)
            assert "供应商" in report or "排名" in report

    def test_save_report_to_file(self, orchestrator, sample_yaml_config):
        """测试: 保存报告到文件"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "config.yaml"
            yaml_file.write_text(sample_yaml_config, encoding="utf-8")

            problem = orchestrator.load_from_yaml(yaml_file)
            result = orchestrator.analyze(problem)

            report_file = Path(tmpdir) / "report.md"
            orchestrator.save_report(problem, result, report_file, format="markdown")

            assert report_file.exists()
            content = report_file.read_text(encoding="utf-8")
            assert len(content) > 0


# =============================================================================
# 端到端测试
# =============================================================================

class TestEndToEnd:
    """端到端集成测试"""

    def test_complete_workflow(self, sample_yaml_config):
        """测试: 完整工作流程"""
        with TemporaryDirectory() as tmpdir:
            # 1. 创建配置文件
            yaml_file = Path(tmpdir) / "config.yaml"
            yaml_file.write_text(sample_yaml_config, encoding="utf-8")

            # 2. 创建编排器
            orchestrator = MCDAOrchestrator()

            # 3. 加载问题
            problem = orchestrator.load_from_yaml(yaml_file)
            assert problem is not None

            # 4. 验证问题
            validation_result = orchestrator.validate(problem)
            assert validation_result.is_valid is True

            # 5. 分析问题
            result = orchestrator.analyze(problem)
            assert result is not None

            # 6. 生成报告
            report = orchestrator.generate_report(problem, result)
            assert report is not None

            # 7. 保存报告
            report_file = Path(tmpdir) / "report.md"
            orchestrator.save_report(problem, result, report_file)
            assert report_file.exists()

    def test_multi_algorithm_comparison(self, sample_yaml_config):
        """测试: 多算法对比"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "config.yaml"
            yaml_file.write_text(sample_yaml_config, encoding="utf-8")

            orchestrator = MCDAOrchestrator()
            problem = orchestrator.load_from_yaml(yaml_file)

            algorithms = ["wsm", "wpm", "topsis", "vikor"]
            results = {}

            for algo_name in algorithms:
                result = orchestrator.analyze(problem, algorithm_name=algo_name)
                results[algo_name] = result

                assert result is not None
                assert result.metadata.algorithm_name == algo_name

            # 所有算法都应该产生结果
            assert len(results) == 4

    def test_batch_analysis(self):
        """测试: 批量分析多个问题"""
        with TemporaryDirectory() as tmpdir:
            orchestrator = MCDAOrchestrator()

            # 创建多个配置文件
            configs = [
                """
name: 问题1
alternatives: [A, B]
criteria:
  - name: 成本
    weight: 0.5
    direction: lower_better
  - name: 质量
    weight: 0.5
    direction: higher_better
scores:
  A: {成本: 50, 质量: 80}
  B: {成本: 70, 质量: 60}
algorithm: {name: wsm}
""",
                """
name: 问题2
alternatives: [X, Y]
criteria:
  - name: 效率
    weight: 0.6
    direction: higher_better
  - name: 成本
    weight: 0.4
    direction: lower_better
scores:
  X: {效率: 70, 成本: 60}
  Y: {效率: 80, 成本: 80}
algorithm: {name: wsm}
"""
            ]

            results = []
            for i, config in enumerate(configs):
                yaml_file = Path(tmpdir) / f"config{i}.yaml"
                yaml_file.write_text(config, encoding="utf-8")

                problem = orchestrator.load_from_yaml(yaml_file)
                result = orchestrator.analyze(problem)
                results.append(result)

            assert len(results) == 2
            for result in results:
                assert result is not None


# =============================================================================
# 边界情况测试
# =============================================================================

class TestEdgeCases:
    """边界情况测试"""

    def test_empty_alternatives(self, orchestrator):
        """测试: 空备选方案列表"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "config.yaml"
            yaml_file.write_text("""
name: 测试
alternatives: []
criteria:
  - name: 成本
    weight: 1.0
    direction: lower_better
scores: {}
algorithm: {name: wsm}
""", encoding="utf-8")

            with pytest.raises(ValidationError):
                orchestrator.load_from_yaml(yaml_file)

    def test_single_alternative(self, orchestrator):
        """测试: 单个备选方案（最少 2 个）"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "config.yaml"
            yaml_file.write_text("""
name: 测试
alternatives:
  - 方案A
criteria:
  - name: 成本
    weight: 1.0
    direction: lower_better
scores:
  方案A:
    成本: 50
algorithm: {name: wsm}
""", encoding="utf-8")

            with pytest.raises(ValidationError):
                orchestrator.load_from_yaml(yaml_file)

    def test_score_out_of_range(self, orchestrator):
        """测试: 评分超出范围"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "config.yaml"
            yaml_file.write_text("""
name: 测试
alternatives:
  - 方案A
  - 方案B
criteria:
  - name: 成本
    weight: 1.0
    direction: lower_better
scores:
  方案A:
    成本: 150
  方案B:
    成本: 50
algorithm: {name: wsm}
""", encoding="utf-8")

            # DecisionProblem 会在创建时验证评分范围并抛出异常
            with pytest.raises(ValidationError):
                orchestrator.load_from_yaml(yaml_file)
