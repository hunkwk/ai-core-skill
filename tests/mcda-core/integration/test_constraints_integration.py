"""
一票否决机制集成测试

测试完整的决策分析流程（包含一票否决）
"""

import pytest
from pathlib import Path
from mcda_core.cli import MCDACommandLineInterface
from mcda_core.core import MCDAOrchestrator


class TestConstraintsIntegration:
    """测试一票否决机制集成"""

    def test_orchestrator_with_constraints(self):
        """测试 MCDAOrchestrator 应用约束"""
        # 创建一个简单的 YAML 配置（包含否决规则）
        yaml_content = """
name: 供应商准入评估

alternatives:
  - 供应商A
  - 供应商B
  - 供应商C

criteria:
  - name: 资质评分
    weight: 0.6
    direction: higher_better
    veto:
      type: hard
      condition:
        operator: ">="
        value: 60
        action: reject

  - name: 财务风险
    weight: 0.4
    direction: lower_better
    veto:
      type: soft
      condition:
        operator: ">"
        value: 60
        action: warning
      penalty_score: -30

scores:
  供应商A:
    资质评分: 80
    财务风险: 50
  供应商B:
    资质评分: 40
    财务风险: 70
  供应商C:
    资质评分: 70
    财务风险: 60

algorithm:
  name: wsm
"""

        # 写入临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name

        try:
            # 创建 orchestrator
            orchestrator = MCDAOrchestrator()

            # 运行工作流（应用约束）
            result = orchestrator.run_workflow(
                file_path=temp_file,
                apply_constraints=True
            )

            # 验证结果
            assert hasattr(result, 'veto_results')
            assert result.veto_results is not None

            # 供应商B应该被拒绝（资质评分 40 < 60）
            assert result.veto_results['供应商B'].rejected is True

            # 供应商C应该有警告（财务风险 60 == 60，但 > 才触发，所以不触发）
            # 实际上 60 不大于 60，所以不触发警告
            # 让我检查一下...

            # 供应商A应该通过
            assert result.veto_results['供应商A'].rejected is False

        finally:
            # 清理临时文件
            Path(temp_file).unlink()

    def test_orchestrator_without_constraints(self):
        """测试 MCDAOrchestrator 不应用约束"""
        yaml_content = """
name: 供应商准入评估

alternatives:
  - 供应商A
  - 供应商B

criteria:
  - name: 资质评分
    weight: 1.0
    direction: higher_better
    veto:
      type: hard
      condition:
        operator: ">="
        value: 60
        action: reject

scores:
  供应商A:
    资质评分: 80
  供应商B:
    资质评分: 40

algorithm:
  name: wsm
"""

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name

        try:
            orchestrator = MCDAOrchestrator()

            # 运行工作流（不应用约束）
            result = orchestrator.run_workflow(
                file_path=temp_file,
                apply_constraints=False
            )

            # 不应该有 veto_results
            assert not hasattr(result, 'veto_results') or \
                   result.veto_results is None

            # 所有方案都应该参与排序
            assert len(result.rankings) == 2

        finally:
            Path(temp_file).unlink()
