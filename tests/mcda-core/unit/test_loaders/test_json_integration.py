"""
MCDA Core - JSON 配置集成测试

测试完整的决策流程：JSON 加载 → 验证 → 计算 → 报告生成。
确保 JSON 和 YAML 配置产生相同的结果。
"""

import pytest
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from mcda_core.core import MCDAOrchestrator
from mcda_core.models import (
    Criterion,
    DecisionProblem,
)
from mcda_core.algorithms import get_algorithm
from mcda_core.exceptions import (
    ValidationError,
    ConfigLoadError,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_json_config():
    """示例 JSON 配置数据"""
    return {
        "name": "供应商选择",
        "description": "测试 JSON 配置",
        "alternatives": ["供应商A", "供应商B", "供应商C"],
        "criteria": [
            {
                "name": "成本",
                "weight": 0.4,
                "direction": "lower_better",
                "description": "月度成本（万元）"
            },
            {
                "name": "质量",
                "weight": 0.3,
                "direction": "higher_better",
                "description": "质量评分"
            },
            {
                "name": "交付期",
                "weight": 0.2,
                "direction": "lower_better",
                "description": "交付天数"
            },
            {
                "name": "服务",
                "weight": 0.1,
                "direction": "higher_better",
                "description": "服务水平"
            }
        ],
        "scores": {
            "供应商A": {
                "成本": 50,
                "质量": 80,
                "交付期": 30,
                "服务": 70
            },
            "供应商B": {
                "成本": 70,
                "质量": 60,
                "交付期": 20,
                "服务": 80
            },
            "供应商C": {
                "成本": 60,
                "质量": 90,
                "交付期": 40,
                "服务": 60
            }
        },
        "algorithm": {
            "name": "wsm"
        }
    }


@pytest.fixture
def sample_yaml_as_json():
    """将 YAML 示例转换为 JSON 格式的配置"""
    return {
        "name": "云服务商选择",
        "alternatives": ["AWS", "Azure", "GCP"],
        "criteria": [
            {"name": "成本", "weight": 0.35, "direction": "lower_better"},
            {"name": "功能完整性", "weight": 0.30, "direction": "higher_better"},
            {"name": "易用性", "weight": 0.20, "direction": "higher_better"},
            {"name": "技术支持", "weight": 0.15, "direction": "higher_better"}
        ],
        "scores": {
            "AWS": {"成本": 3, "功能完整性": 5, "易用性": 4, "技术支持": 4},
            "Azure": {"成本": 4, "功能完整性": 4, "易用性": 4, "技术支持": 5},
            "GCP": {"成本": 5, "功能完整性": 4, "易用性": 5, "技术支持": 3}
        },
        "algorithm": {"name": "wsm"}
    }


@pytest.fixture
def orchestrator():
    """MCDAOrchestrator 实例"""
    return MCDAOrchestrator()


# =============================================================================
# JSON Loader 测试
# =============================================================================

class TestJSONLoaderIntegration:
    """测试 JSON 配置加载集成"""

    def test_load_from_json_file(self, orchestrator, sample_json_config):
        """测试: 从 JSON 文件加载决策问题"""
        with TemporaryDirectory() as tmpdir:
            # 创建 JSON 配置文件
            config_file = Path(tmpdir) / "config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(sample_json_config, f, ensure_ascii=False, indent=2)

            # 加载决策问题
            problem = orchestrator.load_from_json(config_file)

            # 验证
            assert problem is not None
            assert len(problem.alternatives) == 3
            assert len(problem.criteria) == 4
            assert problem.scores is not None

            # 验证备选方案
            assert "供应商A" in problem.alternatives
            assert "供应商B" in problem.alternatives
            assert "供应商C" in problem.alternatives

            # 验证准则
            criterion_names = {c.name for c in problem.criteria}
            assert "成本" in criterion_names
            assert "质量" in criterion_names
            assert "交付期" in criterion_names
            assert "服务" in criterion_names

            # 验证算法配置
            assert problem.algorithm is not None
            assert problem.algorithm["name"] == "wsm"

    def test_load_from_json_with_description(self, orchestrator):
        """测试: JSON 配置包含 description 字段"""
        config = {
            "name": "测试问题",
            "description": "这是一个测试决策问题",
            "alternatives": ["A", "B"],
            "criteria": [
                {"name": "成本", "weight": 0.6, "direction": "lower_better"}
            ],
            "scores": {
                "A": {"成本": 80},
                "B": {"成本": 60}
            },
            "algorithm": {"name": "wsm"}
        }

        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False)

            # 加载应该成功
            problem = orchestrator.load_from_json(config_file)
            assert problem is not None
            assert len(problem.alternatives) == 2

    def test_load_from_json_missing_field(self, orchestrator):
        """测试: JSON 配置缺少必需字段"""
        # 缺少 scores 字段
        config = {
            "name": "测试问题",
            "alternatives": ["A", "B"],
            "criteria": [
                {"name": "成本", "weight": 0.6, "direction": "lower_better"}
            ],
            "algorithm": {"name": "wsm"}
        }

        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "invalid.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False)

            # 应该抛出验证错误
            with pytest.raises(ValidationError):
                orchestrator.load_from_json(config_file)

    def test_load_from_json_invalid_direction(self, orchestrator):
        """测试: JSON 配置包含无效的 direction 值"""
        config = {
            "name": "测试问题",
            "alternatives": ["A", "B"],
            "criteria": [
                {"name": "成本", "weight": 0.6, "direction": "invalid_direction"}
            ],
            "scores": {
                "A": {"成本": 100},
                "B": {"成本": 150}
            },
            "algorithm": {"name": "wsm"}
        }

        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "invalid.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False)

            # 应该抛出验证错误
            with pytest.raises(ValidationError):
                orchestrator.load_from_json(config_file)

    def test_load_from_json_auto_normalize_weights(self, orchestrator):
        """测试: JSON 配置自动归一化权重"""
        # 权重总和不为 1
        config = {
            "name": "测试问题",
            "alternatives": ["A", "B"],
            "criteria": [
                {"name": "成本", "weight": 0.6, "direction": "lower_better"},
                {"name": "质量", "weight": 0.5, "direction": "higher_better"}
            ],
            "scores": {
                "A": {"成本": 80, "质量": 80},
                "B": {"成本": 60, "质量": 90}
            },
            "algorithm": {"name": "wsm"}
        }

        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False)

            # 加载并归一化
            problem = orchestrator.load_from_json(config_file, auto_normalize_weights=True)

            # 验证权重已归一化（总和为 1）
            total_weight = sum(c.weight for c in problem.criteria)
            assert abs(total_weight - 1.0) < 0.0001

            # 验证权重比例 (0.6/(0.6+0.5) ≈ 0.545, 0.5/(0.6+0.5) ≈ 0.455)
            cost_criterion = next(c for c in problem.criteria if c.name == "成本")
            quality_criterion = next(c for c in problem.criteria if c.name == "质量")
            expected_cost = 0.6 / (0.6 + 0.5)
            expected_quality = 0.5 / (0.6 + 0.5)
            assert abs(cost_criterion.weight - expected_cost) < 0.0001
            assert abs(quality_criterion.weight - expected_quality) < 0.0001


class TestJSONvsYAMLConsistency:
    """测试 JSON 和 YAML 配置的一致性"""

    def test_same_result_json_and_yaml(self, orchestrator, sample_yaml_as_json):
        """测试: 相同内容的 JSON 和 YAML 应产生相同的分析结果"""
        with TemporaryDirectory() as tmpdir:
            # 创建 JSON 配置文件
            json_file = Path(tmpdir) / "config.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(sample_yaml_as_json, f, ensure_ascii=False, indent=2)

            # 创建等效的 YAML 配置文件
            yaml_file = Path(tmpdir) / "config.yaml"
            yaml_content = f"""
name: {sample_yaml_as_json['name']}
alternatives:
"""
            for alt in sample_yaml_as_json['alternatives']:
                yaml_content += f"  - {alt}\n"

            yaml_content += "criteria:\n"
            for crit in sample_yaml_as_json['criteria']:
                yaml_content += f"  - name: {crit['name']}\n"
                yaml_content += f"    weight: {crit['weight']}\n"
                yaml_content += f"    direction: {crit['direction']}\n"

            yaml_content += "scores:\n"
            for alt, scores in sample_yaml_as_json['scores'].items():
                yaml_content += f"  {alt}:\n"
                for key, value in scores.items():
                    yaml_content += f"    {key}: {value}\n"

            yaml_content += f"algorithm:\n  name: {sample_yaml_as_json['algorithm']['name']}\n"

            with open(yaml_file, 'w', encoding='utf-8') as f:
                f.write(yaml_content)

            # 分别加载
            json_problem = orchestrator.load_from_json(json_file)
            yaml_problem = orchestrator.load_from_yaml(yaml_file)

            # 验证备选方案相同
            assert json_problem.alternatives == yaml_problem.alternatives

            # 验证准则数量相同
            assert len(json_problem.criteria) == len(yaml_problem.criteria)

            # 验证权重相同（归一化后）
            for j_crit, y_crit in zip(json_problem.criteria, yaml_problem.criteria):
                assert j_crit.name == y_crit.name
                assert abs(j_crit.weight - y_crit.weight) < 0.0001
                assert j_crit.direction == y_crit.direction

            # 验证评分矩阵相同
            assert len(json_problem.scores) == len(yaml_problem.scores)
            for alt in json_problem.alternatives:
                json_scores = json_problem.scores[alt]
                yaml_scores = yaml_problem.scores[alt]
                for crit_name in json_scores:
                    assert json_scores[crit_name] == yaml_scores[crit_name]

    def test_json_and_yaml_produce_same_rankings(self, orchestrator):
        """测试: JSON 和 YAML 配置应产生相同的排名结果"""
        config_data = {
            "name": "产品优先级",
            "alternatives": ["产品A", "产品B", "产品C"],
            "criteria": [
                {"name": "市场潜力", "weight": 0.4, "direction": "higher_better"},
                {"name": "开发成本", "weight": 0.3, "direction": "lower_better"},
                {"name": "技术难度", "weight": 0.2, "direction": "lower_better"},
                {"name": "战略价值", "weight": 0.1, "direction": "higher_better"}
            ],
            "scores": {
                "产品A": {"市场潜力": 90, "开发成本": 30, "技术难度": 40, "战略价值": 80},
                "产品B": {"市场潜力": 70, "开发成本": 50, "技术难度": 60, "战略价值": 70},
                "产品C": {"市场潜力": 80, "开发成本": 40, "技术难度": 50, "战略价值": 90}
            },
            "algorithm": {"name": "topsis"}
        }

        with TemporaryDirectory() as tmpdir:
            # 创建 JSON 文件
            json_file = Path(tmpdir) / "config.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False)

            # 创建 YAML 文件
            yaml_file = Path(tmpdir) / "config.yaml"
            with open(yaml_file, 'w', encoding='utf-8') as f:
                import yaml
                yaml.dump(config_data, f, allow_unicode=True)

            # 分别加载并分析
            json_problem = orchestrator.load_from_json(json_file)
            yaml_problem = orchestrator.load_from_yaml(yaml_file)

            json_result = orchestrator.analyze(json_problem)
            yaml_result = orchestrator.analyze(yaml_problem)

            # 验证排名相同
            assert len(json_result.rankings) == len(yaml_result.rankings)
            for j_rank, y_rank in zip(json_result.rankings, yaml_result.rankings):
                assert j_rank.rank == y_rank.rank
                assert j_rank.alternative == y_rank.alternative


class TestAutoFormatDetection:
    """测试自动格式检测 (load_from_file)"""

    def test_auto_detect_json_format(self, orchestrator, sample_json_config):
        """测试: 自动检测 JSON 格式"""
        with TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "config.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(sample_json_config, f, ensure_ascii=False)

            # 使用 load_from_file 应该自动识别为 JSON
            problem = orchestrator.load_from_file(json_file)

            assert problem is not None
            assert len(problem.alternatives) == 3

    def test_auto_detect_yaml_format(self, orchestrator):
        """测试: 自动检测 YAML 格式"""
        yaml_content = """
name: 测试
alternatives:
  - A
  - B
criteria:
  - name: 成本
    weight: 0.6
    direction: lower_better
scores:
  A:
    成本: 80
  B:
    成本: 60
algorithm:
  name: wsm
"""

        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "config.yaml"
            with open(yaml_file, 'w', encoding='utf-8') as f:
                f.write(yaml_content)

            # 使用 load_from_file 应该自动识别为 YAML
            problem = orchestrator.load_from_file(yaml_file)

            assert problem is not None
            assert len(problem.alternatives) == 2

    def test_unsupported_format_raises_error(self, orchestrator):
        """测试: 不支持的格式应该抛出错误"""
        with TemporaryDirectory() as tmpdir:
            xml_file = Path(tmpdir) / "config.xml"
            with open(xml_file, 'w', encoding='utf-8') as f:
                f.write("<config></config>")

            # 应该抛出 ValueError
            with pytest.raises(ValueError, match="不支持的文件格式"):
                orchestrator.load_from_file(xml_file)


class TestJSONWorkflow:
    """测试 JSON 配置的完整工作流"""

    def test_complete_workflow_with_json(self, orchestrator, sample_json_config):
        """测试: 使用 JSON 配置的完整工作流"""
        with TemporaryDirectory() as tmpdir:
            # 1. 创建配置文件
            config_file = Path(tmpdir) / "config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(sample_json_config, f, ensure_ascii=False)

            # 2. 加载配置
            problem = orchestrator.load_from_json(config_file)

            # 3. 验证
            validation_result = orchestrator.validate(problem)
            assert validation_result.is_valid

            # 4. 分析
            result = orchestrator.analyze(problem)

            # 5. 验证结果
            assert result is not None
            assert len(result.rankings) == 3
            assert result.rankings[0].rank == 1

            # 6. 生成报告
            report = orchestrator.generate_report(problem, result, format="markdown")
            assert report is not None
            assert len(report) > 0

            # 7. 生成 JSON 报告
            json_report = orchestrator.generate_report(problem, result, format="json")
            assert json_report is not None
            report_data = json.loads(json_report)
            assert "problem" in report_data
            assert "result" in report_data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
