"""
MCDA Core - 命令行接口

提供命令行工具用于决策分析。
"""

import sys
import argparse
from pathlib import Path
from typing import Any

from .core import MCDAOrchestrator
from .exceptions import MCDAError, YAMLParseError
from .converters import ConfigConverter


# =============================================================================
# MCDACommandLineInterface - 命令行接口
# =============================================================================

class MCDACommandLineInterface:
    """MCDA 命令行接口

    支持的命令:
    - analyze: 分析决策问题
    - validate: 验证配置文件
    - convert: 转换配置格式（YAML ↔ JSON）
    - version: 显示版本信息
    - help: 显示帮助信息
    """

    def __init__(self):
        """初始化 CLI"""
        self.orchestrator = MCDAOrchestrator()
        self.converter = ConfigConverter()
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """创建命令行参数解析器"""
        parser = argparse.ArgumentParser(
            prog="mcda",
            description="MCDA Core - 多准则决策分析工具",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  mcda analyze config.yaml
  mcda analyze config.yaml -o report.md
  mcda analyze config.yaml --algorithm topsis
  mcda validate config.yaml
  mcda convert config.yaml config.json
  mcda convert config.yaml config.json --format json
  mcda --version
            """
        )

        # 添加全局选项
        parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s 0.1.0"
        )

        # 添加子命令
        subparsers = parser.add_subparsers(dest="command", help="可用命令")

        # analyze 命令
        analyze_parser = subparsers.add_parser(
            "analyze",
            help="分析决策问题"
        )
        analyze_parser.add_argument(
            "config",
            type=Path,
            help="YAML/JSON 配置文件路径"
        )
        analyze_parser.add_argument(
            "-o", "--output",
            type=Path,
            help="输出报告文件路径（默认: stdout）"
        )
        analyze_parser.add_argument(
            "-a", "--algorithm",
            help="指定算法（wsm, wpm, topsis, vikor）"
        )
        analyze_parser.add_argument(
            "-f", "--format",
            choices=["markdown", "json", "html", "pdf", "excel"],
            default="markdown",
            help="报告格式（默认: markdown）"
        )
        analyze_parser.add_argument(
            "--include-chart",
            action="store_true",
            help="包含图表（仅适用于 html/pdf 格式）"
        )
        analyze_parser.add_argument(
            "-s", "--sensitivity",
            action="store_true",
            help="运行敏感性分析"
        )
        analyze_parser.add_argument(
            "--apply-constraints",
            action="store_true",
            help="应用一票否决约束（过滤和惩罚）"
        )

        # validate 命令
        validate_parser = subparsers.add_parser(
            "validate",
            help="验证配置文件"
        )
        validate_parser.add_argument(
            "config",
            type=Path,
            help="YAML/JSON 配置文件路径"
        )

        # convert 命令
        convert_parser = subparsers.add_parser(
            "convert",
            help="转换配置格式（YAML ↔ JSON）"
        )
        convert_parser.add_argument(
            "input",
            type=Path,
            help="输入配置文件路径"
        )
        convert_parser.add_argument(
            "output",
            type=Path,
            help="输出配置文件路径"
        )
        convert_parser.add_argument(
            "-f", "--format",
            choices=["json", "yaml"],
            help="输出格式（默认: 根据输出文件扩展名自动检测）"
        )

        return parser

    def run(self, args: list[str] | None = None) -> None:
        """运行 CLI

        Args:
            args: 命令行参数（默认使用 sys.argv）
        """
        if args is None:
            args = sys.argv[1:]

        parsed_args = self.parser.parse_args(args)

        # 如果没有指定命令，显示帮助
        if parsed_args.command is None:
            self.parser.print_help()
            return

        try:
            # 执行对应命令
            if parsed_args.command == "analyze":
                self._cmd_analyze(parsed_args)
            elif parsed_args.command == "validate":
                self._cmd_validate(parsed_args)
            elif parsed_args.command == "convert":
                self._cmd_convert(parsed_args)
            else:
                self.parser.print_help()
        except MCDAError as e:
            # MCDA 错误
            print(f"错误: {e.message}", file=sys.stderr)
            if e.details:
                for key, value in e.details.items():
                    print(f"  {key}: {value}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            # 未知错误
            print(f"未知错误: {e}", file=sys.stderr)
            sys.exit(1)

    # -------------------------------------------------------------------------
    # 命令处理函数
    # -------------------------------------------------------------------------

    def _cmd_analyze(self, args: argparse.Namespace) -> None:
        """处理 analyze 命令

        Args:
            args: 解析后的命令行参数
        """
        # 加载并分析问题（自动检测格式）
        result = self.orchestrator.run_workflow(
            file_path=args.config,
            output_path=args.output,
            algorithm_name=args.algorithm,
            run_sensitivity=args.sensitivity,
            apply_constraints=args.apply_constraints,
            format=args.format,
            include_chart=args.include_chart
        )

        # 如果没有指定输出文件，打印到 stdout
        if args.output is None:
            problem = self.orchestrator.load_from_file(args.config)

            if args.format == "markdown":
                report = self.orchestrator.generate_report(
                    problem, result, format="markdown"
                )
                print(report)
            elif args.format == "json":
                report = self.orchestrator.generate_report(
                    problem, result, format="json"
                )
                print(report)

        print(f"✓ 分析完成: {args.config}", file=sys.stderr)

    def _cmd_validate(self, args: argparse.Namespace) -> None:
        """处理 validate 命令

        Args:
            args: 解析后的命令行参数
        """
        # 自动检测格式并加载问题
        problem = self.orchestrator.load_from_file(args.config)

        # 验证问题
        validation_result = self.orchestrator.validate(problem)

        # 显示验证结果
        if validation_result.is_valid:
            print(f"✓ 配置有效: {args.config}")
            if validation_result.warnings:
                print("\n警告:")
                for warning in validation_result.warnings:
                    print(f"  - {warning}")
        else:
            print(f"✗ 配置无效: {args.config}", file=sys.stderr)

            if validation_result.errors:
                print("\n错误:", file=sys.stderr)
                for error in validation_result.errors:
                    print(f"  - {error}", file=sys.stderr)

            if validation_result.warnings:
                print("\n警告:", file=sys.stderr)
                for warning in validation_result.warnings:
                    print(f"  - {warning}", file=sys.stderr)

            sys.exit(1)

    def _cmd_convert(self, args: argparse.Namespace) -> None:
        """处理 convert 命令

        Args:
            args: 解析后的命令行参数
        """
        # 执行转换
        self.converter.convert(
            input_file=args.input,
            output_file=args.output,
            output_format=args.format
        )

        print(f"✓ 转换完成: {args.input} → {args.output}", file=sys.stderr)


# =============================================================================
# 命令行入口点
# =============================================================================

def main() -> None:
    """命令行入口点"""
    cli = MCDACommandLineInterface()
    cli.run()


if __name__ == "__main__":
    main()
