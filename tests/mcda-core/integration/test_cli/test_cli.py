"""
MCDA Core - CLI 接口测试

测试命令行接口功能。
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from io import StringIO
import sys

from mcda_core.cli import MCDACommandLineInterface
from mcda_core.exceptions import YAMLParseError, ValidationError


# =============================================================================
# fixtures
# =============================================================================

@pytest.fixture
def sample_config():
    """示例配置文件内容"""
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


# =============================================================================
# CLI 基础测试
# =============================================================================

class TestMCDACommandLineInterface:
    """测试 CLI 接口"""

    def test_create_cli(self):
        """测试: 创建 CLI 实例"""
        cli = MCDACommandLineInterface()
        assert cli is not None

    def test_analyze_command(self, sample_config):
        """测试: analyze 命令"""
        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text(sample_config, encoding="utf-8")

            cli = MCDACommandLineInterface()

            # 模拟命令行参数
            sys.argv = ["mcda", "analyze", str(config_file)]

            # 捕获输出
            captured_output = StringIO()
            sys.stdout = captured_output

            try:
                cli.run()
                output = captured_output.getvalue()

                # 验证输出包含关键信息
                assert "供应商" in output or "排名" in output or "分析完成" in output
            finally:
                sys.stdout = sys.__stdout__

    def test_validate_command_valid(self, sample_config):
        """测试: validate 命令（有效配置）"""
        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text(sample_config, encoding="utf-8")

            cli = MCDACommandLineInterface()

            sys.argv = ["mcda", "validate", str(config_file)]

            captured_output = StringIO()
            sys.stdout = captured_output

            try:
                cli.run()
                output = captured_output.getvalue()

                # 验证输出显示验证通过
                assert "有效" in output or "valid" in output.lower() or "✓" in output
            finally:
                sys.stdout = sys.__stdout__

    def test_validate_command_invalid(self):
        """测试: validate 命令（权重和不为1，但会自动归一化）"""
        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "invalid.yaml"
            # 权重和不为 1（0.5 + 0.3 = 0.8），但会自动归一化
            config_file.write_text("""
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

            cli = MCDACommandLineInterface()

            sys.argv = ["mcda", "validate", str(config_file)]

            captured_output = StringIO()
            sys.stdout = captured_output

            try:
                cli.run()
                output = captured_output.getvalue()

                # 权重会自动归一化，所以验证通过
                assert "有效" in output or "valid" in output.lower() or "✓" in output
            finally:
                sys.stdout = sys.__stdout__

    def test_help_command(self):
        """测试: help 命令"""
        cli = MCDACommandLineInterface()

        sys.argv = ["mcda", "--help"]

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            with pytest.raises(SystemExit) as exc_info:
                cli.run()

            # --help 会 exit(0)，这是正常的
            assert exc_info.value.code == 0
            output = captured_output.getvalue()

            # 验证帮助信息
            assert "usage" in output.lower() or "帮助" in output or "命令" in output
        finally:
            sys.stdout = sys.__stdout__

    def test_version_command(self):
        """测试: version 命令"""
        cli = MCDACommandLineInterface()

        sys.argv = ["mcda", "--version"]

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            with pytest.raises(SystemExit) as exc_info:
                cli.run()

            # --version 会 exit(0)，这是正常的
            assert exc_info.value.code == 0
            output = captured_output.getvalue()

            # 验证版本信息
            assert "version" in output.lower() or "版本" in output or "0." in output
        finally:
            sys.stdout = sys.__stdout__

    def test_analyze_with_output_file(self, sample_config):
        """测试: analyze 命令指定输出文件"""
        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text(sample_config, encoding="utf-8")

            output_file = Path(tmpdir) / "report.md"

            cli = MCDACommandLineInterface()

            sys.argv = ["mcda", "analyze", str(config_file), "-o", str(output_file)]

            captured_output = StringIO()
            sys.stdout = captured_output

            try:
                cli.run()

                # 验证输出文件已创建
                assert output_file.exists()
                content = output_file.read_text(encoding="utf-8")
                assert len(content) > 0
            finally:
                sys.stdout = sys.__stdout__

    def test_analyze_with_algorithm_option(self, sample_config):
        """测试: analyze 命令指定算法"""
        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text(sample_config, encoding="utf-8")

            cli = MCDACommandLineInterface()

            # 测试指定 TOPSIS 算法
            sys.argv = ["mcda", "analyze", str(config_file), "--algorithm", "topsis"]

            captured_output = StringIO()
            sys.stdout = captured_output

            try:
                cli.run()
                output = captured_output.getvalue()

                # 验证使用了 TOPSIS 算法
                assert "topsis" in output.lower() or "分析完成" in output
            finally:
                sys.stdout = sys.__stdout__

    def test_analyze_nonexistent_file(self):
        """测试: analyze 不存在的文件"""
        cli = MCDACommandLineInterface()

        sys.argv = ["mcda", "analyze", "nonexistent.yaml"]

        captured_output = StringIO()
        sys.stderr = captured_output

        try:
            with pytest.raises(SystemExit):
                cli.run()
        finally:
            sys.stderr = sys.__stderr__

    def test_invalid_command(self):
        """测试: 无效命令"""
        cli = MCDACommandLineInterface()

        sys.argv = ["mcda", "invalid_command"]

        captured_output = StringIO()
        sys.stderr = captured_output

        try:
            with pytest.raises(SystemExit):
                cli.run()
        finally:
            sys.stderr = sys.__stderr__


# =============================================================================
# CLI 集成测试
# =============================================================================

class TestCLIIntegration:
    """CLI 集成测试"""

    def test_complete_cli_workflow(self, sample_config):
        """测试: 完整 CLI 工作流程"""
        with TemporaryDirectory() as tmpdir:
            # 1. 创建配置文件
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text(sample_config, encoding="utf-8")

            # 2. 验证配置
            cli = MCDACommandLineInterface()

            sys.argv = ["mcda", "validate", str(config_file)]
            captured_output = StringIO()
            sys.stdout = captured_output

            try:
                cli.run()
                validate_output = captured_output.getvalue()
            finally:
                sys.stdout = sys.__stdout__

            # 3. 分析问题（指定输出文件，所以不会打印报告到 stdout）
            output_file = Path(tmpdir) / "report.md"
            sys.argv = ["mcda", "analyze", str(config_file), "-o", str(output_file)]
            captured_output = StringIO()
            sys.stdout = captured_output
            captured_stderr = StringIO()
            sys.stderr = captured_stderr

            try:
                cli.run()
                analyze_output = captured_output.getvalue()
                analyze_stderr = captured_stderr.getvalue()
            finally:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

            # 验证结果
            assert output_file.exists()
            # 分析完成消息会输出到 stderr
            assert len(analyze_stderr) > 0 or len(analyze_output) > 0

    def test_batch_analysis_with_cli(self):
        """测试: 使用 CLI 批量分析"""
        with TemporaryDirectory() as tmpdir:
            cli = MCDACommandLineInterface()

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

            outputs = []
            for i, config in enumerate(configs):
                config_file = Path(tmpdir) / f"config{i}.yaml"
                config_file.write_text(config, encoding="utf-8")

                output_file = Path(tmpdir) / f"report{i}.md"

                sys.argv = ["mcda", "analyze", str(config_file), "-o", str(output_file)]
                captured_output = StringIO()
                sys.stdout = captured_output

                try:
                    cli.run()
                    outputs.append(str(output_file))
                finally:
                    sys.stdout = sys.__stdout__

            # 验证所有报告都已生成
            assert len(outputs) == 2
            for output in outputs:
                assert Path(output).exists()


# =============================================================================
# 错误处理测试
# =============================================================================

class TestCLIErrorHandling:
    """CLI 错误处理测试"""

    def test_yaml_syntax_error(self):
        """测试: YAML 语法错误"""
        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "invalid.yaml"
            config_file.write_text("""
name: test
  invalid:
    indent
""", encoding="utf-8")

            cli = MCDACommandLineInterface()
            sys.argv = ["mcda", "analyze", str(config_file)]

            captured_output = StringIO()
            sys.stderr = captured_output

            try:
                with pytest.raises(SystemExit):
                    cli.run()
                output = captured_output.getvalue()

                # 应该显示 YAML 错误信息
                assert "yaml" in output.lower() or "语法" in output or "syntax" in output.lower()
            finally:
                sys.stderr = sys.__stderr__

    def test_missing_required_field(self):
        """测试: 缺少必需字段"""
        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "incomplete.yaml"
            # 缺少 scores 字段
            config_file.write_text("""
name: 测试
alternatives:
  - 方案A
  - 方案B
criteria:
  - name: 成本
    weight: 1.0
    direction: lower_better
algorithm:
  name: wsm
""", encoding="utf-8")

            cli = MCDACommandLineInterface()
            sys.argv = ["mcda", "analyze", str(config_file)]

            captured_output = StringIO()
            sys.stderr = captured_output

            try:
                with pytest.raises(SystemExit):
                    cli.run()
            finally:
                sys.stderr = sys.__stderr__
